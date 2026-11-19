# 跨领域生命周期、协程与会话边界

本文件记录已覆盖领域中会改变日志判断的异步边界。代码事实基于 ab680809。它不替代各领域手册的业务状态机。

## 先区分两类工作

| 类型 | 当前实现 | 页面或同步界面离开时的判断 |
| --- | --- | --- |
| 页面工作 | OpenDoorViewModel、AttendanceViewModel、SignViewModel、SyncDataViewModel 使用 viewModelScope | ViewModel 清理时，仍在该 scope 内的鉴权、图片转换、签到、考勤写入或同步编排可能取消；不能把入口日志当成最终副作用 |
| 单例后台工作 | DoorLockReportManager、AttendanceRepositoryImpl、FaceRepositoryImpl、ConfigRepositoryImpl、SyncDataImpl、ProgramRepositoryImpl 有独立 IO scope | 不随单个页面销毁而取消；但仍可能被解绑、指定 IoT 命令、下一次强制任务或组件自身状态清理影响 |

页面回调与单例后台任务之间必须分开取证。例如开门页返回前的任务落库，不代表后台 opened 已成功；考勤页面离开后，已经写入本地的记录仍可能由 AttendanceRepositoryImpl 的后台上报循环继续发送。

## 各领域的重要边界

| 领域 | 页面侧 | 后台侧 | 诊断重点 |
| --- | --- | --- | --- |
| 门禁 | 开门鉴权和硬件调用经 OpenDoorViewModel | DoorLockReportManager 使用 SupervisorJob 和 IO scope 处理图片、轮询和 Outbox | 页面完成只证明落库调用已返回；解绑会取消任务并清空 Outbox |
| 考勤 | 人脸和 NFC 入口通过 AttendanceViewModel | AttendanceRepositoryImpl 独立 IO scope 每 3 秒扫描待上报记录 | 人脸图片与 markUserAttendance 都在页面链路内；本地记录写入后，后台上报不依赖该页面 |
| 签到 | NFC、人脸图片上传和签到接口均在 SignViewModel 的 viewModelScope | SignRepositoryImpl 的 Flow 只在调用方 collect 时运行 | 页面销毁可中断尚未完成的上传或签到；当前没有本地 Outbox 续传 |
| 人脸 | FaceControllerUseCase 随 Surface 启停相机并清除跟踪图 | FaceRepositoryImpl 使用 SupervisorJob 和 IO scope 同步人脸库 | clearFace 会取消当前同步 Job；已投递的 60 秒失败重试应以之后的同步日志确认，不能仅凭取消当前 Job 判定已停止 |
| 同步和配置 | SyncDataViewModel 串行编排同步任务与超时 | SyncDataImpl 的延时刷新、ConfigRepositoryImpl 的配置请求使用独立 IO scope | 同步页超时只说明页面已判失败；底层独立请求是否仍在，必须继续查其仓库日志 |
| 节目 | ProgramFragment 管理页面容器 | ProgramRepositoryImpl 的 IO scope 接收绑定、IoT 和 Uips 回调 | 离开节目页不等于 Uips 已停止下载或播放；应用层只能确认其回调和顶层路由 |

## 取消、超时与解绑

- ViewModel 的 onCleared 会移除考勤、签到的人脸和 NFC 监听器；因此后续没有入口回调，可能是页面不再订阅，而非算法或硬件失效。
- SyncDataViewModel 的 10 秒或 20 秒超时取消的是等待结果的页面协程。ConfigRepositoryImpl、FaceRepositoryImpl 等独立 scope 的操作可能仍继续，需用实际完成或失败日志判断。
- SyncDataImpl 在网络断开、设备解绑、收到 refreshAll 或 rebind 时取消延时刷新；这不是当前同步页已经完成的证据。
- DoorLockReportManager 的解绑清理会停止轮询、取消图片上传并删除开门任务；旧场地任务不应跨绑定继续上报。

## 排查方法

出现“页面离开后结果缺失”或“超时后又成功”的问题时：

1. 先定位工作是在页面 scope 还是单例后台 scope 创建。
2. 查明确的取消来源：onCleared、解绑、clearFace、下一次强制同步、延时刷新防抖或 Job timeout。
3. 再查持久化边界：是否已写入 Room 或 Preferences；只有可恢复的本地状态才可在后续继续处理。
4. 报告中分别写出“页面已结束”“后台任务已取消”“持久化成功”“网络副作用已确认”，不要合并成单一的成功或失败。
