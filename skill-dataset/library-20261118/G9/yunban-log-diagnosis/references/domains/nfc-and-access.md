# NFC 刷卡与韦根输出

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理“卡读到了但没有 RN 事件/响铃/门禁输出”及卡号格式错误。先按日志 TAG 确认输入路径：三个机型都有 `android/app/src/main/java/com/seewo/yunban/plugins/nfc/AndroidNfcPlugin.java`；SK05 另有 `android/app/src/main/java/com/seewo/yunban/plugins/nfc/SK05IntentNfcPlugin.java`；SK06 的 UDS 回调和 SK22 的 UDI 事件进入 `android/app/src/main/kotlin/com/seewo/yunban/plugins/nfc/NfcCardReadWorkflow.kt#handle`。读对应 [机型参考](../../SKILL.md#路由)。

## 事件链与指纹

UDS/UDI 链：`SDK 事件 → 卡号解析/进制映射 → [nfc_card] workflow_start → ring_requested → 后台 target.active 检查 → RN 事件 → IAccessControl 韦根请求 → Adapter 结果`。`CardReadEvent` 同时持有 RN 8 位十六进制与韦根十进制卡号；不能直接把两种表示对比为不同卡。`ring_requested` 只证明开始播放请求；异步任务可能因 Activity 非 active 或 React 未 ready 跳过 RN/韦根。

SK05 固件广播链：`cardid → hexCardId → ring → NativeCallRnHelper.sendNfcId → 线程内 sendWiegand → Signway SDK`。搜 `SK05IntentNfcPlugin` 的 `cardId`、`hexCardId`、`sendWiegand`，注意直接 Log/XLog 混用；`sendWiegand` 在 SDK 调用前写日志，不能证明硬件输出。`AndroidNfcPlugin` 从 `NEW_INTENT` 读取 Android NFC，再直接发 RN，不经该 workflow。非 SK05 的公共插件还会安装 `AcsSmcNfcPlugin`，从 USB 读卡器直接通知 RN。不要把这些直达 RN 的事件误认作 UDS/UDI workflow。

SK06 的 UDS 输出搜 `UdsAccessControl [request]/[accepted]/[not_ready]`；`accepted` 仅为本地 helper 同步接受。SK22 先搜 `UdiNfcCardEvent [nfc_tag] subscribe_requested/listener_received/accepted/ignored`，再追公共流程；`listener_received` 也可能因 event/payload 不符而被忽略。

报告中只展示卡号掩码。若 RN 已收到卡但考勤没记录，读 [考勤](attendance.md)；若模式置顶影响页面，读 [当前置顶](mode-occupation-and-current-top.md)。

## 代码定位与关联键

| 输入/输出 | 源码与符号 |
| --- | --- |
| SK05 固件广播与 Signway | `android/app/src/main/java/com/seewo/yunban/plugins/nfc/SK05IntentNfcPlugin.java#onReceive/#sendWiegand` |
| Android Intent 与 ACS USB | `android/app/src/main/java/com/seewo/yunban/plugins/nfc/AndroidNfcPlugin.java#onNewIntent`、`android/app/src/main/java/com/seewo/yunban/plugins/nfc/AcsSmcNfcPlugin.java#init` |
| SK06 UDS 回调 | `android/app/src/uds/java/com/seewo/yunban/plugins/uds/UdsPlugin.java#onNfcCardRead` |
| SK22 UDI 事件 | `android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/event/UdiNfcCardEventModule.kt#onEvent` |
| 公共编排与输出 | `android/app/src/main/kotlin/com/seewo/yunban/plugins/nfc/NfcCardReadWorkflow.kt#handle`、`android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsAccessControlAdapter.kt#sendCard` |

SK05 广播给 `cardid` 整数，转换成 8 位 hex 给 RN，原整数给 Signway；公共 workflow 的 `CardReadEvent` 分别持有 `rnHexCardId`、`wiegandDecimalCardId`。先根据来源与转换规则核对同一张卡，报告只展示掩码及保留末几位。`wiegand_complete` 的卡号可与同次 `workflow_start` 强关联，但旧 SK05 和 Android/ACS 直达 RN 没有相同任务 ID；多次连续刷卡不可只按秒合并。

## 平台条件与结果语义

`UdsPlugin` 在 SK05/SK06 旧 UDS flavor 都安装，但 `registerCallback` 对 SK05 不注册 NFC callback。SK05 的 Signway 路径独立于 `IAccessControl`；SK06 的 UDS callback 和 SK22 的 UDI 事件才进公共 workflow。SK22 先检查订阅状态、事件名、payload、十进制卡号映射，之后才会出现 `[nfc_card] workflow_start`。

公共 workflow 先验证卡号和 target、请求响铃，再用 `AppTaskExecutor` 异步顺序发 RN 与韦根。RN Context 未 ready 时只跳过 RN；随后仍可继续尝试韦根。SK06 `UdsAccessControl [accepted]` 表示 helper 同步接受，不是门禁电气动作；SK05 `sendWiegand` 日志也在 SDK 调用前。SK22 须再看其 UDI Access Adapter 的 callback 状态。

## 实际日志指纹

| 路径/节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| SK05 输入 | `SK05IntentNfcPlugin` + `cardId:` 或 `hexCardId:` | `cardId:0` 是无效输入且直接返回；hex 日志说明已走到 RN 调用前。 |
| SK05 输出 | `sendWiegand, cardId:` / `onError:` | 韦根 SDK 调用前或响铃错误；两者通道不同。 |
| Android/ACS | `AndroidNfcPlugin nfcId` / `AcsSmcNfcPlugin nfcCard:` | 各自读到卡，后续仅直接通知 RN。 |
| SK22 UDI | `[nfc_tag] subscribe_skipped/subscribe_requested/listener_received/ignored/accepted` | 从订阅到 payload 接受分段判断。 |
| 公共流程 | `[nfc_card] workflow_start`、`ring_requested`、`rn_skipped/rn_dispatched`、`wiegand_requested/wiegand_complete` | 每个阶段分别判断；`rn_dispatched` 仍不证明 JS listener 已处理。 |
| SK06 门禁 | `UdsAccessControl [request]/[not_ready]/[accepted]` | helper 可用和同步接受结果。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 无任何读卡入口 | 硬件、订阅或日志通道 | 机型、广播/UDS/UDI/USB 事件及 logcat 覆盖。 |
| SK22 `listener_received` 后 `ignored` | 事件名、payload 或卡号格式 | 同一事件的 reasonCode、脱敏 payload 形状。 |
| `workflow_start` 后没有 RN | 异步调度/Activity/RN 生命周期 | `rn_skipped`、`schedule_failed`、销毁时间。 |
| RN 已派发、考勤没有记录 | JS 监听与考勤业务 | [考勤](attendance.md) 的事件和人员匹配。 |
| 韦根请求后无可确认结果 | Adapter/SDK/硬件 | UDS/UDI 回调、控制器现场状态；不把 accepted 当开门。 |
