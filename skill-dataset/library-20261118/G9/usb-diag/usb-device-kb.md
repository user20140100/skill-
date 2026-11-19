# MAXHUB USB 设备知识库

此文件包含 MAXHUB UC 设备的完整信息：VID/PID 映射、应用层枚举逻辑、HID 接口要求。

## 核心概念：设备枚举依赖 HID 接口

MAXHUB UC 应用**不是直接通过 USB VID/PID 枚举设备**，而是通过 WinRT DeviceWatcher 查询特定的 **HID 接口**。即使 USBTreeView 显示设备"连接正常"，如果 HID 接口不可用，应用就枚举不到设备。

### 枚举方式分类

| 方式 | 说明 | 涉及设备 |
|------|------|---------|
| **HID 接口枚举** | 查询 `GUID_DEVINTERFACE_HID`，要求特定 UsagePage/UsageId | SC802A, SC805B, SC26A, SC26B, SC29A, MU55A, MS75A, BM32, BM51D, BM52C |
| **USB 设备枚举** | 查询 `GUID_DEVCLASS_USB`，按 VID/PID 匹配 | XBoardV7, MS07A, MS10E, MU08A, DT10PB, DT10PC |
| **Video 接口枚举** | 查询 `KSCATEGORY_VIDEO_CAMERA`，按 VID/PID 匹配 | SC25A |

### HID UsagePage 常量

| UsagePage | 用途 | 使用者 |
|-----------|------|--------|
| `0xFF00` | UVC 控制 HID（摄像头控制） | UuidBar, WebCamera, XBoardV7, MxxxxBar, Dt10xx |
| `0xFF01` | UVC 文件 HID（固件升级文件传输） | 同上 |
| `0xFF02` | PTZ 摄像头控制 HID | PtzCamera (SC802A, SC805B) |
| `0xFFA0` | HDMI 桥接 HID | Dt10xx (HDMI 子设备) |

---

## 设备型号完整信息

### SC802A — MAXHUB UC P30（PTZ 摄像头）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0523` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `PtzCameraDeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0523` |
| HID UsagePage | `0xFF02` |
| HID UsageId | `0x01` |
| 接口类 GUID | `GUID_DEVINTERFACE_HID` (`4D1E55B2-F16F-11CF-88CB-001111000030`) |

**枚举条件**：设备必须暴露 HID 接口，InstanceId 以 `HID\VID_1FF7&PID_0523` 开头，且 HID UsagePage=0xFF02, UsageId=0x01。

**枚举失败原因排查**：
- 配置描述符中缺少 `bInterfaceClass = 0x03` (HID) 的接口 → **Error：HID 接口不存在**
- 设备描述符 `bDeviceClass` 不是 `0xEF` (Miscellaneous/Composite) → 可能驱动异常
- `Class` 字段不是 `HIDClass` → HID 驱动未加载
- `Device Description` 显示为通用名称而非设备名称 → 驱动可能不完整

---

### SC805B — ViewSonic UMC211T（PTZ 摄像头）

| 项目 | 值 |
|------|-----|
| VID:PID | `0543:A040` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `PtzCameraDeviceService` |
| HID InstanceId 前缀 | `HID\VID_0543&PID_A040` |
| HID UsagePage | `0xFF02` |
| HID UsageId | `0x01` |

同 SC802A，枚举条件和失败排查完全一致。

---

### MU55A — MAXHUB XBar U50（视频会议 Bar）

| PID | 功能 | VID |
|-----|------|-----|
| `0516` | 摄像头（Camera） | `1FF7` |
| `0479` | 音频（Audio） | `1FF7` |

**摄像头接口 (PID 0516) 枚举方式**：**HID 接口枚举**
- 枚举服务：`UuidBarDeviceService`
- HID InstanceId 前缀：`HID\VID_1FF7&PID_0516`
- HID UsagePage：`0xFF00` (UVC 控制)
- 接口类 GUID：`GUID_DEVINTERFACE_HID`

**音频接口 (PID 0479) 枚举方式**：**HID 接口枚举**
- HID InstanceId 前缀：`HID\VID_1FF7&PID_0479&MI_00&COL01`（注意 `&MI_00&COL01` 后缀）
- 不要求特定 UsagePage，但要求 InstanceId 包含 `&MI_00&COL01`（第一个 HID Collection）

**复合设备完整性**：Camera PID + Audio PID 必须同时出现在拓扑中。

---

### MS75A — MAXHUB XBar W70（视频会议 Bar）

| PID | 功能 | VID |
|-----|------|-----|
| `0513` | 摄像头（Camera） | `1FF7` |
| `0476` | 音频（Audio） | `1FF7` |

**摄像头接口 (PID 0513)**：
- 枚举服务：`UuidBarDeviceService`
- HID InstanceId 前缀：`HID\VID_1FF7&PID_0513`
- HID UsagePage：`0xFF00`

**音频接口 (PID 0476)**：
- HID InstanceId 前缀：`HID\VID_1FF7&PID_0476&MI_00&COL01`

同 MU55A 模式。

---

### MS76A — Q-SYS MS76A

| PID | 功能 | VID |
|-----|------|-----|
| `001B` | 摄像头（Camera） | `1656` |
| `001C` | 音频（Audio） | `1656` |

**摄像头接口**：HID InstanceId 前缀 `HID\VID_1656&PID_001B`，UsagePage `0xFF00`
**音频接口**：HID InstanceId 前缀 `HID\VID_1656&PID_001C&MI_00&COL01`

---

### XBoard V7 — MAXHUB 大屏 IFP

| PID | 功能 | VID |
|-----|------|-----|
| `0470` | 音频（Audio） | `1FF7` |
| `0526`/`0527`/`052A`/`052B`/`052C`/`052F` | 摄像头（Camera，多版本） | `1FF7` |

**枚举方式**：**USB 设备枚举**（通过 `GUID_DEVCLASS_USB`）
- 枚举服务：`XBoardV7DeviceService`
- 查询 `USB\VID_1FF7&PID_xxxx` 前缀匹配
- 枚举到 USB 设备后，再通过 ContainerID 解析 HID 子设备：
  - Camera HID：UsagePage `0xFF00` + `0xFF01`
  - Audio UAC Ctrl HID：`HID\VID_1FF7&PID_xxxx&MI_00&COL01`
  - Audio UAC Tool HID：`HID\VID_1FF7&PID_xxxx&MI_01`

**注意**：XBoardV7 使用 USB 设备枚举而非直接 HID 枚举，因此 USB 层面问题（Problem Code、驱动缺失）会直接导致枚举失败。但 HID 子设备解析失败也会导致功能不可用。

---

### MS07A — MAXHUB UC S07（Soundbar）

| PID | 功能 | VID |
|-----|------|-----|
| `040E` | 音频（Audio） | `1FF7` |
| `051F` | 摄像头（Camera） | `1FF7` |

**枚举方式**：**USB 设备枚举**（通过 `GUID_DEVCLASS_USB`）
- 枚举服务：`MxxxxBarDeviceService`
- 后续 HID 解析同 XBoardV7 模式

---

### MS10E — MAXHUB UC S15（Soundbar）

| PID | 功能 | VID |
|-----|------|-----|
| `0408` | 音频（Audio） | `1FF7` |
| `051E` | 摄像头（Camera） | `1FF7` |

**枚举方式**：**USB 设备枚举**（通过 `MxxxxBarDeviceService`）

---

### MU08A — ViewSonic UMB202 Concam（Soundbar）

| PID | 功能 | VID |
|-----|------|-----|
| `A032` | 音频（Audio） | `0543` |
| `A033` | 摄像头（Camera） | `0543` |

**枚举方式**：**USB 设备枚举**（通过 `MxxxxBarDeviceService`）

---

### SC26A — MAXHUB UC W20（WebCamera）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0509` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `WebCameraDeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0509` |
| HID UsagePage | `0xFF00` (UVC 控制) |

---

### SC26B — MAXHUB UC W21（WebCamera）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0507` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `WebCameraDeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0507` |
| HID UsagePage | `0xFF00` |

---

### SC29A — MAXHUB UC W31（WebCamera）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0511` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `WebCameraDeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0511` |
| HID UsagePage | `0xFF00` |

---

### SC25A — MAXHUB UC M31（WebCamera）

| PID | VID | 说明 |
|-----|-----|------|
| `0506` | `1FF7` | 标准版 |
| `1221` | `2245` | 升级版（不同 VID） |

**枚举方式**：**Video 接口枚举**（通过 `KSCATEGORY_VIDEO_CAMERA`）
- 枚举服务：`Sc25aDeviceService`
- 查询的是视频摄像头接口，不是 HID 接口
- 使用 USB Extension Unit (XU) 而非 HID 通信
- InstanceId 前缀：`USB\VID_1FF7&PID_0506` 或 `USB\VID_2245&PID_1221`

**注意**：SC25A 是唯一使用 Video 接口枚举的设备，不依赖 HID。如果摄像头在系统中能显示画面，通常枚举就没问题。

---

### BM32 — MAXHUB UC BM35（SpeakerPhone）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:040F` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `SpeakerPhoneDeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_040F&MI_01` |
| 不要求 UsagePage | — |

**关键**：InstanceId 必须包含 `&MI_01`（第二个 USB 接口的 HID 工具通道）。

---

### BM51D — MAXHUB UC BM45（SpeakerPhone）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0455` |
| 枚举方式 | **HID 接口枚举** |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0455&MI_01` |

---

### BM52C — ViewSonic UMS301T（SpeakerPhone）

| 项目 | 值 |
|------|-----|
| VID:PID | `0543:A041` |
| 枚举方式 | **HID 接口枚举** |
| HID InstanceId 前缀 | `HID\VID_0543&PID_A041&MI_01` |

---

### DT10PB — TCP20T（触控屏/会控）

| PID | 功能 | VID |
|-----|------|-----|
| `0F6A` | MCU 控制 | `1FF7` |
| `0FF6` | HDMI 桥接 | `1FF7` |

**枚举方式**：**USB 设备枚举**（通过 `GUID_DEVCLASS_USB`）
- 枚举服务：`Dt10xxDeviceService`
- 后续 HID 解析：
  - MCU HID：UsagePage `0xFF00`, UsageId `0x0000`
  - HDMI HID：UsagePage `0xFFA0`, UsageId `0x0001`

---

### DT10PC — ViewSonic MRC1010（会控）

| PID | 功能 | VID |
|-----|------|-----|
| `A031` | MCU 控制 | `0543` |
| `A030` | HDMI 桥接 | `0543` |

**枚举方式**：**USB 设备枚举**（通过 `Dt10xxDeviceService`）
- 后续 HID 解析同 DT10PB

---

### DT12PA — TCP30T（会控屏）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0F75` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `Rv1126DeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0F75&MI_01` |
| HID UsagePage | `0xFF75` |
| HID UsageId | `0x0001` |
| 接口类 GUID | `GUID_DEVINTERFACE_HID` |

---

### DT12PC — TCP33T（会控屏）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0F83` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `Rv1126DeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0F83&MI_01` |
| HID UsagePage | `0xFF75` |
| HID UsageId | `0x0001` |

---

### DT12PD — TCP31T（会控屏）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0F84` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `Rv1126DeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0F84&MI_01` |
| HID UsagePage | `0xFF75` |
| HID UsageId | `0x0001` |

---

### DT12PE — ViewSonic MRC111T（会控屏）

| 项目 | 值 |
|------|-----|
| VID:PID | `0543:A038` |
| 枚举方式 | **HID 接口枚举** |
| 枚举服务 | `Rv1126DeviceService` |
| HID InstanceId 前缀 | `HID\VID_0543&PID_A038&MI_01` |
| HID UsagePage | `0xFF75` |
| HID UsageId | `0x0001` |

---

### AC21B — MAXHUB UC AC21B（SpeakerPhone）

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:0601` |
| 枚举方式 | **USB 设备枚举** |
| 枚举服务 | `AC21DeviceService` |
| 查询条件 | `GUID_DEVCLASS_USB` + `USB\VID_1FF7&PID_0601` |
| InstanceId 前缀 | `USB\VID_1FF7&PID_0601` |

**注意**：AC21B 通过 USB 设备枚举，后续 HID 解析逻辑与 SpeakerPhone 类似。

---

### MC33C — MAXHUB DM30（扩展麦克风）

| 项目 | 值 |
|------|-----|
| 宿主设备 | MU55A Audio (`1FF7:0479`) |
| 枚举方式 | **HID 接口枚举**（通过宿主设备发现） |
| 枚举服务 | `MC33CDeviceService` |
| HID InstanceId 前缀 | `HID\VID_1FF7&PID_0479&MI_00&COL01`（复用 MU55A Audio 的 HID） |

**特殊逻辑**：MC33C 不直接枚举，而是通过 MU55A 的音频 HID 接口轮询发现扩展麦克风。MC33C 的前提是 MU55A Audio (PID 0479) 已正常枚举。

---

### XBoard V7 BYOD — V7 Touch out

| 项目 | 值 |
|------|-----|
| VID:PID | `1FF7:052E` |
| 枚举方式 | 无独立枚举（作为 XBoard V7 的附属模式识别） |

---

## 快速查找表（VID:PID → 型号 + 枚举信息）

```
# 格式：VID:PID → 型号 (枚举方式 | HID要求)

# === HID 接口枚举 ===
1FF7:0523 → SC802A  (HID枚举 | UsagePage=0xFF02, UsageId=0x01)
0543:A040 → SC805B  (HID枚举 | UsagePage=0xFF02, UsageId=0x01)
1FF7:0516 → MU55A Camera  (HID枚举 | UsagePage=0xFF00)
1FF7:0479 → MU55A Audio   (HID枚举 | &MI_00&COL01)
1FF7:0513 → MS75A Camera  (HID枚举 | UsagePage=0xFF00)
1FF7:0476 → MS75A Audio   (HID枚举 | &MI_00&COL01)
1656:001B → MS76A Camera  (HID枚举 | UsagePage=0xFF00)
1656:001C → MS76A Audio   (HID枚举 | &MI_00&COL01)
1FF7:0509 → SC26A  (HID枚举 | UsagePage=0xFF00)
1FF7:0507 → SC26B  (HID枚举 | UsagePage=0xFF00)
1FF7:0511 → SC29A  (HID枚举 | UsagePage=0xFF00)
1FF7:040F → BM32   (HID枚举 | &MI_01)
1FF7:0455 → BM51D  (HID枚举 | &MI_01)
0543:A041 → BM52C  (HID枚举 | &MI_01)

# === USB 设备枚举 ===
1FF7:0470 → XBoardV7 Audio     (USB枚举 | 后续解析HID)
1FF7:0526 → XBoardV7 Camera   (USB枚举)
1FF7:0527 → XBoardV7 Camera   (USB枚举)
1FF7:052A → XBoardV7 Camera   (USB枚举)
1FF7:052B → XBoardV7 Camera   (USB枚举)
1FF7:052C → XBoardV7 Camera   (USB枚举)
1FF7:052F → XBoardV7 Camera   (USB枚举)
1FF7:040E → MS07A Audio   (USB枚举)
1FF7:051F → MS07A Camera  (USB枚举)
1FF7:0408 → MS10E Audio   (USB枚举)
1FF7:051E → MS10E Camera  (USB枚举)
0543:A032 → MU08A Audio   (USB枚举)
0543:A033 → MU08A Camera  (USB枚举)
1FF7:0F6A → DT10PB MCU    (USB枚举 | HID UsagePage=0xFF00)
1FF7:0FF6 → DT10PB HDMI   (USB枚举 | HID UsagePage=0xFFA0)
0543:A031 → DT10PC MCU    (USB枚举)
0543:A030 → DT10PC HDMI   (USB枚举)

# === Video 接口枚举 ===
1FF7:0506 → SC25A      (Video枚举 | KSCATEGORY_VIDEO_CAMERA)
2245:1221 → SC25A 升级版 (Video枚举)

# === HID 枚举（会控屏 Rv1126）===
1FF7:0F75 → DT12PA (HID枚举 | UsagePage=0xFF75, &MI_01)
1FF7:0F83 → DT12PC (HID枚举 | UsagePage=0xFF75, &MI_01)
1FF7:0F84 → DT12PD (HID枚举 | UsagePage=0xFF75, &MI_01)
0543:A038 → DT12PE (HID枚举 | UsagePage=0xFF75, &MI_01)

# === USB 枚举（AC21B）===
1FF7:0601 → AC21B  (USB枚举)

# === 特殊（MC33C 通过宿主 MU55A 发现）===
# MC33C 无独立 VID/PID，通过 MU55A Audio (1FF7:0479) 的 HID 轮询发现

# === 其他 ===
1FF7:052E → XBoardV7_BYOD
```

## 复合设备完整性检查规则

| 型号 | 必需接口 | 判定 |
|------|---------|------|
| MU55A | Camera PID 0516 + Audio PID 0479 | 两者都出现=完整 |
| MS75A | Camera PID 0513 + Audio PID 0476 | 两者都出现=完整 |
| MS76A | Camera PID 001B + Audio PID 001C | 两者都出现=完整 |
| XBoard V7 | 任意 Camera PID + Audio PID 0470 | 两者都出现=完整 |
| MS07A | Camera PID 051F + Audio PID 040E | 两者都出现=完整 |
| MS10E | Camera PID 051E + Audio PID 0408 | 两者都出现=完整 |
| MU08A | Camera PID A033 + Audio PID A032 | 两者都出现=完整 |
