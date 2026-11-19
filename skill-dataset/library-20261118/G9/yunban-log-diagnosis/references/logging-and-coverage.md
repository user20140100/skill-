# 日志来源与覆盖

本 Skill 的输入是**已解析的可读日志文件**（如 `.log`、`.txt`）；以下源码用于解释文件覆盖和缺口，不要求解码 `.xlog`、连接设备或采集全量日志。先读 [分析契约](analysis-contract.md)，再用本页判断“未看到一行”是否有诊断价值。源码基线为 `1735b1d25cfd20528e160011abb76689beaf5bcc`。

## 先标记每份输入的来源

| 来源和源码 | 会出现的内容 | 缺失时的判断边界 |
| --- | --- | --- |
| Mars XLog：`android/app/src/main/java/com/seewo/yunban/system/capacities/logger/LoggerCapacity.java#load`、`.../system/helper/XLogImp.java`、`XLog.java` | `LoggerCapacity` 初始化 Mars 后接管 `XLog`；异步写外部目录 `Seewo/com.seewo.yunban/logs`，缓存目录 `files/xlog`，文件名前缀含进程名。Debug 开启 console sink，Release 关闭。 | 仅有 logcat 时，Release 的 XLog 业务行可能不出现；Release 初始化前 `XLog` 默认实现也会丢弃行。`LoggerCapacity` 本身没有可依赖的“初始化成功”业务行。 |
| 直接 Android Log：`sk05/.../SK05IntentNfcPlugin.java`、`sk22/.../UdiRuntime.kt`、`sk22/.../handler/DeviceHandler.kt` | 如 SK05 的 `cardId:0`、SK22 的 `[udi_init]` / `[udi_sn]` 提交行直接写 logcat。 | 这些行不自动写入 Mars；只给 XLog 文本时不能据缺失判定未执行。 |
| RN 经 Native XLog：`src/units/xlog/index.js#_log` → `android/app/src/main/java/com/seewo/yunban/packages/logger/XLogModule.java` | JS 包装器先 `console.log`，再调用 Native `XLogModule.log`；同次调用可能在 Console 和 XLog 各有一份。 | 不把跨通道重复行计为两次事件；JS 热更新版可改变日志文本或执行顺序。确认 Native 模块、RN 进程和文本来源。 |
| RN Console 与条件日志：`src/units/network/units.ts`、`src/views/widgets/message/index.tsx` | 网络辅助日志写 Console；消息组件的 `RNDEBUG` 仅在 `Config.LOG === 'true'` 时输出。部分网络日志仅打印请求选项，不含返回体。 | RN Console 不一定进入 XLog 文件；`RNDEBUG` 缺席不能证明消息组件未运行。Release HTTP BODY 日志可能不存在。 |
| Debug HTTP 拦截器：`android/app/src/main/java/com/seewo/yunban/system/helper/http/client/BpHttpClient.java`、`.../system/helper/HttpHelper.java` | `BuildConfig.DEBUG` 时接入 BODY 拦截，相关日志走其各自输出通道。 | Release 没有请求/响应 BODY 行是预期可能性；用调用方结果、错误码和服务端证据判断请求。 |
| 崩溃上报：`.../system/capacities/crash/CrashHandlerCapacity.java`、`src/units/tracer/sentry.ts` | Native Bugly 依赖非空 `BUGLY_APP_ID`；RN Sentry 只在配置环境初始化，开发环境可丢弃事件。 | XLog、logcat、Bugly、Sentry、ANR 是不同证据源；不能假设单一文本覆盖全部崩溃证据。 |
| IoT 日志快照：`.../system/helper/logging/LogFiles.java#snapshot`、`.../plugins/iot/handler/event/IotLoggerHandler.java` | 收到 `thing.service.uploadLogs` 后按请求的进程和日期生成快照，当前进程先刷盘；`LogFiles snapshot parts=..., bytes=..., deferredTailBytes=...` 记录快照情况。 | 快照可仅覆盖一个进程/日期；活动文件尾部可能延期。`parts/bytes` 不等于业务日志完整。先核对用户给的文本是否来自快照。 |

路径中 `...` 仅省略 `android/app/src/main/java/com/seewo/yunban` 等共同前缀，具体定位按表内起点搜索。

## 实际日志指纹与定位

| 搜索文本 / 来源 | 代码位置 | 只能确认什么 |
| --- | --- | --- |
| `XLog 缓存路径:`、`XLog 日志路径:` / XLog Debug | `android/app/src/main/java/com/seewo/yunban/system/helper/XLogImp.java#init` | 初始化期间尝试打印配置路径；Debug 行缺席不证明 Mars 未初始化。 |
| `SK05IntentNfcPlugin cardId:0` / 直接 Android Log | `android/app/src/main/java/com/seewo/yunban/plugins/nfc/SK05IntentNfcPlugin.java#onReceive` | 0 值广播被忽略；XLog 快照里可能没有这一行。 |
| `UdiRuntime [udi_init]`、`Sk22DeviceHandler [udi_sn] action=commit` / 直接 Android Log | `android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/UdiRuntime.kt`、`android/app/src/sk22/kotlin/com/seewo/yunban/handler/DeviceHandler.kt` | UDI 初始化请求/决议提交节点；只有 XLog 文本时不能据缺席判断它们未发生。 |
| `LogFiles snapshot parts=..., bytes=..., deferredTailBytes=...` / XLog | `android/app/src/main/java/com/seewo/yunban/system/helper/logging/LogFiles.java#snapshot` | 本地已生成所选进程/日期的快照；`deferredTailBytes` 提示活动尾块未纳入。 |
| `log cleanup bytes=...` / XLog | `android/app/src/main/java/com/seewo/yunban/system/services/AppMonitorService.java` | 清理任务的目录体积变化；不能据此推断某次业务操作发生或未发生。 |

## 文件与时间覆盖检查

1. 对每个文件记录首末时间、时区、进程名/PID、日志通道、来源说明、文件是否轮转、是否跨应用重启。时间戳可能受校时、时区或设备时钟回拨影响；跨进程先用关联键和相对顺序核对。
2. Mars 使用异步写、单文件最大约 50 MB、最大存活时间配置 7 天；`cachedays=0` 是缓存目录策略，不是历史日志完整性承诺。`LogFiles.snapshot` 优先寻找指定进程/日期的一个来源目录，可能延期活动尾块；清理还受空间阈值影响。因而“整天没日志”先检查所给文件的覆盖范围。
3. `XLog.java#cycleFace` 对高频人脸行节流；`XLog.interval` 也可限频。没看到每帧日志不能推出摄像头没有出帧。
4. 同一事件跨 XLog、RN Console、直接 Log 的时间可能接近但格式不同。用任务 ID、请求 ID、卡号脱敏键等核对；只有秒级邻近不足以合并。
5. 若只收到部分文本，报告写清楚“当前可见到哪一层”。申请补证时指定最短时间窗、进程/PID、通道、TAG/关联键和所需外部结果，不笼统索要设备全量日志。

## 缺行时的最小判断

| 输入覆盖 | 找不到目标行时先检查 | 能提出的补证 |
| --- | --- | --- |
| 只有 XLog 文本 | 目标行是否直接写 Android Log、JS Console、Debug 级或被节流；是否在 LoggerCapacity 前。 | 同时间窗的 logcat/Console 已解析片段，或目标分支的下游结果。 |
| 只有 logcat | Release 是否关闭 Mars console sink；日志是否仅写 XLog 文件。 | 用户已有的已解析 XLog 文本中目标进程/日期片段。 |
| 只有 IoT 快照导出 | 请求指定进程/日期、快照 `parts`/`deferredTailBytes`、是否跨轮转或重启。 | 缺失时间段或另一进程的已解析文本；不默认要求设备全量采集。 |
| 多通道混合 | 相同业务行是否是 RN Console 与 Native XLog 的双写；时间戳与 PID 是否可比。 | 能唯一关联操作的脱敏键和来源说明。 |

例如：只有 SK22 的 XLog 文本却找不到 `[udi_init]`，应先标注该行由 `UdiRuntime` 直接写 Android Log；只有 `UdsPowerControl [accepted]`，只能确认同步平台入口接受；只有 `NfcCardReadWorkflow` 的 RN 派发，不能推断门禁控制器动作。
