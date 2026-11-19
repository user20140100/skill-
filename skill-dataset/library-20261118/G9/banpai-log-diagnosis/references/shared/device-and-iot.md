# 设备、门锁与 IoT 开门

本文件描述开门的硬件和 IoT 入口，代码事实基于 `ab680809`。

## 枚举语义

| 字段 | 值 | 含义 |
| --- | --- | --- |
| `authType` | 1 / 2 / 3 / 4 / 5 | 刷卡 / 扫码 / 人脸 / 离线 / IoT |
| `status` | 1 / 2 / 3 | 已确认开门成功 / 开门失败 / 指令已发出但无状态回传 |

`OPEN_UNKNOWN=3` 不表示开门失败；它表示当前硬件协议没有回传最终开门状态。分析后台事件时要保留这层语义。

## IoT 下发开门

`DoorLockManager` 注册 `accessControlAuthed` 命令。收到指令后，它从消息中读取首个卡号、`userUid` 和 `eventId`，调用硬件开门，并在 `onComplete` 中通过 `DoorLockRepositoryImpl.enqueueOpenDoorReport()` 创建 `authType=5` 的任务。

可搜索的主要日志为：

```text
lock_door_lock_manager | IOT | accessControlAuthed | 开门中...
lock_door_lock_manager | IOT | accessControlAuthed | 开门结果：..., 是否回传：...
```

当前 `onError` 仅记录 `IOT | accessControlAuthed | 开门失败：...`，没有调用入队接口。若日志命中这一分支，不能期待后续存在 `DoorLockReportManager` 任务；这是当前代码路径的事实，不是日志缺失。

## 硬件开门边界

`DoorLockManager.openDoor()` 先读取本地门锁配置。若 `hasAccessLock != true`，会记录“非法调用，本地没有锁配置”，同时调用错误和完成回调。IO、韦根和蓝牙协议各自具有不同的硬件完成语义：

- IO：是否有回传由 `enableAccessLockCallBack` 决定。
- 韦根：用户鉴权场景缺卡号会记录 `cardNumber 为空，取消调用 UDS`，不会下发底层命令。
- 蓝牙：日志会记录发送、等待状态更新、超时或失败；其 `onComplete` 的成功值才是开门上报状态的输入。

硬件回调成功只证明应用收到的开门结果，不等同于后台 `opened` 事件已上报。必须继续关联 `DoorLockReportManager` 的入队和上报日志。
