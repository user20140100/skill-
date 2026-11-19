# 模式占用与当前置顶

## 边界

处理考勤、考试、巡课、霸屏、屏保、通话等模式互相抢占、退出后不恢复、弹层看似“置顶错误”。核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。此处“当前置顶”指 RN 业务占用权与弹层配置；Android 系统前台进程、物理屏幕电源和节目资源是否可播分别另查。

## 代码定位与关联键

| 目的 | 源码与关键符号 |
| --- | --- |
| 模式及优先级 | `src/units/modeController/modeSetting.js`：`authority`、`disableResetHome` |
| 申请、释放与裁决 | `src/units/modeController/occupationController.js`：`startOccupationTask`、`cancelOccupationTask`、`getStatus` |
| 顺序执行 | `src/units/modeController/taskQueue.js`：`addTask`、`runNextTask` |
| 组件订阅与方法 | `src/units/modeController/withModeController.js`：`occupyScreen`、`cancelMode`、`update` |
| 弹层配置 | `src/views/container/UserPopupWindow/modeConfig.js`：`setModalMode`、`hasModeVisible`、`clearModalMode` |

本控制器没有跨模块的占用事务 ID。用设备、一次申请/释放的 `modeName`、相近的 `add startOccupation` 到 `current effectMode is:` 的顺序关联；并发事件只按时间接近不能合并。`effectMode` 是当前生效者，各模式 `isOccupied` 是各自状态；`getModeStatus().currentMode` 取自 `effectMode`。`modeConfig.key/visible` 仅是弹层配置，不能替代占用状态。

## 裁决和 UI 链路

`业务事件 → withModeController.occupyMode/occupyScreen → TaskQueue → startOccupationTask → getStatus → effectMode/isOccupied → 订阅组件重渲染 → 页面或 Modal`。优先级数字越小越高：`update=2`、`faceTime=3`、`familyPhone=5`、`exam=6`、`attendance=7`、`patrollesson=10`、`dominatingScreenResource=20`、`screenProtection=30`。`getStatus` 只检查已有更高优先级的 `isOccupied`；低优先级申请失败时要找当时占用者，不要只看申请方日志。

成功申请会设置 `effectMode` 并通知订阅者；除 `disableResetHome=true` 的模式外还调用 `resetHome()`。所以 `current effectMode` 改变只说明裁决结果，具体画面还取决于组件的 `visible`、路由和资源。`startOccupation` 返回值依据申请前 `oldOccupyStatus===false`，不能当成“本次一定取得置顶权”；以 `final status:` 与随后 `current effectMode is:` 判断。

`cancelOccupationTask` 释放当前 `effectMode` 时会置空、触发 `SCREEN_CLICK`、清掉全部模式的 `isOccupied` 并通知订阅者；释放一个未生效但标记占用的模式只清该模式。后续由组件重新申请，不能假定自动恢复原低优先级模式。`setModalMode` 与 `clearModalMode` 操作的是另一份内存配置，必须分别核对其消费者是否展示弹层。

## 实际日志指纹

| 节点 | `occupation` 日志文本 | 能确认什么 |
| --- | --- | --- |
| 入队申请 | `add startOccupation: <mode>` | 业务发起申请；队列可能尚未完成。 |
| 开始裁决 | `startOccupation: <mode>` 与其 JSON 状态 | 执行时的申请方状态。 |
| 裁决结果 | `startOccupation:<mode> final status:<true/false>` | 该模式本轮优先级检查结果。 |
| 导航重置 | `<mode>:resetHome` | 已调用导航重置；不证明页面已显示。 |
| 当前生效者 | `current effectMode is:<mode/null>` | 执行完这次申请时的 `effectMode`。 |
| 入队/执行释放 | `add cancelOccupation:`、`cancel occupation:`、`effectMode set to null` | 释放请求与当前生效者被清除的区别。 |

`withModeController`、`modeConfig` 这一层没有同等的固定 XLog；它们的状态要由消费者或现场 UI 佐证。检查 JS XLog 是否确实进入输入文件，避免把看不到这些指纹当作没有模式事件。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 业务声称触发，未见 `add startOccupation` | 业务事件到申请，或日志覆盖缺口 | 业务 handler/组件日志、JS 日志通道。 |
| 有 `add`，无 `final status` | 队列执行或文本截断 | 同 PID 后续 `startOccupation`、异常和重启记录。 |
| `final status:false` | 已被更高优先级占用挡住 | 当前各模式状态 JSON、上一轮 `effectMode`。 |
| `final status:true`，目标界面不可见 | 裁决之后的组件/路由/资源 | 对应模式组件 `visible`、路由和内容数据。 |
| `effectMode set to null` 后旧画面仍在 | 释放后 UI 更新或弹层配置 | 订阅生命周期、`modeConfig`、组件可见状态。 |
| 低优先级模式未恢复 | 释放清掉所有 `isOccupied`，等待重新申请 | `SCREEN_CLICK` 触发后对应组件是否再次申请。 |

屏保查 [屏保](screen-protection.md)，考勤查 [考勤](attendance.md)，霸屏/视频资源查 [节目与媒体](program-and-media.md)，通话查 [通话](family-calling-and-voice.md)。
