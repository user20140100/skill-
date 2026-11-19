# 考勤

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理考勤事件不显示、读卡/人脸后无记录、上报与页面不一致。入口：`src/models/attendanceModel.js`、`src/views/container/Attendance/`、`android/app/src/main/java/com/seewo/yunban/packages/attendance/AttendanceController.java`。

## 分开两条链

事件展示：`queryAttendanceEventList → 服务端事件/日期 → model 列表 → 当前有效事件 → 页面/置顶`。`queryAttendanceUserStatus` 需要非空 `eventId` 且事件存在于列表；请求异常被捕获后用空列表更新，因此“页面显示无人”不能直接证明服务端没有考勤记录。考勤置顶还受 `src/views/container/Attendance/shared/data/getInAttendanceEvents.js` 的时间窗和模式裁决约束。

外设输入：`SerialPortService 连接 → AttendanceController.onDataReceive → Gdm2mPort.getCards → status=true 才 sendCode`。可搜 `AttendanceController` 的 `USB has ... attendance device`、`cards...,status:`、`Attendance#SerialPort` 的 `serial connect`。读到卡且 `status=false` 时并未调用 `AttendanceUtils.sendCode`；Native 设备数据和 RN 业务上报必须分别确认。

刷卡链路先读 [NFC](nfc-and-access.md)；相机启动、识别和底库先读 [人脸](face-and-face-db.md)，识别后的考勤记录与上报按下文追；当前考勤抢占屏幕读 [当前置顶](mode-occupation-and-current-top.md)。报告按 `eventId`、人员脱敏 ID 和发生日关联，防止相邻考勤事件串案。

## 人脸考勤记录与上报链路

`InAttendance` 只有 `hasFacePermission` 为真且有当前考勤事件时才渲染 `Camera`。`FaceDetectCall.sendFaceId` 排除无效用户、已发送的 track 和重复 UID 后，发 `nativeFaceId`；这条 Native 事件也可能来自其他人脸页面，必须确认考勤 `Camera` 当时已挂载。`Camera.handleFaceCallback` 只接受非空 `list`，把 UID 集合传给 `attendance.record('face')`。`record` 要求 `getInAttendanceEvents()` 产生当前事件，否则打印 `no attendance events, return` 后结束。

`FaceRecorder.apply` 按每个当前事件匹配人员：课程考勤或自定义人员事件考勤匹配考勤用户列表；按班级的事件考勤匹配班级学生。`BaseMultiRecorder.removeCachedItems` 用 `userUid + eventId + attendanceDate` 排除本地已有记录。只有新记录非空才 `dispatch` 到 `attendanceResult`、触发 `onrecord` 页面动画，并尝试异步 `FaceIdCtrl.take(true)` 拍照；拍照成功才写入 `attendanceImages`。因此 Native 已识别、RN 已收到回调、生成新记录、页面提示和服务端收录是不同节点；重复人脸也可能止于本地去重。

结果上报：`HomePage` 挂载的 `attendance.handleTimer` 每秒调用 `ReportService.run`。`reportResult` 约 15 秒一轮，从 `attendanceResult` 取上次成功后新增的记录，经 `reportAttendanceResult` POST `/api/attendance/v1/{schoolUid}/data`。接口请求经过网络层 HTTP 与业务 `statusCode === 200` 校验；成功后推进已上报数量，非考勤时段可清掉已报本地结果。失败时不推进，下轮重试。推送同步的记录只供本地展示，不二次回传。`FaceRecorder` 写入 `attendanceResult` 和 `EventChannel.publish('onrecord')` 都不是后台成功的凭据。

图片上报另走一路：`takeImage` 成功才产生 `diskPath`。`reportImages` 约 37 秒一轮，最多从未上传图片中取最新 20 条、按本地路径去重，经 `FileUpload.uploadImageFileWithMetadata(true)` 获得 `picUrl`，再 POST `/api/attendance/v1/{schoolUid}/images`。后台响应的 `failList` 对应图片继续留在本地，其余从本地队列移除；本地文件不存在的 `'404'` 会被清理。图片上传失败或未拍到照片，不等于 `/data` 考勤结果上报失败。

图片后台上报成功后，`reportToApplication` 才为有学号或手机号的用户调用 `AttendanceTrain.record`；转发还依赖小应用考勤开关及回调 URL，`DelayReporter` 异步 POST。小应用转发结果与考勤主服务 `/data`、`/images` 要分别判断，不能用页面动画或其中一路成功替代另外两路。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 事件和人员状态 | `src/models/attendanceModel.js#queryAttendanceEventList/#queryAttendanceUserStatus` |
| 时间窗与导航 | `src/views/container/Attendance/shared/data/getInAttendanceEvents.js#getInAttendanceEvents` |
| 串口接入/状态门槛 | `android/app/src/main/java/com/seewo/yunban/packages/attendance/SerialPortService.java`、`android/app/src/main/java/com/seewo/yunban/packages/attendance/AttendanceController.java#onDataReceive` |
| 课程联动 | `src/models/scheduleModel.ts#setCourseAttendanceList` |
| 人脸回传与监听 | `android/app/src/main/java/com/seewo/yunban/packages/face/view/detect/FaceDetectCall.java#sendFaceId`、`src/views/container/Attendance/InAttendance/Camera.js#handleFaceCallback` |
| 匹配、去重、记录、拍照 | `src/views/container/Attendance/shared/RecorderFactory/FaceRecorder.js#apply/#dispatch`、`BaseMultiRecorder.js#removeCachedItems`、`BaseRecorder.js#takeImage` |
| 结果与图片上报 | `src/views/container/Attendance/shared/ReportService/reportResult.js#reportData`、`reportImages.js#reportData`、`src/services/attendance.js#reportAttendanceResult/#reportAttendanceImages` |
| 小应用转发 | `src/units/appThroughTrain/AttendanceTrain/index.ts#record`、`DelayReporter.ts#send` |

用 `eventId`、`attendanceType`、`attendanceDate`、学校/场室 ID、脱敏人员或卡号关联。人脸图片本地移除键是 `userUid#eventId#attendanceDate`；同一识别可落入多个重叠事件，按键逐条核对。一次事件可能包含多个班级和用户；课程的 `lessonId` 只用于课程考勤映射，不能代替 `eventId`。串口原始卡片数据与 RN 事件没有统一任务 ID，连续刷卡时只能结合格式和窄时间窗。

## 事件、状态与硬件分开

`queryAttendanceEventList` 获取事件后计算 `isEnd`，合并用户列表；未结束事件才逐个查询用户状态，再更新 model 和课程考勤映射。单个 `queryAttendanceUserStatus` 需要已有事件列表、非空 `eventId` 且在列表中，否则直接返回；请求失败时以空状态列表继续。事件列表总请求失败时会保留原事件，并对跨日期旧状态清空。因此“页面缺一个人”可能是状态请求失败/过滤，不等于服务端未生成事件。

`getInAttendanceEvents` 按当前时间筛选、决定是否可置顶、计算迟到/超时区间，必要时导航考勤页。串口链则是 `设备识别 → 串口连接 → onDataReceive → Gdm2mPort.getCards → status=true → AttendanceUtils.sendCode`。`status=false` 时可看到卡数据但不发送。NFC/人脸识别并非此串口入口，需分别追业务监听和上报接口。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 串口设备 | `USB has attendance device` / `USB has no attendance device, try serial port connect` | 设备检测分叉。 |
| 串口连接 | `Attendance#SerialPort` + `serial connect succeed/failed` | 打开串口的结果，不证明收到有效卡。 |
| 卡解析与门槛 | `AttendanceController` + `,status:` | 已解析到非空卡集合和发送开关状态；`status:false` 不转发。 |
| 考勤页面导航 | `AttendanceEvents` + `will navigate to attendance with key:` / `already navigate` / `in face time, not navigateToAttendance` | 时间窗和页面抢占的分支。 |
| 事件查询异常 | `attendanceModel` 的 `console.error(e)` | 仅有 JS Console 时可见；需结合 URL 判别。 |
| Native 人脸回传 | `Face#FaceDetectCall` + `[FaceDetectCall][sendFaceId] 识别人脸成功，回传 RN 进行打卡` | Native 发出 `nativeFaceId` 前；仍需核对考勤页面监听。 |
| RN 人脸输入和候选记录 | `RNDEBUG` + `attendance native callback:` / `attendance report face:` / `record attendance items:` | 分别是 RN 收到、进入匹配、去重后的候选；都不能证明已上报。 |
| 人员匹配分支 | `RNDEBUG` + `handleCustomUserSign` / `handleEventSign` | 进入自定义用户或班级事件匹配分支；仍需查看新增记录是否非空。 |
| 无当前事件 | `RNDEBUG` + `no attendance events, return` | 人脸或其他方式到达 `record`，但没有当前考勤事件。 |
| 结果接口请求 | `RNDEBUG` + `attendance report data:`；JS Console `/api/attendance/v1/` + `/data` 或 `请求失败` | 前者在请求成功或失败之后都会打印请求体，不能单独证明成功；需核对同请求的业务响应或服务端记录。 |
| 图片上传及异常 | JS Console `reportImages`；`AttendanceReportService` + `upload attendance face error:` / `clear urls who not in dish path:` | 上传尝试、异常、文件缺失清理；`reportImages` 不代表上传或 `/images` 成功。 |
| 小应用转发 | `AttendanceTrain` + `未开启考勤转发事件`；`DelayReporter` + `report attendance events to the third party` | 转发开关与请求尝试；还需回调响应判定结果。 |

`RNDEBUG` 这些 `Message.log` 仅在 `Config.LOG === 'true'` 时输出；缺行要先核对构建配置和日志覆盖。`/data`、`/images` 成功没有固定的专属 XLog 成功文本；网络层 `log` 是 JS Console，`/images` 的响应体也不由它打印。`queryAttendanceEventList` 是 effect 名称，不是保证落盘的日志。若用户声称“考勤已上报”，还要找对应接口的业务响应或后端记录；串口 `sendCode` 和页面状态均不能单独证明上报成功。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 有事件列表但无当前事件 | 日期、开始/结束/迟到窗口过滤 | 原始事件时间、设备时钟、`getInAttendanceEvents` 结果。 |
| 当前事件有，人员显示空 | 用户列表合并或状态请求 | `eventId`、状态接口响应、班级范围。 |
| 串口连上但无卡 | 驱动读取/协议解码 | 原始字节、串口错误、设备现场。 |
| 见卡且 `status:false` | Controller 门槛关闭 | 状态设置调用及当时业务模式。 |
| 已转 RN 但页面/后端无记录 | 监听、人员匹配或接口 | RN 接收、对应事件/人员、网络业务码。 |
| Native 发了 `nativeFaceId`，无 RN 回调 | 页面 `Camera` 挂载、监听时机和 JS 日志开关 | `hasFacePermission`、当前页面、`Config.LOG` 与 RN Console 覆盖。 |
| RN 收到回调，无新增候选记录 | 当前事件、人员范围、本地同日去重 | `inAttendanceEvents`、事件人员/班级、`attendanceResult` 对应键。 |
| 已生成本地结果，后台无记录 | `/data` 调用、HTTP/业务响应、约 15 秒定时器 | 同键的网络响应和服务端入库查询；`attendance report data:` 不能当回执。 |
| `/data` 成功，图片缺失 | `FaceIdCtrl.take`、文件上传、`/images` 及 `failList` | 本地 `diskPath/picUrl` 状态、上传结果和图片接口响应。 |
| `/images` 成功，小应用未收到 | 学号/手机号、转发开关、URL、异步回调 | `AttendanceTrain`/`DelayReporter` 日志及第三方响应。 |
