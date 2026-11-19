# IoT、JPush 与远程命令

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理设备不上线、远程命令丢失、推送到了却业务不更新。入口：`android/app/src/main/java/com/seewo/yunban/system/helper/IotClientDepository.kt`、`src/push/connections/IotPush/IotConnection.ts`、`src/push/connections/jPush/JPushConnection.ts`、`src/push/handlers/index.js`。

## 排查链

IoT Native：`连接配置/SN → 注册 → MQTT 连接 → topic/method/traceId 回调 → Native handler 或 RN 事件 → 业务 handler → 本地结果/上报`。`IotClientDepository` 的 `provideIotClient: required runtime state is unavailable` 是前置状态不足；`register success`、`connectAsync success`、`>>> handle callback` 是不同阶段。RN `IotConnection` 监听 `nativeCallRnIot` 并解析/转发；JPush 有独立连接和处理入口。

用 `method`、`traceId` 和业务 ID 优先关联，区分“连接成功”“收到指令”“handler 执行”“业务状态更新”“回执送达”。`src/push/handlers/index.js` 只是路由注册，目标业务 handler 需按 method 再查；无某 handler 日志也可能是 Console 未入输入。IoT 配置指令在 `IotConfigsHandler.java`，屏保指令在 `src/push/handlers/protectionScreenPush.js`。

设备身份前置读 [启动](startup-and-device-identity.md)，JS/Native 事件拼接读 [桥接](../shared/rn-native-boundary.md)。不要把一次 `postEvent=true` 表述为服务端已处理。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 注册与 MQTT 连接 | `android/app/src/main/java/com/seewo/yunban/system/helper/IotClientDepository.kt#register/#connectToIot` |
| Native 服务/属性回调 | `android/app/src/main/java/com/seewo/yunban/system/helper/IotClientDepository.kt#addEventCallBack/#handleCommand` |
| RN IoT 事件 | `src/push/connections/IotPush/IotConnection.ts` |
| JPush 事件与 ID | `src/push/connections/jPush/JPushConnection.ts` |
| 业务分发 | `src/push/handlers/index.js`、`android/app/src/main/java/com/seewo/yunban/plugins/iot/handler/event/IotConfigsHandler.java` |

`traceId` 与 `topic/method` 是 Native IoT 回调强键；进入 RN 后还要确认对应载荷确实传递了这些字段。JPush 的 registrationID 仅标识推送注册，不能代替 IoT traceId。业务 `eventId` 若在 handler 内重新生成，也不能当成原指令 ID。按设备、连接会话、方法和同一次指令的时间窗分段。

## 连接、指令和回执分开

`provideIotClient` 可能因 SN/配置等运行状态不足返回 null。`register()` 成功只完成设备注册；`initMqtt`、`connectAsync` 及 SSL 状态 callback 才构成连接结果。连接重试与清理可取消未完成任务。MQTT service callback 交给 `iotConnectEventListener.handleCommand`，property get/set 则走本类 `handleCommand`，其 `TslResponse.SUCCEED` 是当前客户端回调返回，并不证明目标业务已执行。

RN `IotConnection` 监听 `nativeCallRnIot`，解析并分发给业务 handler；JPush 是另一入口。若日志有“Native 收到”但无业务变化，先确认方法路由和 RN 事件覆盖，再进目标领域。配置 `thing.service.configUpload` 在 Native 转 EventBus；屏保、解绑、节目等 JS handler 也各有自己的前置条件。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 前置不足 | `provideIotClient: required runtime state is unavailable` | 本次未提供可用客户端。 |
| 注册 | `register begin` / `register success` / `register failed` | 注册请求及同步结果；尚非 MQTT 已连接。 |
| 连接 | `initMqtt fail` / `connectAsync success` / `connectAsync error res =` / `isConnected =` | MQTT 初始化、异步连接结果和 SSL callback。 |
| 命令到 Native | `>>> handle callback: topic=...,method=...,traceId=...` | property get/set 入口被调用；service callback 要看其 listener 路径。 |
| 配置转发 | `IotConfigsHandler` 参数日志 | `configUpload` 到达并转 EventBus，不证明配置应用。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 无注册 | 身份/配置/网络前置 | SN、broker、环境和 `provideIotClient` 状态。 |
| 注册成功但连接失败 | MQTT 初始化或 SSL/网络 | callbackCode、TLS/系统网络日志。 |
| 已连接但未见指令 | 订阅、服务端投递或日志覆盖 | topic/method、traceId、服务端下发记录。 |
| Native 收到但 RN 未处理 | Bridge 或 handler 路由 | `nativeCallRnIot`、method 注册与 JS 异常。 |
| handler 已执行但业务未更新 | 对应领域的状态/请求 | 目标 model、回执及最终效果。 |
