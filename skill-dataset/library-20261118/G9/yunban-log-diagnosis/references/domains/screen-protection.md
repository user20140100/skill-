# 屏保模式

## 边界

处理屏保配置不生效、无操作后未出现、内容错误、被考勤遮挡或退出后又出现。核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。这里的屏保是 RN 的内容 Modal；屏幕物理电源见 [显示与灯](display-and-light.md)，谁取得占用权见 [当前置顶](mode-occupation-and-current-top.md)。仅凭配置接口成功，不能确认 Modal 可见或视频已播放。

## 代码定位与关联键

| 目的 | 源码与关键符号 |
| --- | --- |
| 推送设置/移除 | `src/push/handlers/protectionScreenPush.js`：`setScreensaver`、`removeScreensaver`、`needDisplayNow` |
| 查询、转换、默认值 | `src/models/screenProtectionModal.ts`：`queryScreenMode`、`handleScreenMode`、`setMode`、`setNoneffective` |
| 无操作计时与展示 | `src/views/container/ScreenProtection/index.js`：`refreshTimer`、`update`、`render` |
| 占用权 | `src/units/modeController/withModeController.js`、`src/units/modeController/occupationController.js` |
| 公告及照片内容 | `src/models/screenProtectionModal.ts#queryInformDetail`、`src/views/container/ScreenProtection/` 下对应组件 |

| 关联键 | 使用限制 |
| --- | --- |
| 设备 SN、一次 `setScreensaver`/`removeScreensaver` 推送时间 | 同一设备相邻配置变更没有本地屏保任务 ID，需按时间顺序拆开。 |
| `code`、`waitMinute`、`publishUid`、图片/视频资源 ID | `code` 是内容类型；`publishUid` 只用于公告详情，不代表整个屏保配置。 |
| `occupationModeStatus.currentMode`、`isOccupied`、路由名 | 占用模式与 `screenProtection.mode` 是两种状态；路由名也不是 Modal 可见证据。 |

## 期望链路与分叉

`setScreensaver → queryScreenMode(snCode) → data.code → handleScreenMode → setMode → 内容补充查询 → 定时/立即触发 → occupyScreen → Modal.visible`。若接口无 `data.code`，`queryScreenMode` 执行 `resetMode`。`handleScreenMode` 用 `data.content` 解析内容，设置 `waitMinute`，公告有 `publishUid` 才查询详情；班级/学校相册分别触发照片查询。云图片按设备 `screenPattern` 从横图或竖图 URL 生成 `imgs`。逐层核查“配置得到、内容得到、占用成功、组件可见、媒体播放”。

`removeScreensaver` 调用 `setNoneffective`，当前实现重置为默认 `MODE.home`、5 分钟，`effect` 仍为 `true`；不能据名称推断屏保总开关变为 `false`。`MODE.home` 不在 `MODE_COMPONENTS`，所以回首页不等于弹出屏保。`setScreensaver.needDisplayNow` 只触发 `START_PROTECTION_AT_ONCE`；对应 handler 调 `occupyScreen()`，本身没有直接设置 `visible=true`。普通计时到达时，`update()` 才在已占用情况下 `resetHome()` 并置 `visible=true`。

若到点时 `currentMode=attendance`，`update()` 先判断是否仍有进行中的考勤。有则可能跳考勤页、隐藏弹层、重置计时并返回；没有则释放考勤占用后再申请屏保。失去 `isOccupied` 时 `getDerivedStateFromProps` 会把原先的 `visible=true` 改为 `false`。最终 `Modal.visible` 同时要求 `isOccupied && !!MODE_COMPONENTS[mode] && visible`。

## 实际日志指纹

| 节点 | 可检索文本及来源 | 能确认什么 |
| --- | --- | --- |
| 立即显示事件 | `ScreenProtection` + `startScreenProtectAtOnce` | 收到立即占用事件；不能确认 Modal 已显示。 |
| 计时决策 | `ScreenProtection` + `current mode:` | `update()` 已运行并读到当时的占用模式。 |
| 考勤分叉 | `current mode is attendance, has in attendance event` / `no in attendance event` | 到点后保留考勤或释放考勤的分支。 |
| 导航考勤 | `current routeName:` | 只在考勤仍进行时记录当时路由。 |
| 占用申请与结果 | `occupation` + `add startOccupation: screenProtection` / `final status:` / `current effectMode is:` | 屏保申请、优先级裁决及生效模式；不证明媒体已渲染。 |

`queryScreenMode`、`setMode` 是源码符号，不是保证出现的日志文本。若只有 XLog、没有 JS Console/网络日志，缺少配置查询证据时应写“未覆盖”，不能写“未查询”。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 仅有设置推送 | 指令到接口查询之间 | 同时间窗的请求/响应、SN、JS 错误。 |
| 查询返回且 `code` 为空 | model 会恢复默认 home | 接口原始业务码与脱敏 `code`、配置目标设备。 |
| 配置为 notice/photo/video，但内容空 | 内容补充查询或资源列表 | `publishUid`、相册/视频资源 ID、对应接口结果。 |
| 有 `startScreenProtectAtOnce`，无 Modal | 立即事件只申请占用；再查计时和 `visible` | `occupation` 的最终状态、`waitMinute`、下一次 `update()`。 |
| 占用失败或 `currentMode=attendance` | 优先级或考勤时段 | 当前各模式申请、考勤事件时间窗。 |
| 占用成功且组件应存在，画面仍不对 | RN `visible`、内容组件或播放器 | 内容组件日志、路由、物理屏幕状态。 |

视频/霸屏内容联查 [节目与媒体](program-and-media.md)，公告联查 [消息与通知](messaging-and-notices.md)。截图、图片 URL、人员信息和 SN 均需脱敏。
