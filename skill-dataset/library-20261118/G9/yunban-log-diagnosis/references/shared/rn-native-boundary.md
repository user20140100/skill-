# RN 与 Native 事件边界

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。当一次故障需要拼接 Android 与 React Native 日志时读取。先判方向、Bridge 方法或事件名，再按“发起 → 进入桥 → JS/Native handler → 状态/回调 → 外部结果”列节点；不能从单侧发送日志直接推断另一侧已消费。

## 四类跨界链路

| 方向 | 当前基线的入口 | 最容易误判的位置 |
| --- | --- | --- |
| JS → Native 方法 | `YunBanRNInterface` 暴露 `commModule.rnCallNative/rnCallNativeFromCallback`，按 `action` 派发 EventBus、异步 SN 回调等 | 进入方法不等于 EventBus 订阅者完成；`setMcuPowerOffAndOnV3` 先 `callback.invoke(code=200)`，后发设置事件。 |
| Native → RN 通用事件 | `NativeCallRnHelper.sendNfcId` 发 `nativeCallRn` JSON；`NativeEvent.nativeCallback` 解析 `type/params` 并触发 `CARD_EVENT` 等 | Native emit 与业务 listener 接收之间还有 JS 实例、订阅、解析和页面生命周期。 |
| Native → RN 人脸 | `FaceDetectCall.sendFaceId → NativeCallRnHelper.sendFaceEvent('nativeFaceId') → Attendance/Camera.handleFaceCallback` | `send face event:` 只是把 emit 排到 JS 队列；相机页面是否挂载、是否有考勤事件仍需验证。 |
| Native → RN IoT | `nativeCallRnIot → IotConnection.handleEvents(JSON.parse) → Event.Message callback → 业务 handler` | IoT 属性/服务回调、JPush 自定义消息各有入口，不能凭相同 payload 当作同一次投递。 |

`YunBanRNInterface.rnCallNative*` 开始时 XLog 打入参；SN 的 `sn_bridge [request]/[reply]` 分别在等待前与 `callback.invoke` 前。对于设置 MCU 计划，`code=200` 回调先于 EventBus 设置事件，不能当成 MCU 已执行。反向通路中，`sendFaceEvent` 检查 `hasActiveCatalystInstance`，有实例时记 `send face event:` 并在 JS 队列 emit，无实例记 `cannot send face event:`；即使前者出现，`Camera` 的 `nativeFaceId` listener 也只在组件挂载期间存在。NFC 的 `sendNfcId` 会捕获 Native 异常；`NfcCardReadWorkflow` 的 `rn_dispatched` 只能证明调用返回，需再查 JS 分发/业务处理。

JS `src/units/xlog/index.js` 同一次 `_log` 既调用 `console.log`，也经 `NativeModules.XLog.log → XLogModule.log` 写 Native；两个通道出现相同消息时应按时间/TAG 合并为一次打点。`NativeEvent` 的 `nativeCallRn` 与 `IotConnection` 的 `nativeCallRnIot`、`JPushConnection` 的 SDK listener 是三种不同订阅。`IotConnection` 解析/回调异常只打 JS Console `console.error`，只提供 Native XLog 时可能看不到。屏保/置顶的 JS `effectMode` 和 Android 电源/显示 Adapter 也属于不同状态层，详见[当前置顶](../domains/mode-occupation-and-current-top.md)。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| JS → Native 方法与回调 | `android/app/src/main/java/com/seewo/yunban/packages/transive/YunBanRNInterface.java#rnCallNative/#rnCallNativeFromCallback/#sendSerialCodeAsync/#setMcuPowerOffAndOnV3` |
| Native 通用/人脸事件 | `android/app/src/main/java/com/seewo/yunban/system/helper/NativeCallRnHelper.java#sendNfcId/#sendFaceEvent`、`android/app/src/main/java/com/seewo/yunban/packages/face/view/detect/FaceDetectCall.java#sendFaceId` |
| JS 订阅与业务入口 | `src/units/NativeInteraction/NativeEvent.js#nativeCallback`、`src/views/container/Attendance/InAttendance/Camera.js#handleFaceCallback` |
| IoT/JPush 两种入口 | `src/push/connections/IotPush/IotConnection.ts#handleEvents`、`src/push/connections/jPush/JPushConnection.ts#addReceiveCustomMsgListener` |
| JS 日志桥 | `src/units/xlog/index.js#_log`、`android/app/src/main/java/com/seewo/yunban/packages/logger/XLogModule.java#log` |

用事件名（`nativeCallRn`/`nativeFaceId`/`nativeCallRnIot`）、`action/type`、脱敏 UID/卡号、IoT `traceId` 和窄时间窗关联。检查 Native 与 RN 的 PID/进程和对应 APK/热更新 JS 版本；RN 事件不自动带通用请求 ID。敏感入参、SN 和人脸身份不可原样引用。

## 实际日志指纹与可证明范围

| 节点 | 搜索文本/通道 | 可确认范围 |
| --- | --- | --- |
| JS → Native SN | `sn_bridge` + `[request] RN 请求 SN` / `[reply] RN 返回 SN` | 方法进入与 Native 准备回调；JS 使用结果还需后续证据。 |
| JS → Native MCU 设置 | `YunBanRNInterface` 的 action JSON | Bridge 收到指令；`code=200` 回调先于 EventBus，不代表硬件完成。 |
| Native 人脸 emit | `NativeCallRnHelper` + `send face event:nativeFaceId` / `cannot send face event:nativeFaceId` | JS 实例活跃并排队，或因实例不活跃拒发。 |
| 考勤 RN 接收 | `RNDEBUG` + `attendance native callback:` | `Camera` handler 到达；该 `Message.log` 仅在 `Config.LOG=true` 时输出。 |
| Native NFC 调用 | `NfcCardReadWorkflow` + `rn_dispatched` / `rn_skipped` | Native 发起 RN 通知或跳过；不证明 JS 的 `CARD_EVENT` handler 已完成。 |
| IoT RN 解析异常 | JS Console 无固定前缀的 `console.error` | JS 解析或 listener 失败；需结合堆栈和 `nativeCallRnIot` 时间窗，不能仅凭错误词归因。 |

`YunBanRNInterface` 入口打点为 XLog Debug 级，日志级别可能过滤。`nativeCallRn` 的通用分发和多数 JS listener 没有固定成功日志。只有 Native XLog 而没有 JS Console 时，不能因找不到 handler 行断定未消费；只有 JS Console 时也不能倒推出平台 SDK 成功。若文本有重复的 Console/XLog 打点，先辨认同一 `_log`，避免把一条事件数两次。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| `YunBanRNInterface` 收到 action，JS 无回调 | action 分支、Native 等待或回调异常 | 具体 `action`、`sn_bridge`/EventBus 后续与 JS callback。 |
| Native `send face event`，考勤无记录 | JS 队列、页面 listener、当前考勤事件/人员匹配 | `Camera` 挂载、`attendance native callback:`、[考勤](../domains/attendance.md)匹配结果。 |
| NFC `rn_dispatched`，RN 无业务 | 通用事件解析、订阅、日志覆盖 | `nativeCallRn` payload 类型、`CARD_EVENT` listener 与 JS 异常。 |
| IoT Native 收到，JS 没处理 | `nativeCallRnIot` 发送/订阅、JSON 解析、handler 路由 | 同 traceId 的 Native emit、JS Console 与业务 handler。 |
| JS 模式已置顶，物理屏幕异常 | JS UI 状态与平台显示能力 | 当前 `effectMode`、Modal 可见性、机型 Adapter 结果。 |
