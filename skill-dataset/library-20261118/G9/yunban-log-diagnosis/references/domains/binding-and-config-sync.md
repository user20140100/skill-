# 绑定与配置同步

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理设备未绑定、学校/班级配置不生效、启动刷新后页面仍旧。入口：`src/views/pages/RootPage/index.js#readBindInfo`、`src/models/userModel.ts`、`src/models/deviceModel.ts#queryDeviceMsg`、`src/views/container/LoadData/LoadDataTasks/otherTask.js`。

## 排查链

`SN 就绪 → 本地绑定信息读取 → user.bindingSuccess / schoolUid / roomUid → 网络可用 → 数据加载任务 → 各 model/reducer → 页面或 Native 能力`。`RootPage` 的后续任务受网络、绑定成功及学校 ID 共同约束；某个请求未发生时先查前置条件。`src/push/handlers/devicePush.js` 的解绑指令和 `android/app/src/main/java/com/seewo/yunban/plugins/iot/handler/event/IotConfigsHandler.java` 的配置指令是另一入口，不要和启动同步自动合并。

检索 `RootPage`、`readBindInfo`、`devicePush`、`IotConfigsHandler`、相关 model 的 effect 名称；这些是搜索种子，只有源码中真正输出的文本才算日志指纹。按设备 SN、学校/班级 ID 和推送事件时间分段，输出时脱敏。一个 model 更新成功不代表其他配置或 Native 硬件侧已经生效。

若入口是认证失败读 [鉴权](auth-and-permissions.md)；若 IoT 指令未达读 [IoT/推送](iot-and-push.md)；若只见服务端响应而页面未变，读 [存储与缓存](../shared/storage-and-cache.md)。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 设备信息与绑定状态 | `src/models/userModel.ts#queryDeviceInfo/#postDeviceBinding`、`src/models/deviceModel.ts#queryDeviceMsg` |
| 启动恢复/下发 Uips | `src/views/pages/RootPage/index.js#startSchoolScopedInitialization/#readBindInfo` |
| 手动全量刷新 | `src/views/pages/RootPage/container/UpdateAllDataModal.tsx`、`src/views/container/LoadData/LoadDataTasks/otherTask.js` |
| 远程解绑与计划刷新 | `src/push/handlers/devicePush.js`：`systemCmd-unbind`、`systemCmd-updateDevicePowerPlan` |
| Native 配置命令 | `android/app/src/main/java/com/seewo/yunban/plugins/iot/handler/event/IotConfigsHandler.java#run` |

用脱敏 SN、`schoolUid`、`roomUid`、`classUid`、绑定/解绑指令时间和一次刷新窗口关联。`IotConfigsHandler` 收到 `thing.service.configUpload` 后新建本地 `eventId` 并转 EventBus；该 `eventId` 不应和服务端 `traceId` 自动视为同一键。学校 ID 相同也不能把两次手动刷新合为一次。

## 绑定、刷新和解绑的不同链

`user/queryDeviceInfo → setBindingRoom → 检查 data.schoolUid → setBindingSuccess 或 setBindingFail → 备份保存/清理`。`postDeviceBinding` 成功后会更新绑定房间、同步 Uips Webpage 数据、触发课表查询和保存楼栋信息；这些是分离的后续动作。`RootPage` 即使网络就绪，也要 `bindingSuccess && schoolUid` 才执行学校范围初始化；其中下发 Uips 绑定信息、查询应用列表、上传设备信息等互不等价。

`systemCmd-unbind` 先取消电源计划，再清绑定备份、`RESET_ALL`、跳起始页并清持久化、人脸、学生、节目缓存。日志 `systemCmd-unbind:resetAll` 在前段，`systemCmd-unbind:clearStudent` 在后段；前者不能证明所有清理都结束。配置上传 `IotConfigsHandler` 只是转发要求，具体配置应用还要追相应消费者。手动刷新与启动自动初始化不是一条任务线。

## 实际日志指纹与缺口

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 本地绑定消费 | JS Console `readBindInfo bindingInfo :` | RootPage 读到当前 Redux 绑定信息；不证明服务端仍保持同一绑定。 |
| Native 配置指令 | `IotConfigsHandler` 输出的参数 | 收到 `configUpload` 并转发；参数可能敏感，报告只摘键名。 |
| 解绑前段 | `devicePush` + `systemCmd-unbind:resetAll` | Redux 重置动作之后，后续清理尚未全部证实。 |
| 解绑后段/异常 | `systemCmd-unbind:clearStudent` / `systemCmd-unbind:Error` | 学生存储清理到达或捕获异常。 |

`queryDeviceInfo`、`setBindingSuccess`、`LoadDataTasks` 是源码符号，不能当作保证落盘的日志。缺少 JS Console 或 HTTP 时，只能说明当前输入无法观察绑定查询。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 有 SN 无绑定查询 | RootPage/Blank 时序、网络与请求覆盖 | 同 PID 的 RN 启动、网络状态、接口记录。 |
| 绑定接口有响应，`schoolUid` 空 | `queryDeviceInfo` 会标记解绑并清备份 | 返回的脱敏学校字段、旧备份状态。 |
| `bindingSuccess=true` 但学校任务未发起 | `networkReady` 或 `hasStarted` 条件 | RootPage 生命周期、网络回调、当前 `schoolUid`。 |
| 某配置请求完成但页面/硬件旧值 | model 写入到消费者之间 | 对应 reducer、缓存版本、Native Adapter 结果。 |
| 已见 `resetAll`，仍有旧数据 | 解绑后段缓存清理或再次同步 | `clearStudent`、人脸/Uips 清理结果、新绑定事件。 |
