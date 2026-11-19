# 屏幕硬件、方向与状态灯

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理屏幕电源/方向/亮度、状态灯、补光异常。此领域指 Android 平台能力；JS 屏保内容另见 [屏保](screen-protection.md)。入口：`android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsDisplayControl.kt`、`android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsStatusLightControl.kt`、`android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/adapter/UdiDisplayControl.kt`、`android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/adapter/UdiStatusLightControl.kt`。

从业务调用 `PlatformRegistry` 或 Native module 找到 `set_screen_power`、`set_orientation`、状态灯动作，再按机型追 Adapter 的 `[request]`、`[stage_request]`、`[stage_complete]`、`[complete]`/`[not_configured]`。UDS 的 `uds_ready`、同步 helper 接受与硬件结果分开；UDI 的 HTTP/SDK 回调也不自动证明用户实际看到变化。

SK06 补光入口在 `android/app/src/sk06/kotlin/com/seewo/yunban/platform/uds/UdsFaceFillLightControl.kt`，SK22 的 `UdiPlatformServices#faceFillLightControl` 在此基线返回 `NOT_CONFIGURED`。状态灯还受 `src/models/authStatusModel.ts#queryResourceList` 的资源开关影响；开关关闭和平台调用失败是两种断点。

屏幕保持黑色时先区分系统屏幕电源、RN 页面/Modal、节目播放器；分别联合 [电源](power-schedule.md)、[当前置顶](mode-occupation-and-current-top.md)、[媒体](program-and-media.md)。

## 代码定位与关联键

| 能力 | 源码与符号 |
| --- | --- |
| SK05/06 显示 | `android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsDisplayControl.kt#setScreenPower/#setOrientation` |
| SK05/06 状态灯 | `android/app/src/uds/kotlin/com/seewo/yunban/platform/uds/UdsStatusLightControl.kt#setSteadyLight/#setBreathingLight` |
| SK22 显示 | `android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/adapter/UdiDisplayControl.kt` |
| SK22 状态灯 | `android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/adapter/UdiStatusLightControl.kt` |
| SK06 补光 | `android/app/src/sk06/kotlin/com/seewo/yunban/platform/uds/UdsFaceFillLightControl.kt` |
| 授权对状态灯的门槛 | `src/models/authStatusModel.ts#queryResourceList` |

以 `action`、目标 `power/orientation/state`、一次请求和其 callback 时间窗关联。显示电源、旋转、状态灯和人脸补光是不同能力；同一时刻“黑屏+灯灭”不能自动归到同一个 API。状态灯的 `statusLampShow` 配置是上游门槛，不等于平台回调状态。

## 两套平台的完成点

UDS 显示 `setScreenPower` 先判断 helper ready，再同步调用 `setScreenStatus`；`[accepted]` 是提交到 helper 成功，没有实际屏幕完成回调。UDS 旋转用 `setScreenOrientation` 的 boolean 判定。UDS 状态灯的 boolean 也只表示 helper 仍可接受同步调用，`false` 归 `NOT_READY`。SK05/06 还要按各自绑定判断具体硬件。

SK22 UDI 显示先检查 Runtime 状态，再调度到后台并回报 `[complete]`；状态灯稳态 RED/GREEN 分两阶段 `set_power_led_color`、`set_rgb_led_brightness`，OFF 只设亮度。某阶段失败就不能宣称最终颜色已应用。SK22 `setBreathingLight` 明确返回 `UNSUPPORTED`；补光在此基线为 `NOT_CONFIGURED`。平台 callback 成功仍只代表 SDK 边界结果，物理显示需系统或现场证据。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| UDS 显示 | `UdsDisplayControl [request] action=set_screen_power`、`[not_ready]`、`[accepted]` | helper 可用与命令同步接受。 |
| UDS 状态灯 | `UdsStatusLightControl [request] action=set_steady_light` / `[not_ready]` / `[accepted]` | 同步状态，不是 LED 视觉结果。 |
| UDI 显示 | `UdiDisplayControl [request]` / `[not_configured]` / `[complete]` | Runtime/后台 API 结果。 |
| UDI 状态灯 | `UdiStatusLightControl [stage_request]` / `[stage_complete]` / `[complete]` | 颜色与亮度阶段结果。 |
| UDI 呼吸灯 | `[unsupported] action=set_breathing_light` | 此基线不支持该命令。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 业务想开屏，没 Adapter request | RN/Native 调用或配置门槛 | 调用方日志、权限、机型绑定。 |
| UDS `[not_ready]` | helper 尚不可用或释放 | UDS 初始化/连接状态。 |
| UDI `not_configured`/`NOT_READY` | Runtime 未配置或初始化中 | `UdiRuntime [udi_init]` 结果。 |
| UDI 某 `stage_complete` 失败 | 特定 LED 阶段 | stage/reasonCode、同次下一阶段是否出现。 |
| Adapter 成功但画面仍黑 | 系统显示、RN Modal、播放器分层 | 屏幕物理状态、[当前置顶](mode-occupation-and-current-top.md)、[媒体](program-and-media.md)。 |
