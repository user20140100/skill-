# 家校电话、音视频与语音

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理外接电话无响应、音视频来电未显示、录音或语音播放失败。入口：`android/app/src/main/java/com/seewo/yunban/packages/phone/PhoneController.java`、`android/app/src/main/java/com/seewo/yunban/packages/phone/service/PortService.java`、`src/models/faceTimeModel.ts`、`android/app/src/main/java/com/seewo/yunban/packages/voice/recorder/RecorderController.java`。

外接电话：`USB 设备 → PortService 串口连接 → PhoneController 发送 AT 指令 → PhoneService.callback 解码 → RN 事件/业务状态`。`PhoneId#Controller` 的 `USB has no phone device` 与直接 `android.util.Log` 的 `send data:`/`send error:` 属不同日志通道；`send` 返回只反映串口发送，通话接通还需设备回调。日志可能含电话号码或 AT 指令，报告必须脱敏。

音视频通话：`faceTimeModel.ts#postCallingRecord` 先请求上报，成功后才 `doSaveCallingRecord`；`updateTag` 与 `cancelRoomId` 驱动本地状态，记录上报成功不等于媒体会话建立。`RecorderController` 的 `start: init minBuffer` 与 `stop` 只标记录制流程，文件可用和后续上传另查。

若通话界面被其他模式抢占，读 [当前置顶](mode-occupation-and-current-top.md)；语音文件上传失败读 [文件传输](network-and-file-transfer.md)。

## 代码定位与关联键

| 路径 | 源码与符号 |
| --- | --- |
| 电话硬件入口 | `android/app/src/main/java/com/seewo/yunban/packages/phone/PhoneController.java#call/#receive` |
| 串口及 RN 事件 | `android/app/src/main/java/com/seewo/yunban/packages/phone/service/PortService.java#connect/#send`、`android/app/src/main/java/com/seewo/yunban/packages/phone/utils/PhoneUtils.java#sendCode` |
| 音视频记录状态 | `src/models/faceTimeModel.ts#postCallingRecord/#doSaveCallingRecord/#doCancel`、`src/services/faceTime.ts` |
| 录音 | `android/app/src/main/java/com/seewo/yunban/packages/voice/recorder/RecorderController.java#start/#stop` |

电话用脱敏号码、AT 指令类型、串口连接会话、设备回传 `PhoneCode` 和窄时间窗关联；音视频用 `callRoomId`、通话角色及业务记录 ID。`callRoomId` 不会自动贯穿外接串口电话。录音文件 ID/路径需单独跟踪，不能拿拨号成功匹配一次上传。

## 三条链及异步边界

外接电话：`USB 检测 → PortService.connect → PhoneController.call → ATD 发送 → 串口读线程 → PhoneService.callback → PhoneUtils.sendCode(nativePhoneId) → JS`。`call` 会给号码补分号；返回值只反映 AT 指令是否被送出。`PhoneUtils.sendCode` 仅在 context 为 ReactContext 时发事件，直接 `Log.i("PhoneId", "react send code:")` 在 emit 前，不能证明 JS 已处理。

音视频：`postFaceTimeRecord` 先带设备 SN/学校 ID 请求接口，成功后才 `doSaveCallingRecord` 更新 RN 本地记录；`doUpdateTag`、`doCancel` 控制页面刷新和取消房间。记录接口成功与媒体连接、接听、通话质量要分开。录音的 `start: init minBuffer` 是缓冲区初始化，`bytesEncoded` 与 `stop` 是录制过程，文件存在及上传仍需另查。

## 实际日志指纹

| 节点 | 搜索文本与通道 | 可确认范围 |
| --- | --- | --- |
| 无电话设备 | XLog `PhoneId#Controller USB has no phone device` | 设备检测未命中；仍可能是串口/USB 枚举问题。 |
| 串口连接 | logcat `PhoneId#SerialPort` + `connect serial port` / `Phone serial connect succeed:` / `can't connect` | 打开串口的分支。 |
| 拨号与下行 | logcat `PhoneId#Controller send data:`、`send error:` | AT 写入尝试或异常；包含号码，报告脱敏。 |
| 回传 RN | logcat `PhoneId react send code:` | Native 将解码事件交给 RN 发射前。 |
| 录音 | XLog `RecorderController start: init minBuffer:` / `bytesEncoded:` / `stop` | 录音启动、写入及停止阶段。 |
| 音视频记录 | `postFaceTimeRecord` 对应请求 URL 的 JS Console/HTTP | 记录接口结果；model 没有专用固定 XLog。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 无 USB/串口 | 外设检测、权限或设备接线 | USB 枚举、端口路径、权限。 |
| 串口已连，`send error` | 写入协议或端口关闭 | AT 类型、异常、同时间窗读线程。 |
| `send data` 后无回传 | 外设/网络通话状态或读线程 | 原始脱敏回传、PhoneService 解码状态。 |
| `react send code` 后页面未变 | RN listener 或模式置顶 | `nativePhoneId` 订阅、[当前置顶](mode-occupation-and-current-top.md)。 |
| 通话记录已上报却未接通 | 媒体会话与记录分离 | 媒体 SDK 连接/接听回调、房间 ID。 |
