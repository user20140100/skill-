# 定时电源、待机与唤醒

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理未按计划关机、误关机、待机无法唤醒、重启或系统校时影响计划。入口：`android/app/src/main/java/com/seewo/yunban/system/services/MCUOperationService.java`、`android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsPowerControl.kt`、`android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/adapter/UdiDevicePowerAdapter.kt`。

## 判定顺序

`计划加载/变更 → 当前是否在关机区间 → 近期开机时间跳过条件 → 倒计时 → 平台预配置 → 到点动作 → 回调/设备状态`。先搜 `McuService` 的 `checkShouldPowerOff`、`[skip_countdown]`、`[power_control] action=prepare_scheduled_power_transition`。下一次开机时间过近会跳过倒计时；`status=UNSUPPORTED` 会退到原有到点动作，`status=FAILED` 与 `status=IGNORED reason=stale_countdown_callback` 要分别解释。

SK05/06 的 `UdsPowerControl [accepted]` 仅为旧 `IDevicePower` 同步入口接受命令，没有物理完成 callback。SK22 的 `UdiDevicePowerAdapter [power_task_request]/[power_task_complete]` 要按 `stage=clear_power_control_tasks`、`set_power_control_task` 区分；任务设置成功不自动证明设备实际关机/唤醒。SK22 的 `[scheduled_standby] screen_event_received` 及 reboot 回调另成链。平台细节见对应机型参考。

注意设备校时可能导致墙上时间跳变；同时比较单调时间/日志顺序与计划绝对时间。若表现是屏幕黑但进程还在运行，读 [显示](display-and-light.md)，不要直接称作关机。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 计划与倒计时 | `android/app/src/main/java/com/seewo/yunban/system/services/MCUOperationService.java#checkShouldPowerOff/#prepareScheduledPowerTransition` |
| 计划恢复/计算 | `android/app/src/main/java/com/seewo/yunban/plugins/mcu/MCUPlanManager.java` |
| SK05/06 旧平台 | `android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsPowerControl.kt` |
| SK22 UDI 任务 | `android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/adapter/UdiDevicePowerAdapter.kt` |
| 推送改计划 | `src/push/handlers/devicePush.js`：`systemCmd-updateDevicePowerPlan`、`systemCmd-cancelPowerPlan` |

关联时记录计划类型、关机/开机绝对时间、`power_off_after_seconds`、`wakeup_after_seconds`、倒计时 generation 和一次 Adapter action。generation 只存在于代码状态而未必落日志；若计划变更导致迟到 callback，应优先看 `stale_countdown_callback`。同一设备校时后不能只以墙上时间串联倒计时。

## 关键分叉

`checkShouldPowerOff` 先判是否处于关机区间；若下次开机时间很近，可设置忽略时间并跳过倒计时。进入倒计时后先调用 `schedulePowerOffAndWakeAfterSeconds`。回调 `SUCCESS` 带策略时，可能由设备任务接管或走本地熄屏待机；`UNSUPPORTED` 退到旧到点动作；`FAILED` 标记准备失败并重新检查倒计时。不能把这些状态归为同一个“关机成功”。

到点时 `DEVICE_POWER_TASK` 只收尾本地倒计时，不清除设备任务；`LOCAL_STANDBY` 熄屏并等待 SK22 亮屏事件触发重启。旧路径才直接调用 `enterStandbyAndWakeAfterSeconds`。SK05/06 的 UDS `accepted` 没有物理完成 callback；SK22 的 UDI 清任务、设任务、实际执行也分别取证。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 计划检查/跳过 | `McuService checkShouldPowerOff`、`[skip_countdown] reason=...` | 本轮是否进入倒计时；看具体 reason。 |
| 倒计时准备 | `[power_control] action=prepare_scheduled_power_transition` | 发起、成功/失败/UNSUPPORTED/过期回调各不相同。 |
| 到点动作 | `action=device_power_task_due` / `scheduled_standby_due` / `enter_standby_and_wake` | 本次采用哪种策略。 |
| 旧机型 Adapter | `UdsPowerControl [request]` / `[accepted]` | 同步调用被接受，非物理完成。 |
| SK22 任务 | `UdiDevicePowerAdapter [power_task_request]` / `[power_task_schedule]` / `[power_task_complete]` | 清任务、设任务的各阶段状态。 |
| SK22 亮屏 | `[scheduled_standby] screen_event_received` / `reboot_request_complete` | 待机期间亮屏事件和重启请求回调。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 计划已下发、无倒计时 | 当前区间、跳过条件或计划未恢复 | 计划绝对时间、`skip_countdown`、设备时钟。 |
| `prepare` 为 `UNSUPPORTED` | 预计走旧到点动作 | 倒计时归零及旧 Adapter 请求。 |
| `prepare` 为 `FAILED` | 准备阶段失败，可能重试 | reasonCode、计划变化和下一轮检查。 |
| 设备任务设置成功却未关机 | UDI 任务已受理，实际系统执行未证实 | UDI/系统电源事件、设备现场状态。 |
| 黑屏后又亮 | 可能是 SK22 本地待机而非物理关机 | `screen_event_received`、重启请求、PID 连续性。 |
