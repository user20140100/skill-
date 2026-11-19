# USB 诊断规则库

## 规则概述

分两层诊断：
1. **USB 层诊断**（规则 1-10）：检查物理连接、驱动、电源等基础问题
2. **应用层诊断**（规则 11-13）：检查 MAXHUB UC 应用能否成功枚举设备（**最关键**）

---

# 第一部分：USB 层诊断

## 规则 1：设备识别

**严重性**：Info

- 提取 VID/PID，对照 `usb-device-kb.md` 快速查找表
- 标注型号名称、枚举方式（HID枚举/USB枚举/Video枚举）

## 规则 2：连接状态

**严重性**：—

- `Connection Status : 0x01` = 已连接（正常）
- `Connection Status : 0x00` = 空端口（跳过）
- `Connection Status : 0x02` = 设备枚举失败（**Error**）

## 规则 3：Problem Code

**严重性**：Error

- `Problem Code : 0` = 正常
- 非零 = 有问题，对照下表：

| Code | 含义 | 建议 |
|------|------|------|
| 10 | 设备未启动 | 重新安装驱动 |
| 14 | 需要重启 | 重启计算机 |
| 18 | 需要重新安装 | 设备管理器卸载后重新插拔 |
| 22 | 设备被禁用 | 设备管理器中启用 |
| 28 | 未安装驱动 | 安装驱动程序 |
| 43 | 设备启动后失败 | 可能固件问题 |

## 规则 4：USB 连接速度

**严重性**：Warning

- USB 3.0 设备接在 USB 2.0 端口 = **Warning**（降速）
- 建议：插到 USB 3.0 端口（通常为蓝色）

## 规则 5：供电检查

**严重性**：Warning

- 高功耗设备（>500mA）接在总线供电 Hub 上 = **Warning**
- 建议：使用带独立电源的 Hub 或直连主机

## 规则 6：Hub 级联深度

**严重性**：Warning

- Port Chain 中 `-` 数量 ≥ 3 = **Warning**（经 2+ 级 Hub，信号衰减）
- 建议：直连主机端口

## 规则 7：驱动状态

**严重性**：Error

- `Status` 缺少 `DN_STARTED` 或 `DN_DRIVER_LOADED` = **Error**

## 规则 8：复合设备完整性

**严重性**：Warning

- 同一型号的 Camera PID + Audio PID 是否都出现在拓扑中
- 详见 `usb-device-kb.md` 复合设备完整性检查规则

## 规则 9：电源管理

**严重性**：Warning

- `EnhancedPowerMgmtEnabled = 1` = 可能导致意外断开
- 建议：禁用 USB 选择性暂停

## 规则 10：Host Controller 状态

**严重性**：Warning

- Power State 非 D0 或 HardResetCount 非零 = **Warning**

---

# 第二部分：应用层诊断（MAXHUB UC 应用枚举检查）

> **这是最关键的部分**。USB 层正常不代表应用能枚举到设备。应用依赖特定的 HID 接口、UsagePage、InstanceId 格式等条件。

## 规则 11：HID 接口可用性检查

**检查对象**：所有通过「HID 接口枚举」方式识别的 MAXHUB 设备
**严重性**：Error

对每个 HID 枚举设备，检查以下条件：

### 检查项 11a：配置描述符中是否有 HID 接口

在 XML 的 Configuration Descriptor 区域查找 `bInterfaceClass`：
- 必须存在 `bInterfaceClass : 0x03` (HID) 的接口
- 如果**没有 HID 接口** = **Error：设备未暴露 HID 接口，应用无法枚举**
  - 可能原因：驱动未正确安装，设备使用了通用 USB 驱动而非 HID 驱动
  - 建议：在设备管理器中更新驱动，或卸载后重新插拔让 Windows 重新枚举

### 检查项 11b：复合设备的接口数量

对复合设备（`bDeviceClass = 0xEF`），检查 `bNumInterfaces`：
- SC802A/SC805B：应有至少 2 个接口（UVC Video + HID）
- MU55A/MS75A Camera：应有至少 2 个接口（UVC Video + HID）
- MU55A/MS75A Audio：应有至少 2 个接口（UAC Audio + HID）
- BM32/BM51D/BM52C：应有至少 2 个接口（UAC Audio + HID），其中 `&MI_01` 是工具通道
- 如果接口数少于预期 = **Warning：复合设备接口不完整**

### 检查项 11c：设备描述符的 bDeviceClass

- `bDeviceClass = 0xEF` (Miscellaneous) + `bDeviceSubClass = 0x02` + `bDeviceProtocol = 0x01` = 正常（USB 复合设备，使用 IAD）
- `bDeviceClass = 0x00` = 接口级定义（也正常，部分设备使用此方式）
- `bDeviceClass = 0xFF` (Vendor Specific) = **Warning：可能缺少复合设备驱动**
- `bDeviceClass = 其他值` = **Warning：设备描述符异常**

### 检查项 11d：Class 字段检查

查看 Device Information 中的 `Class` 字段：
- HID 枚举设备：父设备的 `Class` 应为 `USB`（复合设备），子 HID 设备应为 `HIDClass`
- 如果父设备 `Class` 不是 `USB` = **Error：驱动安装异常**
- 如果在 USB 子节点中找不到 `HIDClass` 设备 = **Error：HID 驱动未加载**

### 检查项 11e：Device Description 检查

查看 `Device Description` 字段：
- 正常：应显示设备产品名称或 "USB Composite Device"
- 如果显示 "Unknown Device" = **Error：设备枚举失败**
- 如果显示通用名称如 "USB Device" = **Warning：驱动可能不完整**

## 规则 12：枚举方式匹配检查

**检查对象**：所有已识别的 MAXHUB 设备
**严重性**：Error

根据 VID/PID 确定枚举方式，检查对应的条件是否满足：

### HID 枚举设备（SC802A, SC805B, SC26A/B, SC29A, MU55A, MS75A, BM32, BM51D, BM52C, DT12PA/PC/PD/PE）

需要在 XML 中确认：
1. 设备的 Configuration Descriptor 包含 `bInterfaceClass = 0x03` (HID) 的接口
2. HID 接口的 `bInterfaceProtocol` 字段存在
3. 设备的 Device ID 包含 `USB\VID_xxxx&PID_xxxx` 格式（即 Windows 已正确识别 USB 设备）
4. Device Description 不是 "Unknown Device"

**常见失败场景**：

| 现象（XML 中可见） | 原因 | 严重性 |
|-------------------|------|--------|
| 无 `bInterfaceClass=0x03` 的接口 | HID 驱动未加载，设备被识别为通用 USB 设备 | **Error** |
| `Problem Code = 28` | 无驱动 | **Error** |
| `bDeviceClass = 0xFF` | 设备可能处于异常模式（如固件升级失败） | **Warning** |
| `Device Description = "Unknown Device"` | 设备枚举失败 | **Error** |
| 配置描述符中接口数量少于预期 | 复合设备部分功能丢失 | **Warning** |
| 存在 `bInterfaceClass=0x03` 但 `Class` 不是 `HIDClass` | HID 驱动未绑定到接口 | **Error** |

### USB 枚举设备（XBoardV7, MS07A, MS10E, MU08A, DT10PB, DT10PC, AC21B）

这些设备先通过 USB 层枚举，再解析 HID 子设备。USB 层正常是前提：
1. Problem Code = 0
2. Status 包含 DN_STARTED
3. 后续 HID 子设备解析依赖 ContainerID 正确

**额外检查**：
- 如果 USB 设备枚举成功但功能异常（如摄像头不可控），检查 Configuration Descriptor 中是否有 `bInterfaceClass=0x03` (HID) 接口
- 对 XBoardV7：检查 Camera PID 的 HID UsagePage 是否为 0xFF00，Audio PID 的 HID InstanceId 是否包含 `&MI_00&COL01` 和 `&MI_01`

### Video 枚举设备（SC25A）

### 特殊设备（MC33C）

MC33C (DM30) 是扩展麦克风，**不直接枚举**。它通过 MU55A Audio (PID 0479) 的 HID 接口轮询发现。
- 前提：MU55A Audio 必须先成功枚举
- 如果 MC33C 未发现但 MU55A Audio 正常 → MC33C 物理未连接或故障
- 如果 MU55A Audio 也枚举不到 → 先解决 MU55A 的枚举问题

这些设备通过摄像头视频接口枚举，不依赖 HID：
1. 检查 Configuration Descriptor 中是否有 `bInterfaceClass = 0x0E` (Video/UVC) 的接口
2. 检查 Video 模式描述符是否存在（如分辨率、帧率）
3. 如果有 Video 接口且 Problem Code = 0，通常可以枚举成功

## 规则 13：HID UsagePage 不可直接从 XML 判断的说明

**重要**：USBTreeView XML 通常**不直接显示** HID UsagePage 和 UsageId。这些信息在 HID Report Descriptor 中，而 USBTreeView 不解析 HID Report Descriptor。

因此，规则 11-12 的诊断是基于 XML 中**可推断的信息**进行的间接判断：
- 有 `bInterfaceClass = 0x03` (HID) 接口 → HID 驱动已加载，大概率 UsagePage 正确
- 无 HID 接口 → **确定**无法枚举
- 有 HID 接口但应用仍枚举不到 → 可能是 UsagePage 不匹配，需要用其他工具（如 HID Viewer）进一步确认

**在报告中应明确说明**：
- 如果 XML 中显示 HID 接口正常但应用仍枚举不到 → 建议用 USB HID Viewer 检查 UsagePage 是否正确
- 如果 XML 中没有 HID 接口 → 直接判定为枚举失败原因

---

# 诊断报告输出格式

```markdown
## USB 诊断报告

**计算机**: {computername}
**报告时间**: {date} {time}
**操作系统**: {OS info}

---

### 设备概览

| # | 设备名称 | VID:PID | MAXHUB 型号 | 枚举方式 | 端口路径 | 连接速度 | USB状态 | 应用枚举 |
|---|---------|---------|------------|---------|---------|---------|--------|---------|
| 1 | ... | ... | ... | HID/USB/Video | ... | ... | ✅/❌ | ✅/❌/⚠️ |

### USB 层诊断

#### ❌ 错误 ({count})
#### ⚠️ 警告 ({count})
#### ✅ 通过 ({count})

### 应用层诊断（MAXHUB UC 枚举检查）

对每个 MAXHUB 设备输出：

**[设备名]** (VID:PID) — 枚举方式: {HID/USB/Video}
- USB 层: ✅/❌ {描述}
- HID 接口: ✅ 存在 / ❌ 不存在
- 复合设备接口数: {N} (预期 ≥ {M})
- bDeviceClass: {值} ({含义})
- Class 字段: {值}
- Device Description: {值}
- **结论**: 应用能否枚举 → ✅ 可以 / ❌ 不可以 / ⚠️ 不确定

### 复合设备完整性

| 型号 | Camera | Audio | 状态 |
|------|--------|-------|------|
| ... | ✅ PID xxxx | ✅ PID xxxx | 完整 |

### 修复建议（优先级排序）

1. {最紧急}
2. {次紧急}
...

### USB 拓扑概览

{ASCII 树形图，每个设备标注 USB 状态 + 应用枚举状态}
```
