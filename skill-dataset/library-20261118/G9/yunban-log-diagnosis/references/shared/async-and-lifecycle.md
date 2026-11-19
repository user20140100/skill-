# 异步与生命周期边界

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。当事件跨线程、协程、定时器、Activity/RN 页面或进程重启时读取。先为每个回调/任务标出创建、排队、执行、完成和清理时间；页面消失、函数返回与异步任务完成不是同一节点。

## 四种实际时序

| 场景 | 源码时序 | 诊断边界 |
| --- | --- | --- |
| 刷卡分段 | `NfcCardReadWorkflow.handle → ring_requested → AppTaskExecutor 排队 → active 检查 → sendToRn → active 再检查 → sendToWiegand → 平台回调` | 响铃请求先于排队；Activity target 失效或 RN 未 ready 可跳过后续；`wiegand_requested` 仍非硬件完成。 |
| 文件上传 | `CStoreUploader.uploadFile → ioScope.launch(IO + SupervisorJob) → 文件/策略/上传 → callback` | 调用返回时协程可能尚未执行；最终要匹配同文件的回调及业务引用。进程终止后不能假设协程仍运行。 |
| SK06 初始化 | `DeviceHandler.init → 等 OpenSDK 或 60 秒超时 → resolveSn/fallback → SN ready → finishInit/capacity callback` | `[wait]` 期间初始化链尚未释放；`[ready]`、`[capacity]` 与 RN 收到 SN 是不同节点。 |
| 屏保计时与置顶 | `ScreenProtection.refreshTimer → update → occupyScreen → isOccupied/visible → Modal` | 点击可重置计时；考勤可抢占；发起 occupy 不等于屏保已经可见。 |

`NfcCardReadWorkflow` 入队前检查一次 active，任务执行前和韦根前再次检查；`ActivityCardReadBusinessTarget.release` 先置 inactive 再清空 Activity。`rn_dispatched` 只到 Native 发给 RN 的尝试，JS 消费继续看[RN/Native 边界](rn-native-boundary.md)。SK06 的 OpenSDK 迟到回调、兜底与超时可能在同一窗口竞争；`mSnResolved` 使后到结果被忽略，不能按最后一条 SN 日志倒推首个生效来源。

`withModeController` 在构造时订阅占用状态，卸载时移除；`ScreenProtection` 在挂载时监听立即屏保、点击和新考勤事件，在卸载时移除并取消无操作定时器。`startScreenProtectAtOnce` 仅请求占用，`update` 才按当前模式/事件决定导航或设置 `visible`；最终 Modal 还要求 `isOccupied`、组件存在和 `visible` 同时满足。异步事件跨过卸载时点，要先核对监听是否仍在，而不是把“上游发了事件”写成“页面处理了事件”。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 刷卡任务与 Activity 状态 | `android/app/src/main/kotlin/com/seewo/yunban/plugins/nfc/NfcCardReadWorkflow.kt#handle/#release`、`android/app/src/main/java/com/seewo/yunban/system/helper/AppTaskExecutor.java#run` |
| 上传协程与回调 | `android/app/src/main/java/com/seewo/yunban/system/helper/cstore/CStoreUploader.kt#uploadFile` |
| SK06 SN 等待/释放 | `android/app/src/sk06/java/com/seewo/yunban/handler/DeviceHandler.java#init/#onOpenSDKConnected/#finishInit` |
| 页面订阅与计时 | `src/units/modeController/withModeController.js`、`src/views/container/ScreenProtection/index.js#refreshTimer/#update/#componentWillUnmount` |

时间线至少保留 PID/进程、线程（若日志提供）、单调序号或请求键、页面挂载/卸载和回调时间。刷卡用脱敏卡号与输入来源；上传用文件名/大小与 callback；SN 用同一初始化会话；屏保用模式与计时重置时间。不同进程时钟可能校时、重启后 PID 会变，跨线程日志的时间邻近只能作弱关联。

## 实际日志指纹与可证明范围

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 刷卡入口/排队前 | `NfcCardReadWorkflow` + `[nfc_card] workflow_start` / `ring_requested` / `schedule_failed` | 输入进入、响铃调用、排队失败的不同阶段。 |
| 刷卡异步执行 | `inactive_target_before_dispatch` / `rn_skipped reason=react_not_ready` / `rn_dispatched` / `inactive_target_before_wiegand` | 目标失效、RN 未就绪或 Native 已走发送分支。 |
| 韦根回调 | `[nfc_card] wiegand_requested` / `wiegand_complete` | 已请求与平台回调完成；实体门禁结果另查。 |
| 上传协程 | `CStoreUploader` + `start ... file upload:` / `upload file fail:` | 已进入策略前阶段或失败；成功要看调用方 callback。 |
| SK06 等待与释放 | `sn_sk06` + `[wait]` / `[timeout]` / `[resolve]` / `[ready]` / `[capacity]` | 等待、兜底/解析、SN dispatcher 就绪和初始化链释放。 |
| 屏保计时 | `ScreenProtection` + `current mode:` / `startScreenProtectAtOnce` | 计时回调或立即请求，非 Modal 可见证明。 |

没有专门的“已排入 AppTaskExecutor”成功日志；看到 `ring_requested` 但没有后续日志，仍要检查目标失效、进程/日志截断和输出通道。`CStoreUploader` 文件不存在时直接 callback 404，start 又是 Debug 级；不能凭 start 缺失断定协程未执行。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 刷卡响铃、无 RN/韦根 | 入队失败、target 失效、执行延迟或日志缺口 | `schedule_failed`、`inactive_target...`、Activity 销毁时间。 |
| RN 已发、韦根未请求 | 第二次 active 检查或流程异常 | `inactive_target_before_wiegand`、同卡号后续日志。 |
| 上传 start 后无完成 | 策略/直传、回调、进程生命周期 | 同文件的失败日志、回调结果、PID 连续性。 |
| SK06 `[wait]` 后无 `[capacity]` | OpenSDK/超时任务、进程中断 | 完整 60 秒窗口、`[timeout]`、进程重启证据。 |
| 屏保触发却未显示 | 占用裁决、组件/visible、页面卸载 | `effectMode`、`current mode:`、当前 route 与 Modal 条件。 |
