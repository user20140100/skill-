# 考勤与签到

## 边界

本手册覆盖刷卡、人脸和二维码相关的考勤与课程签到，包含人脸图片上传、考勤本地记录、批量上报，以及考勤成功后的可选开门联动。代码事实基于 ab680809。

人脸识别算法是否正确识别、二维码网页侧提交和服务端最终落库不由本手册单独证明。涉及相机或人脸库时同时读取 [人脸认证](face-authentication.md)。

## 代码定位与关联键

下列源码路径均相对 app/src/main/java/com/seewo/yunban。

| 目的 | 路径与关键符号 |
| --- | --- |
| 考勤入口与人脸图片 | ui/attendance/AttendanceViewModel.kt：onFaceDetected、nfcAttendance、faceAttendance |
| 考勤本地状态与批量上报 | data/remote/attendance/AttendanceRepositoryImpl.kt：markUserAttendance、startReporting、handlerReport |
| 考勤本地存储与接口 | data/local/store/attendance/AttendanceLocalStore.kt、data/remote/api/IAttendanceApi.kt |
| 考勤成功后的联动 | usecase/attendance/AttendanceExtensionUseCase.kt |
| 签到入口与人脸图片 | ui/sign/SignViewModel.kt：nfcSignIn、onFaceDetected |
| 签到请求与接口 | data/remote/sign/SignRepositoryImpl.kt、data/remote/api/ISignApi.kt |

| 场景 | 最强关联键 | 不能替代它的键 |
| --- | --- | --- |
| 考勤本地记录与上报 | ruleRecordKey、ruleId、userUid、attendanceTime | 单个批量 records 成功日志不能单独确认某个用户 |
| 考勤页面内判断 | attendanceId 与本地用户 id | attendanceId 不在最终 HTTP record 中，需结合 ruleRecordKey |
| 人脸签到 | orderId、userUid、snCode | facePicFileKey 是可空图片证据，不是签到请求的唯一键 |
| NFC 签到 | orderId、脱敏 cardNumber、snCode | 卡号不可与人脸 userUid 混用 |
| 二维码 | ruleRecordKey、ruleId、roomUid 与时间戳 | 二维码网页后的提交不在当前客户端日志范围 |

## 考勤链路

    NFC 卡 / 已识别的人脸
      -> AttendanceViewModel 过滤当前考勤用户与重复状态
      -> 人脸路径：生成本地图片，上传临时 CStore 文件
      -> AttendanceRepositoryImpl.markUserAttendance
      -> 先触发 AttendanceExtensionUseCase 回调
      -> 写本地考勤记录并更新界面
      -> 每 3 秒读取待上报记录
      -> POST /nebula/attendance/v1/report
      -> 业务成功后 markUserReported

人脸考勤图片上传失败、文件创建失败时，当前代码仍会以空 fileKey 调用 markUserAttendance。因此界面出现考勤成功或本地 attendanceTime 已更新，均不代表图片上传成功或后台上报成功。

markUserAttendance 会先通知扩展回调，再写本地记录。配置开启时扩展可发起开门、账号登录或课程模式；该开门是独立门禁链路，不能用考勤 HTTP 的成功替代其结果。

## 签到链路

    NFC 卡 / 已识别的人脸
      -> SignViewModel 校验当前课次、needSign、signed
      -> 人脸路径：生成本地图片并上传临时 CStore 文件
      -> POST /room/order/v1/room/order/card/sign 或 /face/sign
      -> SignRepositoryImpl 发射结果
      -> SignViewModel 更新 signState 与提示

人脸签到即使图片上传失败，也会带空 facePicFileKey 调用人脸签到接口。签到没有本地 Outbox；如果请求失败，只会记录 SignRepositoryImpl 的 signIn error，当前代码没有像考勤那样的客户端重试队列。

## 日志指纹与关联键

| 场景 | 搜索文本或 TAG | 关联键 |
| --- | --- | --- |
| 人脸考勤入口 | AttendanceViewModel + FaceUser / attendance checking | 脱敏 userId、考勤 event id |
| NFC 考勤 | nfcAttendance cardId / attendance, cardId | 脱敏卡号、userUid、attendanceId |
| 考勤图片 | checkFace create temp image / save image file fail / upload image | userUid、时间窗、fileKey 脱敏值 |
| 考勤上报完成 | AttendanceRepositoryImpl + reportAttendanceRecord success | records 中的 ruleRecordKey、ruleId、userUid |
| 考勤上报失败 | reportAttendanceRecord error | 业务码、ruleRecordKey、时间窗 |
| 签到前置拒绝 | SignViewModel + currentSchedule | orderId、needSign、signed |
| 签到失败 | SignRepositoryImpl + signIn error | orderId、脱敏用户或卡号、业务码 |

不要在报告中原样输出人脸图路径、fileKey、卡号或 userUid。

## 断点判断

| 最晚可见节点 | 判断 | 下一步 |
| --- | --- | --- |
| 识别回调后提示无需考勤或重复 | 当前事件或本地用户筛选拒绝了该次打卡 | 查本地考勤事件、用户列表、attendanceTime |
| 本地考勤成功，无 report success | 本地已记账，后台确认尚未得到证据 | 查 3 秒轮询、待上报记录与 report error |
| report error | 后台上报未成功确认，记录应保持待上报 | 查网络、业务码和下一轮请求；不要重复人工补记 |
| report success，后台查询无记录 | 客户端已确认上报 | 转后端按 ruleRecordKey、userUid、时间查数据 |
| CStore 失败后考勤或签到接口成功 | 图片证据缺失，但业务接口仍可能成功 | 将图片与考勤或签到结果分别报告 |
| 签到接口失败 | 当前客户端无本地重试队列 | 查接口错误、网络和用户是否重试触发 |

考勤上报使用批量 records；同一个日志窗口可能包含多名用户。必须先按 ruleRecordKey、ruleId、userUid 和时间拆分，不能把整批成功推断为某一用户已成功。
