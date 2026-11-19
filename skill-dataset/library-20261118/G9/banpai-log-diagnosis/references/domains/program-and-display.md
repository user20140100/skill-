# 节目与展示

## 边界

本手册覆盖门牌侧节目发布通知、节目有效列表拉取、节目顶层展示，以及与外部 Uips SDK 的边界。代码事实基于 ab680809。

资源下载进度、媒体解码、播放器渲染和 Uips SDK 内部的发布数据处理不在当前应用源码与日志的可确认范围。不能把 Uips 回调成功表述为“资源已下载并正在播放”。

## 代码定位与关联键

下列源码路径均相对 app/src/main/java/com/seewo/yunban。

| 目的 | 路径与关键符号 |
| --- | --- |
| 节目拉取、IoT 转发与顶层状态 | data/remote/program/ProgramRepositoryImpl.kt：triggerUipsFetchValidPublishList、handleCommandMessage、onProgramNotify |
| 节目接口边界 | data/remote/program/IProgramRepository.kt |
| 节目页面容器 | ui/program/ProgramFragment.kt、ui/program/ProgramViewModel.kt |
| 同步入口 | data/remote/sync/SyncDataImpl.kt：loadProgramData |
| 绑定信息缓存 | data/local/store/program/ProgramLocalStore.kt |

| 关联强度 | 键与使用限制 |
| --- | --- |
| 绑定与发布上下文 | roomUid、schoolUid、设备 snCode | 这些是场地级信息，不能区分同一场地的相邻节目变更 |
| IoT 节目变更 | publish 或 unPublish 命令与窄时间窗 | 应用层日志不含发布单号或资源标识 |
| SDK 回调 | onProgramNotify 的 hasProgram 与回调顺序 | hasProgram 只表示有无节目，不能唯一定位一个发布版本 |
| 同步拉取 | triggerUipsFetchValidPublishList 与回调结果 | 当前没有持久化同步批次或 SDK 请求 ID |

## 期望链路

    SyncData.loadProgramData 或离线启动检查
      -> ProgramRepositoryImpl.triggerUipsFetchValidPublishList
      -> UipsController.onIotMessage(type=ALL)
      -> 最多等待 10 秒 SDK 回调
      -> 回调 success 作为节目同步任务结果

    IoT publish 或 unPublish
      -> ProgramRepositoryImpl.handleCommandMessage
      -> 先移除 Program 顶层状态
      -> UipsController.onIotMessage
      -> Uips 事件 onProgramNotify(hasProgram, canOperate)
      -> 更新 hasProgram；有节目时请求 TopScreenService 展示 Program

ProgramRepositoryImpl 初始化时保存当前绑定信息给 ProgramLocalStore，并注册 Uips 事件监听。节目有效且用户离开节目页时，会设置 60 秒无触摸观察器，使 Program 顶层页面重新显示；没有节目时移除观察器。

SyncData 的节目任务只等待 UipsController 的一次回调，超过 10 秒就回调失败。ProgramFragment 负责容器和操作栏，实际节目资源与播放由 Uips SDK 接管。

## 日志指纹与关联键

| 节点 | TAG 或文本 | 出现时确认的事实 |
| --- | --- | --- |
| 绑定信息转交 | ProgramRepositoryImpl + param saveBoundInfo | 当前绑定信息已交给节目本地存储 |
| 全量节目拉取 | triggerUipsFetchValidPublishList | 已请求 Uips 获取有效发布列表 |
| IoT 节目命令 | handleCommandMessage command = publish 或 unPublish | 客户端已接收并转交该节目通知 |
| 节目状态回调 | onProgramNotify hasProgram | Uips 已通知有无可展示节目 |
| 可选 SDK 证据 | UIPS-ProgramRepository 的 mergeProgramResult size，或 UIPS-ProgramPlayingControl 的 hasProgram | 当前导出若包含 Uips 调试日志，可进一步确认 SDK 是否得到可播放节目；这些日志不是所有版本和导出物都保证存在 |
| 顶层展示 | TopScreenService 中 Program 的 set 或 remove 日志 | 页面层级已尝试改变，不等于画面已渲染 |
| 本地清理 | param clearAll | ProgramLocalStore 清理被触发 |

关联时使用设备、roomUid、节目命令、一次同步时间窗和 Uips 回调顺序。由于当前回调日志不携带发布单号或资源标识，多个节目变更紧邻发生时应明确关联强度不足。

## 断点判断

| 最晚可见节点 | 最早可确认断点 | 下一步 |
| --- | --- | --- |
| 无 triggerUipsFetchValidPublishList | 同步或启动检查未进入节目模块 | 查 SyncDataViewModel 的节目任务、网络与绑定状态 |
| 有拉取日志但 10 秒后同步失败 | Uips 回调没有及时成功 | 收集 Uips SDK 日志、网络及发布有效期；当前应用日志不能定因 |
| loadProgramData:true，随后 SDK 或 onProgramNotify 表示无节目 | Uips 拉取回调成功，但没有有效可播放节目 | 查发布有效期、场地与 SDK 的节目合并结果；不要将同步成功表述为节目正在播放 |
| 有 onProgramNotify=false | Uips 判定当前无可展示节目 | 查后端发布条件、有效期和绑定场地 |
| 有 onProgramNotify=true，无 Program 顶层 | Uips 回调到 TopScreen 路由 | 查 TopScreenService 优先级与当前更高层页面 |
| 已尝试展示，画面未播放 | 应用层已走到 SDK 边界 | 查 Uips、下载、播放器和渲染日志，不能只改 ProgramFragment |
| unPublish 后仍显示 | 命令已转交或节目状态未刷新 | 查后续 onProgramNotify、TopScreen 移除和 SDK 状态 |

配置或绑定变更后节目异常时，先读取 [同步与配置](sync-and-configuration.md)，确认新的绑定和同步是否已完成，再判断节目 SDK 的结果。
