# 外设与串口

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理身份证读卡器、考勤串口、家校电话硬件连接与事件丢失。入口：`android/app/src/main/java/com/seewo/yunban/packages/idcard/service/IdCardService.java`、`android/app/src/main/java/com/seewo/yunban/packages/attendance/SerialPortService.java`、`android/app/src/main/java/com/seewo/yunban/packages/phone/service/PortService.java`。

身份证读卡：`USB VID/PID 检测 → 权限广播 → IDCardController.onReceive → IDCardService.send → RN 事件`。`IDCardService#send` 直接写 `android.util.Log` 并且仅在 context 为 `ReactContext` 时发送 RN 事件；“读卡成功”不等于 JS 收到。原始日志可能带身份证号码，不要在报告中复述。

考勤串口：`USB/串口候选 → SerialPortService.connect → 数据接收 → AttendanceController 解析/状态门槛 → 业务事件`。搜 `Attendance#SerialPort` 的 `serial connect`、`openSerialPort`、`send error`；同类日志有 XLog 和直接 Log，两种输入可能覆盖不同。连上串口不证明收到有效卡片，收到字节也不证明业务启用。

电话外设另查 `PhoneId#Controller`、`PhoneId#SerialPort`，业务语义见 [通话](family-calling-and-voice.md)；考勤见 [考勤](attendance.md)。先分清物理设备、权限、串口协议、RN 事件和业务结果五层。

## 代码定位与关联键

| 外设 | 源码与符号 |
| --- | --- |
| 身份证 USB 权限与事件 | `android/app/src/main/java/com/seewo/yunban/packages/idcard/service/IdCardService.java#requestDevicePermission/#send` |
| 身份证读卡线程 | `android/app/src/main/java/com/seewo/yunban/packages/idcard/IDCardController.java#start/#onReceive/#read` |
| 考勤串口 | `android/app/src/main/java/com/seewo/yunban/packages/attendance/SerialPortService.java#connect/#openSerialPort` |
| 考勤协议与门槛 | `android/app/src/main/java/com/seewo/yunban/packages/attendance/AttendanceController.java#onDataReceive` |
| 电话串口 | `android/app/src/main/java/com/seewo/yunban/packages/phone/service/PortService.java` |

USB VID/PID、权限广播、串口路径和一次连接生命周期用于区分物理设备；脱敏证件号/卡号只在本地关联一次读取。电话与考勤可都用串口，但协议、TAG 和 RN 事件不同。设备序列号相同不等于两次读卡属于同一事件。

## 设备边界和日志通道

身份证服务先枚举匹配的 VID/PID 并申请 USB 权限；授权广播才启动 `IDCardController.onReceive`，读卡线程以 500 ms 周期寻找卡并读取。`IdCardService.send` 先设置人脸卡证照片，再直接 `android.util.Log` 打证件号；只有 context 为 `ReactContext` 才向 RN 发事件。此日志极敏感，分析时仅保留“出现与否”和掩码。

考勤串口可先查 USB 设备或回退串口路径；连接成功、线程收到字节、`Gdm2mPort.getCards` 解析、`AttendanceController.status=true` 和 `AttendanceUtils.sendCode` 是五个节点。电话串口 `PortService` 有独立连接、写入与读线程，后续 AT 协议见 [通话](family-calling-and-voice.md)。直接 Log 与 XLog 分开采集，缺少其中一种通道就不能用空白否定对应步骤。

## 实际日志指纹

| 外设/节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 身份证 | logcat `IDCardController#start/#onReceive/#end` | 读卡线程生命周期入口；不证明已读到证件。 |
| 身份证发送 | logcat `IDCardController#send, model:` | 读到模型并进发送函数；不能证明 RN 接收。 |
| 考勤串口 | XLog `Attendance#SerialPort serial connect succeed/failed` / `openSerialPort:` | 串口打开分支。 |
| 考勤卡 | XLog `AttendanceController` + `,status:` | 有解析卡集合且报告当前业务门槛。 |
| 电话串口 | logcat `PhoneId#SerialPort Phone serial connect succeed:` / `Phone serial can't connect` | 端口连接结果；不能证明通话建立。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 找到 USB 却无权限广播 | 系统授权/接收器 | USB 权限状态、系统 logcat。 |
| 身份证 `onReceive` 后无 `send` | SDK 读卡或模型转换 | 读卡器异常、卡片状态。 |
| `send` 出现但 JS 无事件 | ReactContext 或 RN listener | 事件订阅、Bridge 状态。 |
| 考勤串口已连但无有效卡 | 读线程、协议解析 | 脱敏原始字节、设备型号。 |
| 卡有而业务无 | `status` 门槛或后续 RN | [考勤](attendance.md) 的事件、人员与接口。 |
