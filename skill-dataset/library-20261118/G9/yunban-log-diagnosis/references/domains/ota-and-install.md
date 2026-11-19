# OTA 与应用安装

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。先区分云班客户端 OTA、UDS 服务 OTA 与其他应用安装；它们的检查、下载和安装回调不同。入口：`android/app/src/main/java/com/seewo/yunban/packages/ota/OTAManager.java`、`android/app/src/uds/kotlin/com/seewo/yunban/packages/ota/UDSOTAManager.kt`、`android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/UdiPlatformServices.kt`。

客户端 OTA 按 `checkUpdate → onUpdateReturned → onDownloadStart/Update/Success/Failed → 安装请求 → 安装终态` 查。`OTAManager` 的 `onDownloadSuccess` 只证明下载 callback，不是安装完成。UDS 服务 OTA 的 `UDSOTAManager` 只编入旧 UDS flavor，不能把其日志缺失当 SK22 故障。

在此基线，SK05/06 的 `PlatformBindings` 使用 Legacy APK 安装能力；SK22 的 `UdiPlatformServices#apkInstaller` 与 `installCommand` 返回 `NOT_CONFIGURED`。若 SK22 看到 `NOT_CONFIGURED`，先确认调用的是哪种安装能力与 APK 提交，不能套用旧 OpenSDK/PackageManager 的成功语义。

检索 `OTAManager` 的 `checkUpdate`、`onUpdateReturned`、`onDownload*`，旧机型的 `UDSOTAManager`；再追安装 Adapter/系统广播。以版本号、包名和下载文件关联，报告不展示下载签名 URL。下载失败读 [网络](network-and-file-transfer.md)。

## 代码定位与关联键

| 目标 | 源码与符号 |
| --- | --- |
| 客户端检查和下载 | `android/app/src/main/java/com/seewo/yunban/packages/ota/OTAManager.java#checkUpdate/#setDownloadListener/#setUpdateListener` |
| UDS 服务升级 | `android/app/src/uds/kotlin/com/seewo/yunban/packages/ota/UDSOTAManager.kt#checkUpdate`、`android/app/src/uds/java/com/seewo/yunban/plugins/uds/UdsPlugin.java` |
| SK22 安装能力 | `android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/UdiPlatformServices.kt` |
| 旧机型安装能力 | `android/app/src/sk05/kotlin/com/seewo/yunban/platform/binding/PlatformBindings.kt`、`android/app/src/sk06/kotlin/com/seewo/yunban/platform/binding/PlatformBindings.kt` |

用目标包名、当前/目标版本、下载开始时间与脱敏文件名关联。OTA SDK 回调没有保证统一任务 ID；同一包连续检查更新时，不可只用目标版本串联下载和安装。先辨认日志属于客户端 APK、UDS 服务 APK 还是其他应用安装。

## 三种结果边界

客户端 `checkUpdate` 可由手动调用或定时器触发；`onUpdateReturned` 的 YES/NO/TIMEOUT/NONE_NETWORK 进入不同 Promise 分支。`onDownloadStart` 设置更新状态，`onDownloadUpdate` 推进进度；`onDownloadSuccess` 只证明 SDK 下载 callback。`onDownloadFailed` 中特定“已下载”状态会按可继续处理，其余会发 `updateFail` 事件。不能把进度到 96 或下载成功当安装成功。

UDS 服务 OTA 使用单独的 `UDSOTAManager` 与 UDS 连接/安装回调，只编入旧 flavor。SK22 的 `apkInstaller`、`installCommand` 在本基线返回 `NOT_CONFIGURED`；若设备实际上完成安装，要核对 APK 对应源码或确认走了其他系统路径。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 客户端检查 | `OTAManager checkUpdate`、`onUpdateReturned() updateStatus=` | 已触发检查和 SDK 返回状态。 |
| 客户端下载 | `onDownloadStart:`、`=onDownloadUpdate`、`onDownloadSuccess`、`onDownloadFailed` | 下载阶段回调；不代表安装。 |
| UDS 服务 | `UDSOTAManager uds checkUpdate called`、`Download success/failed`、`Update check completed` | 旧机型 UDS 服务升级的独立阶段。 |
| UDS 插件重连 | `UdsPlugin on install success:` | 包安装监听回调；仍需查服务实际启动。 |
| SK22 能力缺失 | `NOT_CONFIGURED` 及调用方结果 | 平台安装接口没有配置；与网络下载失败不同。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 检查未返回 | SDK/网络或当前 promise 生命周期 | SDK callback、网络状态、是否重复检查。 |
| 返回 NO 但后台已有新版本 | 版本/渠道/环境筛选 | 包名、当前版本、更新策略。 |
| 下载失败 | SDK 下载或磁盘 | reasonCode、存储空间、下载服务器状态。 |
| 下载成功但版本未变 | 安装命令/系统安装终态 | Installer 回调、系统广播和安装后的版本号。 |
| UDS 服务下载成功但仍离线 | 安装后连接初始化 | `UdsPlugin` 安装回调、UDS 初始化日志。 |
