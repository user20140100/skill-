# 人脸识别与底库

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理摄像头打不开、识别失败、人脸库未更新、补光异常。入口：`android/app/src/main/java/com/seewo/yunban/packages/face/FaceController.java`、`android/app/src/main/java/com/seewo/yunban/packages/face/service/UserService.java`、`src/models/faceDBModel.ts`、`android/app/src/main/java/com/seewo/yunban/packages/face/rn/data/FaceDataModule.kt`。

## 排查链

识别：`相机可用 → FaceController.start/处理线程 → 帧输入/SDK 识别 → 用户匹配 → RN/考勤等下游`。可搜 `Face#FaceController` 的 `[FaceController][start]`、`FaceView 为空`、`未找到可用摄像头`、`处理线程不为空`，分别确认启动条件；`start` 日志不证明已经匹配到用户。

底库：`faceDBModel.queryFaceDBEnable/queryClassFaceDB → RN 状态` 与 `updateFaceData → FaceDataModule.updateFaceData → Native 底库/SDK` 是不同链路。`queryClassFaceDB` 取得列表并提交到 model，不等于 Native 识别库更新；`updateFaceData` 仅在服务端 `active.data` 为真时调 Native。匹配 Native 存储可查 `android/app/src/main/java/com/seewo/yunban/packages/face/service/ym/FaceUserDBHelper.java`。

SK06 补光经 UDS/OpenSDK，SK22 在此基线 `faceFillLightControl` 返回 `NOT_CONFIGURED`；详见平台文档。不要在报告中放人脸图片、特征或人员标识。若识别后考勤缺失，继续读[人脸考勤记录与上报链路](attendance.md#人脸考勤记录与上报链路)。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 相机/线程生命周期 | `android/app/src/main/java/com/seewo/yunban/packages/face/FaceController.java#start/#stop/#track` |
| SDK 人脸映射 | `android/app/src/main/java/com/seewo/yunban/packages/face/service/UserService.java#findFaceUserList`、`android/app/src/main/java/com/seewo/yunban/packages/face/service/ym/YMUserService.java` |
| RN 底库状态 | `src/models/faceDBModel.ts#queryFaceDBEnable/#queryClassFaceDB/#updateFaceData` |
| Native 数据刷新 | `android/app/src/main/java/com/seewo/yunban/packages/face/rn/data/FaceDataModule.kt#updateFaceData` |
| 本地数据库 | `android/app/src/main/java/com/seewo/yunban/packages/face/service/ym/FaceUserDBHelper.java` |

底库查询用 `schoolUid/classUid`、人员脱敏 ID、一次刷新时间窗；识别用相机启动会话、trackId/脱敏用户和时间。trackId 是一次跟踪上下文，不是跨重启的全局事件 ID。`queryClassFaceDB` 返回列表和 Native 底库数据不能只按数量相等判定同一版本。

## 识别与同步的分叉

`FaceController.start` 先判断 DetectView、摄像头权限/可用性、处理线程，再启动 HandlerThread，约 500 ms 后执行处理任务。`track` 调 UserService 获取匹配用户。`start` 或相机预览成功，只到“识别入口”，尚未证明 SDK 产出 FaceUser。停止时还会关闭补光；补光失败与算法识别应分开。

`faceDBModel.queryFaceDBEnable` 仅更新 RN `enable`；`queryClassFaceDB` 仅更新 RN `classFaceData`。`updateFaceData` 先查当前设备算法是否激活，`active.data` 为真才调 Native；Native `FaceDataModule` 的日志出现在调用 `faceService.dataRefresh` 前，实际下载、写入数据库和可识别用户还要追 Native 服务。`isYMFaceAlgorithmActivated` 仅检查 DB 文件存在，不能当成内容完整。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 启动前置 | `[FaceController][start] 触发启动`、`FaceView 为空`、`未找到可用摄像头`、`处理线程不为空` | 调用和具体拒绝条件。 |
| 线程启动/结束 | `[FaceController][start] HandlerThread 开始启动`、`[FaceController][end]` | 相机处理生命周期，不是识别结果。 |
| 识别输入 | `[YMUserService][findList] 当前帧画面识别不到人脸/识别到多个人脸` | 对应帧的 SDK 人脸数量分支。 |
| RN 激活状态 | JS Console `afu` | 设备算法激活查询结果；含 SN，报告脱敏。 |
| Native 刷库 | `FaceDataModule updateFaceData:` | 调用 `dataRefresh` 前的入口；需续查写库结果。 |
| 本地重置 | `[FaceController][resetData] 人脸识别库重置` | 重置被触发，不证明重建已完成。 |

`[YMUserService][findList]` 由 `XLog.cycleFace` 写入，受周期日志门槛影响；同一时间窗没有逐帧日志不能推断相机没有送帧。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 启动被前置条件拒绝 | View、权限或线程状态 | 相机权限、组件生命周期、已有线程销毁日志。 |
| 相机已启动但无用户 | 帧输入、SDK 跟踪与本地映射 | SDK/`UserService` 日志、相机画面与底库状态。 |
| RN 班级底库有数据但 Native 未更新 | 激活状态与 Bridge 调用 | `afu`、`FaceDataModule`、数据刷新日志。 |
| Native 进入 `dataRefresh` 但用户不可识别 | 下载/写库/算法层 | 人脸服务错误、DB 记录或 SDK 日志。 |
| 已识别用户但无业务结果 | 考勤/通话/页面监听者 | 当前页面、[人脸考勤记录与上报链路](attendance.md#人脸考勤记录与上报链路)的事件与人员条件。 |
