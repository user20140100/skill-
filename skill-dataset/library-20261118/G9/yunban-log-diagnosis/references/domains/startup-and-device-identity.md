# 启动与设备身份

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理启动卡住、SN 缺失、平台 SDK 未就绪、进程反复启动。入口为 `android/app/src/main/java/com/seewo/yunban/MainApplication.java`、`android/app/src/main/java/com/seewo/yunban/MainActivity.java` 和 `src/views/pages/RootPage/index.js`；SN 实现必须按 [机型](../../SKILL.md#路由)选。

## 链路

`进程/Application → 平台与 Logger Capacity → DeviceHandler/UDI 初始化 → SN 决议 → RN RootPage → 设备信息/绑定后的任务`。`RootPage` 先 `queryDeviceMsg`，并在网络、`bindingSuccess`、`schoolUid` 满足时启动部分后续任务；启动页可见不等于业务数据已加载。

| 机型 | 搜索起点 | 易误判点 |
| --- | --- | --- |
| SK05 | `sn_sk05 [init]`、`[read]` | 初始化链立即释放；真正读取 SN 在 getter，`state=ready` 不证明值有效。 |
| SK06 | `sn_sk06 [wait]`、`[uds]`、`[timeout]`、`[resolve]`、`[capacity]` | 超时后可用 fallback 或 null 放行，不能把放行当作真实 UDS SN。 |
| SK22 | `[udi_init]`、`[udi_sn]`、`Sk22DeviceHandler` | `UdiRuntime` 直接写 logcat；`result=requested` 不是所有 UDI 功能已可用。 |

拆分每次 PID、启动和校时后的时间线。若日志只见 RN RootPage，先确认 Native 初始化日志是否被采集，再判断初始化缺口。绑定/配置未继续时读 [绑定与同步](binding-and-config-sync.md)；崩溃重启时读 [崩溃](crash-and-rn-bridge.md)。报告中掩码 SN。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 主进程装配 | `android/app/src/main/java/com/seewo/yunban/MainApplication.java#onCreate`：`PlatformBootstrap.install`、`SystemCapacityBoostrap.loadAll` |
| Activity 与 RN 就绪 | `android/app/src/main/java/com/seewo/yunban/MainActivity.java#onCreate/#onReactContextInitialized` |
| RN 请求设备数据 | `src/models/deviceModel.ts#queryDeviceMsg`、`android/app/src/main/java/com/seewo/yunban/packages/transive/YunBanRNInterface.java` |
| 启动后任务门槛 | `src/views/pages/RootPage/index.js#startSchoolScopedInitialization` |
| 机型 SN | `android/app/src/sk05/java/com/seewo/yunban/handler/DeviceHandler.java`、`android/app/src/sk06/java/com/seewo/yunban/handler/DeviceHandler.java`、`android/app/src/sk22/kotlin/com/seewo/yunban/platform/udi/UdiRuntime.kt` |

最强的切分键是 PID、进程名、一次 `MainActivity onCreate` 的 taskID、APK/JS 版本。SN 可联结设备身份，但校时或进程重启后不能仅凭相同 SN 合并两段启动。`RootPage` 的 `schoolUid`、`bindingSuccess` 与网络就绪是后续学校范围任务的条件，不是 SN 就绪的同义词。

## 具体时序和机型分叉

`MainApplication` 只在主进程装配平台接口，然后加载系统能力，完成后安装插件；`PlatformBootstrap.install` 本身不等待 UDS/UDI SDK 已就绪。`MainActivity` 创建到 `onReactContextInitialized` 又是另一阶段。`RootPage` 先等 `device/queryDeviceMsg`，然后建立连接、启动升级与训练；网络可用后会启动若干设备级任务，学校范围任务还需绑定标志与 `schoolUid`，并只执行一次。

SK05 `DeviceHandler.init` 立即释放初始化链，SN 在 `getSerialCode` 读取并缓存。SK06 可等待 OpenSDK 60 秒，走 UDS 读取或 fallback，`[capacity]` 仅表示初始化链放行。SK22 `UdiRuntime` 的 `udi_init` 和 `udi_sn` 是两条结果线；初始化请求发出不等于 SN 回调成功，且使用直接 `android.util.Log`。历史包要重查对应提交的实现。

## 实际日志指纹

| 阶段 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| Activity 生命周期 | `MainActivity` + `onCreate, [taskID:]` / `onReactContextInitialized` / `onDestroy` | 新任务、RN Context 初始化和销毁的各自时间。 |
| RN 请求 SN | `sn` + `[request] RN 请求 SN`、`[reply] RN 返回 SN` | 桥接层发起和返回；不代表后续绑定请求成功。 |
| SK05 | `sn_sk05 [init]`、`[read] SN 读取完成 source=` | 初始化放行与按需读取分开。 |
| SK06 | `sn_sk06 [wait]`、`[timeout]`、`[resolve] source=`、`[ready]`、`[capacity]` | 真实 UDS、兜底、超时及放行可分别判断。 |
| SK22 | `UdiRuntime [udi_init]`、`[udi_sn] action=request/result=` | UDI 初始化和 SN 读取阶段；确认输入是否含 logcat。 |
| 绑定信息消费 | JS Console `readBindInfo bindingInfo :` | `RootPage` 已读绑定数据并准备下发给 Uips；不证明 Uips 渲染成功。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 只见 Application/Activity | 系统能力、平台 SN 或 RN 初始化 | 同 PID 的能力加载、机型 TAG、RN 异常。 |
| SN 初始化放行但没有有效值 | 按机型查实际读取/回调 | SK05 `[read]`；SK06 `[resolve] source`；SK22 `[udi_sn]` 回调。 |
| RN 已请求 SN，未见回复 | Native getter 或 Bridge 回调 | `YunBanRNInterface` 错误、机型 SN 日志与线程。 |
| RootPage 已显示，学校数据未加载 | 网络、绑定标志、学校 ID 三项门槛 | `readBindInfo`、绑定接口、NetInfo、目标 effect 请求。 |
| 同一设备重复启动 | 崩溃、自重启、系统重建 Activity 需分开 | PID/taskID、异常栈、系统进程死亡信息。 |
