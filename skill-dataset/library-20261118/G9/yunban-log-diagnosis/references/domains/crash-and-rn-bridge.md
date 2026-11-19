# 崩溃、ANR 与 RN 桥接

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理进程重启、页面错误、ANR、Native→RN 调用失败。入口：`android/app/src/main/java/com/seewo/yunban/system/capacities/crash/CrashHandlerCapacity.java`、`android/app/src/main/java/com/seewo/yunban/system/capacities/crash/uncaught/AppUncaughtExceptionHandler.java`、`src/index.js`、`src/views/widgets/ErrorBoundary/HocPageErrorCatch.tsx`、`android/app/src/main/java/com/seewo/yunban/packages/transive/YunBanRNInterface.java`。

## 分层定位

- Native：`AppUncaughtExceptionHandler` 打 `AppUncaughtException`；部分 `java.util.concurrent`、`java.lang` 类型只记录并返回，其他异常在启动 15 秒后可调用 `AppUtils.relaunchApp(true)`。若见新 PID，核对异常时间与重启时间，不把每次新 PID 都归于这个 handler。Bugly 是另一崩溃证据源。
- RN 全局：`src/index.js` 的 `globalErrorHandler` 走 Console、`postNativeError` 与 `XLog.e`；页面边界用 `PageErrorBoundary` 上报并显示错误页面。Sentry 事件与本地文本可能不同时可见。
- 桥接：`YunBanRNInterface.java` 有 Native 调 RN 的异常上报；设备事件、JS 订阅、业务处理和渲染仍应分开。只有 Native `emit` 不能证明 JS listener 执行。

ANR 需线程栈/系统证据；若只给应用文本，只能列出最后可见业务节点和阻塞假设，不能从时间空白直接宣称 ANR 根因。跨进程和生命周期细节见 [异步](../shared/async-and-lifecycle.md)、[RN/Native](../shared/rn-native-boundary.md)。

## 代码定位与关联键

| 层 | 源码与符号 |
| --- | --- |
| Native 捕获与 Bugly | `android/app/src/main/java/com/seewo/yunban/system/capacities/crash/CrashHandlerCapacity.java`、`android/app/src/main/java/com/seewo/yunban/system/capacities/crash/uncaught/AppUncaughtExceptionHandler.java#uncaughtException` |
| RN 全局 | `src/index.js#globalErrorHandler`、`src/units/tracer/pushError` |
| 页面边界 | `src/views/widgets/ErrorBoundary/HocPageErrorCatch.tsx#componentDidCatch` |
| RN→Native 请求 | `android/app/src/main/java/com/seewo/yunban/packages/transive/YunBanRNInterface.java#rnCallNative/#rnCallNativeFromCallback` |

按 PID/进程名、线程名、异常类型/栈顶、`MainActivity` 生命周期和时间关联。相同错误文本可能在异常捕获、Bugly、Sentry 多渠道重复上报；不能数成多次崩溃。RN→Native 消息含 `action type`，请求/回调要在同次调用时间窗匹配；原始 JSON 可含敏感字段。

## 崩溃、页面错误与桥接区别

`AppUncaughtExceptionHandler` 对类名含 `java.util.concurrent` 或 `java.lang` 的异常只写 `ignore` 并返回；其他异常写 XLog，应用启动 15 秒内写 `return` 而不走本类 `relaunchApp`，超过 15 秒调用 `AppUtils.relaunchApp(true)`。这些是此 handler 的分支，不排除系统或其他组件重启进程。页面 `PageErrorBoundary` 捕获 React 渲染错误，设置 `hasError` 展示错误页；点击按钮才 `RNRestart.Restart()`。全局 JS handler 会 `console.warn`、`postNativeError` 和 XLog，不能用一条全局报错证明 Native 进程死亡。

`YunBanRNInterface` 的 `rnCallNative` 和带 callback 版本在入口用 XLog 打请求；解析/分发异常上报 Bugly caught exception。SN 请求另有 `[request]`、`[reply]`、`[error]` 日志。入口被调用、EventBus 被 post、平台服务处理和 JS callback 收到值是不同节点。ANR 属线程长期阻塞，必须有系统 ANR 痕迹或线程栈，不能以一段日志静默定因。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| Native 未捕获 | `AppUncaughtException uncaughtException:` / 异常栈 | 进入 handler；看 `ignore`、`return` 或后续重启。 |
| RN 全局 | `globalErrorHandler Error` / XLog `globalErrorHandler` | JS 全局错误被捕获；不一定进程终止。 |
| 页面边界 | `PageErrorBoundary` + error message/stack | 渲染边界进入错误页。 |
| Bridge SN | `[request] RN 请求 SN` / `[reply] RN 返回 SN` / `[error] RN 回调异常` | 请求、回复和异常分开。 |
| Activity 重建 | `MainActivity onCreate, [taskID:]`、`onDestroy` | 生命周期变化；结合 PID 判断是否进程重启。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| JS 页面报错，PID 连续 | 页面/Bridge 错误而非已证实进程死亡 | ErrorBoundary、RNRestart 操作、系统进程日志。 |
| Native 异常后新 PID | 可能重启，但需对齐分支和时间 | 异常类型、15 秒门槛、系统死亡原因。 |
| Bridge 请求出现但 callback 不来 | Native 分发/异步服务 | action type、对应平台模块回调、生命周期。 |
| 日志长时间空白 | 可能 ANR，也可能采集断档/进程暂停 | traces、系统 ANR 事件、主线程栈和日志轮转。 |
| Bugly/Sentry 有事件而文本无 | 证据通道覆盖不同 | 事件时间、PID/版本、当前文本来源。 |
