# 同步与配置

## 边界

本手册覆盖绑定信息刷新、全量同步触发、同步页任务执行、设备全局配置和 UI 模板刷新。代码事实基于 ab680809。

同步完成只表示客户端在其定义的回调和超时范围内完成了请求；不自动证明页面、门锁、人脸库或节目播放已经实际生效。涉及节目时继续读取 [节目与展示](program-and-display.md)，涉及人脸库时继续读取 [人脸认证](face-authentication.md)。

## 代码定位与关联键

下列源码路径均相对 app/src/main/java/com/seewo/yunban。

| 目的 | 路径与关键符号 |
| --- | --- |
| IoT 触发、延时刷新与领域调度 | data/remote/sync/SyncDataImpl.kt：handleCommandMessage、checkRefreshData、startDelayRefresh、loadXxxData |
| 同步页串行编排和超时 | ui/sync/SyncDataViewModel.kt：startSync、syncData、withTimeoutOrDefault |
| 全局配置与模板 | data/remote/config/ConfigRepositoryImpl.kt：fetchConfigData、fetchAllConfig、handleCommandMessage |
| 配置 API | data/remote/api/IConfigApi.kt |
| 绑定刷新定义 | data/remote/binding/IBindingRepository.kt：refreshBindInfoFromServer |

| 关联强度 | 键与使用限制 |
| --- | --- |
| 同一次全量刷新 | snCode、roomUid、refreshAll 或 rebind 命令、窄时间窗 | 当前没有持久化 syncRunId；相邻刷新必须用命令到 SyncData 页面间的时间顺序区分 |
| 延时自主刷新 | snCode、fetchDelayPullTime 结果、startDelayRefresh 日志 | 没有 IoT 命令不代表未同步，可能走延时自主触发 |
| 单项配置 | command、extraData.changeType、配置键或 templateId | 同一设备连续变更时，changeType 为空或日志缺失会降低关联强度 |
| 单模块结果 | SyncDataViewModel 的 loadXxxData 名称和该次时间窗 | SYNC_OTHER 是九项结果汇总，不是某一接口的唯一结果 |

## 触发与同步编排

    IoT refreshAll 或 rebind
      -> SyncDataImpl 取消延时刷新
      -> TopScreenService 切换到 SyncData
      -> SyncDataViewModel.startSync
      -> refreshBindingInfoData
      -> 依次执行学校、配置、课表、电源、节目、门锁、巡检、活动、座位、公告、考勤

设备网络可用且已绑定时，SyncDataImpl 读取延时配置并等待 refreshAll；等待期未收到推送才主动切换到 SyncData。网络断开、解绑或收到 refreshAll、rebind 都会取消延时任务。延时配置请求失败时随机回退 0 至 60 秒。

SyncDataViewModel 对学校、配置、课表、电源、节目、门锁、巡检、活动、座位、公告分别使用 10 秒超时，对考勤使用 20 秒超时；任务是串行执行。首页状态只由课表结果决定，考勤状态只由考勤结果决定，其他状态是九项任务的合取。

## 配置刷新和落地

    SyncData.loadConfigData
      -> 异步触发人脸数据同步
      -> ConfigRepositoryImpl 并行拉取全局配置、UI 模板、认证方式
      -> 写入 BanpaiPreferences，并更新 StateFlow

全量配置接口是 GET /device/global/config/v1/all；同时会拉取模板和常用认证方式。配置结果任一失败会使配置任务返回失败。全局配置可更新背景、Logo、课程教师显示、离线密码、状态灯、考勤联动和课表认证；模板以 templateId 和内容时间戳决定是否更新。

IoT updateDeviceGlobalDefaultConfig 按 extraData.changeType 只拉取对应单项配置；changeDeviceUiTemplate 只刷新模板。收到 IoT 命令和单项接口成功，均只能证明配置已被客户端处理或写入偏好，仍需查看实际消费者的界面、硬件或下游逻辑。

人脸同步由 loadConfigData 异步触发，不参与 ConfigRepositoryImpl 的三项配置结果汇总。故同一时间窗可以同时出现 loadConfigData:true 和 syncFaceData 的业务失败；应将它们分别写入时间线，不能把前者作为人脸库已同步的证据。

## 日志指纹与关联键

| 节点 | TAG 或文本 | 可确认事实 |
| --- | --- | --- |
| IoT 全量触发 | SyncDataImpl + SyncFlow IOT command | 收到 refreshAll 或 rebind 并准备触发同步 |
| 延时行为 | startDelayRefresh / fetchDelayPullTime | 延时拉取、取消或回退原因 |
| 单任务结果 | SyncDataViewModel + loadXxxData:true 或 false | 对应任务回调在超时内的结果 |
| 任务超时 | Task timeout after | 同步页将该任务视为失败；底层请求是否仍在需另查 |
| 其他汇总 | SYNC_OTHER:true 或 false | 九项非首页、非考勤任务的汇总结果 |
| 全量配置 | ConfigRepositoryImpl + fetchAllConfig | 单项配置读取或解析结果 |
| 模板 | fetchCustomTemplate success / data is not updated / error | 模板请求、版本比较或解析结果 |
| IoT 配置 | handleCommandMessage command / config type | 已收到命令及 changeType 路由 |

关联时优先使用设备序列号、roomUid、命令名、changeType 与一次 SyncData 生命周期的时间窗。不要把相邻两次 refreshAll 的模块结果混为一次同步。

## 断点判断

| 最晚可见节点 | 判断 | 下一步 |
| --- | --- | --- |
| 未收到 SyncFlow 命令，且没有延时触发 | 同步尚未被本客户端触发 | 查网络、绑定状态、IoT 分发和 TopScreen 路由 |
| 某 loadXxxData 为 false 或超时 | 同步页已将该模块判失败 | 进入该模块仓库和 HTTP 日志；超时不等于请求未发出 |
| 配置任务成功，界面或硬件未变 | 配置读取完成，实际消费未确认 | 查 Preferences 对应值、StateFlow 订阅者及门锁/界面日志 |
| 单项 IoT 命令出现，值仍未更新 | 命令已路由但取值或解析未确认 | 查 changeType、对应 fetch 日志和业务响应 |
| 同步成功，节目仍未显示 | 只确认 Uips 拉取回调 | 切到节目与展示，检查 SDK 回调与播放链路 |

解绑会取消延时刷新，且其他业务模块可能清理各自本地数据。排查解绑后状态异常时，先确认房间绑定是否仍存在，再判断是否应保留旧状态。
