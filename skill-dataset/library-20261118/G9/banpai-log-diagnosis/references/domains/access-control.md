# 门禁与开门事件上报

## 边界

本手册覆盖开门页刷卡、扫码、人脸识别，首页 NFC 刷卡，考勤联动开门，以及 IoT 下发开门后对 opened 事件的客户端处理。代码事实基于 ab680809。

门锁实际电气动作、服务端事件入库、后台查询权限和人脸算法识别率不在客户端日志可单独确认的范围。

## 代码定位与关联键

下列源码路径均相对 app/src/main/java/com/seewo/yunban。

| 目的 | 路径与关键符号 |
| --- | --- |
| 开门页入口与页面状态 | ui/opendoor/OpenDoorViewModel.kt：checkOpenDoorAuth、onFaceDetected、enqueueOpenDoorReport |
| 鉴权与入队适配 | data/remote/doorlock/DoorLockRepositoryImpl.kt：checkOpenDoorAuth、enqueueOpenDoorReport |
| Outbox、图片与上报 | data/remote/doorlock/DoorLockReportManager.kt：enqueueOpenDoorReport、uploadFaceImage、reportTask |
| 本地任务读写 | data/local/store/doorlock/OpenDoorReportTaskLocalStore.kt |
| 硬件与 IoT 开门 | infrastructure/doorlock/DoorLockManager.kt、infrastructure/nfc/NfcAuthManager.kt |
| 考勤联动入口与 HTTP 定义 | usecase/attendance/AttendanceExtensionUseCase.kt、data/remote/api/IDoorLockApi.kt |

| 关联强度 | 键与使用限制 |
| --- | --- |
| 最强 | taskId：仅存在于本地任务与 DoorLockReportManager 日志，不在 opened 请求体中 |
| IoT 入口 | eventId：只适用于 IoT 下发开门，不能替代 taskId |
| 次强 | 脱敏 userCode、snCode、authType、status 与窄时间窗的组合 |
| 弱关联 | HTTP 请求：请求体不含 taskId；并发开门时不能仅按同一秒请求认定归属 |

## 期望链路

    刷卡 / 扫码 / 人脸帧
      -> OpenDoorViewModel 鉴权
      -> DoorLockRepositoryImpl.checkOpenDoorAuth
      -> POST /access/control/auth/v1
      -> DoorLockManager.openDoor
      -> 硬件 onComplete 或 onError
      -> DoorLockReportManager 入队并写入 open_door_report_tasks
      -> 可选：上传人脸图片并回填 faceFileKey
      -> 每 3 秒扫描就绪任务
      -> POST /access/control/event/v1/opened
      -> 业务成功后删除任务

开门页在任务落库返回后才更新开门成功状态；它不等待图片上传或 opened 事件上报。鉴权日志前缀 FACE_DOOR_AUTH 当前也用于刷卡和扫码，必须结合 authType 和入口日志判断来源。

IoT accessControlAuthed 在 DoorLockManager 的 onComplete 中以 authType=5 入队；当前 onError 仅记录失败，不会创建上报任务。开门状态值 1、2、3 分别为成功、失败、无硬件回传的未知结果；3 不等同于开门失败。

## HTTP 成功边界

开门鉴权由 DoorLockRepositoryImpl.checkOpenDoorAuth 调用 POST /access/control/auth/v1，并使用 onCommonResponse：除 HTTP 成功外，业务码必须在 200 至 299 且 data 非空才进入鉴权成功分支。

开门事件由 DoorLockReportManager.reportTask 调用 POST /access/control/event/v1/opened，并使用 onOptionalCommonResponse：业务码在 200 至 299 即可进入成功分支，data 可为空；此时才删除对应 taskId 的本地任务。请求体不含 taskId，因此 HTTP 日志和 Outbox 只能由时间窗关联。

读取 [网络、响应语义与 CStore](../shared/network-and-api.md) 核对请求被拦截、HTTP 日志覆盖和图片文件语义；不要把图片上传成功或 HTTP 200 单独等同于 opened 已完成。

## 关键证据

| 节点 | 搜索文本或 TAG | 出现时确认的事实 |
| --- | --- | --- |
| 鉴权跳过 | DoorLockRepositoryImpl + request skipped / missing_bind_info | 因未绑定跳过鉴权请求 |
| 鉴权结果 | FACE_DOOR_AUTH + response success / response error / transport failure | 客户端收到了对应鉴权结果 |
| 硬件结果 | OpenDoorViewModel + 认证开门 + onComplete | 已进入硬件完成回调；继续看 isSuccess 与 hasCallBack |
| 任务落库 | DoorLockReportManager + 任务已落库 task= | 该 taskId 已写入本地 Outbox |
| 图片处理 | uploadFaceImage + 开始上传 / 图片上传成功 / 图片上传失败 | 该任务的人脸图片处理结果；图片失败会降级 |
| 上报尝试 | reportTask + 开始上报 task= | Manager 正在尝试发送该任务 |
| 客户端完成 | 上报成功并删除任务 task= | 客户端收到 opened 业务成功并删除本地任务 |
| 保留重试 | 上报失败，保留任务等待下轮重试 / 请求异常，保留任务 | 客户端未确认成功，任务仍可重试 |

首次检索可使用：

    DoorLockReportManager|FACE_DOOR_AUTH|OpenDoorViewModel|accessControlAuthed|opened

随后用 taskId 收窄。opened 请求体不包含 taskId，HTTP 与任务只能依时间窗关联，除非同一时刻仅有一条任务。

## 断点判断

| 最晚可见节点 | 最早可确认断点 | 最小补证 |
| --- | --- | --- |
| 有入口，无鉴权请求 | 入口到绑定或鉴权 | 未绑定日志、authType、网络状态 |
| 鉴权成功，无硬件回调 | 开门调用或硬件路径 | requestLockOpen、门锁协议、UDS/蓝牙日志 |
| 硬件回调，无任务落库 | 回调到入队 | userCode、绑定信息、Manager session、Room 写入 |
| 已落库，无开始上报 | Manager 选择或扫描 | init、reportPendingTasks、上传标记、解绑、日志覆盖 |
| 已开始上报，无成功删任务 | 网络或业务响应 | HTTP 响应、业务码、请求异常、当前 session |
| 已成功删任务，后台无数据 | 客户端链路已完成 | 后端按时间、设备和脱敏用户条件查落库与查询可见性 |

读取 [持久化与重试](../shared/persistence-and-retry.md)、[网络与 CStore](../shared/network-and-api.md)、[设备与 IoT](../shared/device-and-iot.md) 以核对异步边界。不要用图片上传结果代替 opened 事件结果。
