# USBTreeView XML 格式说明

此文件描述 USBTreeView 工具导出的 XML 报告格式，帮助 Agent 正确解析数据。

## 工具信息

- 工具名称：UsbTreeView
- 官网：https://www.uwe-sieber.de/usbtreeview.html
- 当前测试版本：V4.4.3.0
- 导出格式：XML (UTF-8)

## XML 整体结构

```xml
<?xml version="1.0" encoding="utf-8"?>
<!--UsbTreeView Report file - V4.4.3.0-->
<UsbTreeViewReport computername="HOSTNAME" date="2026-02-10" time="13:10:24">
  <node text="HOSTNAME" icon="0" type="2" expanded="1">
    <text> ... 系统摘要信息 ... </text>

    <!-- Host Controller 节点 -->
    <node text="Controller名称" icon="1" type="3" expanded="1">
      <text> ... Controller 详情 ... </text>

      <!-- Root Hub 节点 -->
      <node text="USB Root Hub (USB 3.0)" icon="18" type="4" expanded="1">
        <text> ... Hub 详情 ... </text>

        <!-- Port 节点 -->
        <node text="[Port1]" icon="13" type="8" speed="2">
          <text> ... Port/Device 详情 ... </text>

          <!-- 如果 Port 下有 Hub，会有嵌套的 Port 节点 -->
          <node text="[Port3]" icon="14" type="8" speed="3">
            <text> ... 子 Port/Device 详情 ... </text>
          </node>
        </node>

      </node>
    </node>

  </node>
</UsbTreeViewReport>
```

## 节点类型（type 属性）

| type | 含义 | icon |
|------|------|------|
| `2` | 计算机（根节点） | 0 |
| `3` | USB Host Controller | 1 |
| `4` | USB Root Hub | 18 |
| `8` | USB Port | 13(USB 2.0) / 14(USB 3.0) |

## speed 属性（Port 节点）

| speed | 含义 |
|-------|------|
| `1` | Low-Speed (USB 1.x, 1.5 Mbps) |
| `2` | Full-Speed/High-Speed (USB 2.0, 12/480 Mbps) |
| `3` | SuperSpeed (USB 3.x, 5/10 Gbps) |

## 关键字段解析

所有字段都嵌套在 `<text>` 标签中，以 `&#xD;&#xA;` 分隔（即 CRLF），格式为 `Key : Value`。

### 系统摘要（type=2 节点）

```
Operating System       : Windows 10 Enterprise: NT10.0 Build 19045.6456
Up Time                : 81 days 23 hours 27 minutes 23 seconds
USB Host Controllers   : 2
USB Root Hubs          : 2
USB Standard Hubs      : 0
USB Peripheral Devices : 3
```

### Host Controller 信息（type=3 节点）

关键字段：

```
Friendly Name            : Intel(R) USB 3.10 eXtensible Host Controller - 1.10 (Microsoft)
Device Path              : \\?\PCI#VEN_8086&DEV_8A13...
Driver                   : \SystemRoot\System32\drivers\USBXHCI.SYS (Version: 10.0.19041.5794)
Status                   : 0x0180200A (DN_DRIVER_LOADED, DN_STARTED, DN_DISABLEABLE, ...)
Problem Code             : 0
Power State              : D0 (supported: D0, D3)
NumberOfRootPorts        : 0x0C (12 Ports)
```

### USB Hub 信息（type=4 节点）

关键字段：

```
Sum of Hubs and Devices  : 3
bNumberOfPorts           : 0x12 (18 Ports)
HubIsBusPowered          : 0x00 (Self Powered)
```

### USB Port / Device 信息（type=8 节点）

这是最核心的诊断数据。关键字段分为以下区域：

#### 连接状态

```
Connection Status        : 0x00 (No device is connected)
Connection Status        : 0x01 (Device is connected)
Port Chain               : 2-7
```

- `Connection Status`:
  - `0x00` = 无设备（空端口）
  - `0x01` = 设备已连接
  - `0x02` = 设备枚举失败

- `Port Chain`：设备在 USB 拓扑中的路径
  - 格式：`{controller}-{port}` 或 `{controller}-{hub_port}-{device_port}`
  - 示例：`2-7` = 第 2 个 Controller 的第 7 个端口

#### 端口属性

```
Properties               : 0x01
 IsUserConnectable       : yes
 PortIsDebugCapable      : no
 PortHasMultiCompanions  : no
 PortConnectorIsTypeC    : no
```

#### 端口支持的 USB 协议

```
SupportedUsbProtocols    : 0x04
 Usb110                  : 0 (no)
 Usb200                  : 0 (no)
 Usb300                  : 1 (yes, port supports USB 3.0)
```

#### 设备摘要（仅已连接设备）

```
Vendor ID                : 0x1FF7 (MAXHUB)
Product ID               : 0x0516
Manufacturer String      : MAXHUB
Serial                   : ---
USB Version              : 2.0.1
Port maximum Speed       : SuperSpeed
Device maximum Speed     : SuperSpeed
Device Connection Speed  : SuperSpeed
Self powered             : no
Demanded Current         : 500 mA
Used Endpoints           : 2
```

#### 设备详情（仅已连接设备）

```
Device Description       : USB Composite Device
Device Path              : \\?\USB#VID_1FF7&PID_0516...
Device ID                : USB\VID_1FF7&PID_0516\5&...
Hardware IDs             : USB\VID_1FF7&PID_0516&REV_...
Driver                   : \SystemRoot\System32\drivers\...
Status                   : 0x0180200A (DN_DRIVER_LOADED, DN_STARTED, ...)
Problem Code             : 0
Container ID             : {xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
EnhancedPowerMgmtEnabled : 0
Power State              : D0 (supported: D0, D3)
```

#### USB 设备描述符

```
bLength                  : 0x12 (18 bytes)
bDescriptorType          : 0x01 (Device Descriptor)
bcdUSB                   : 0x0200 (USB 2.0)
bDeviceClass             : 0xEF (Miscellaneous)
bDeviceSubClass          : 0x02
bDeviceProtocol          : 0x01 (Interface Association Descriptor)
bMaxPacketSize0          : 0x40 (64 bytes)
idVendor                 : 0x1FF7
idProduct                : 0x0516
bcdDevice                : 0x0100
iManufacturer            : 0x01
iProduct                 : 0x02
iSerialNumber            : 0x00
bNumConfigurations       : 0x01
```

#### 配置描述符

包含 Interface 信息，可识别设备功能（UVC 摄像头、UAC 音频、HID 等）：

```
bInterfaceClass          : 0x0E (Video) → UVC 摄像头
bInterfaceClass          : 0x01 (Audio) → UAC 音频
bInterfaceClass          : 0x03 (HID) → 人机接口设备
bInterfaceClass          : 0xFF (Vendor Specific) → 厂商自定义
```

## VID/PID 提取位置

Agent 可以从以下位置提取 VID/PID：

1. **Summary 区域**：`Vendor ID : 0xXXXX` 和 `Product ID : 0xXXXX`
2. **Device ID**：`USB\VID_XXXX&PID_XXXX\...`
3. **Hardware IDs**：`USB\VID_XXXX&PID_XXXX&REV_XXXX`
4. **Device Descriptor**：`idVendor : 0xXXXX` 和 `idProduct : 0xXXXX`

推荐使用 **Summary 区域** 的 `Vendor ID` / `Product ID`，最简洁可靠。

## Companion Port（USB 3.0 特有）

在 xHCI 控制器中，USB 2.0 和 USB 3.0 端口成对出现：

```
CompanionIndex           : 0
 CompanionHubSymLnk      : USB#ROOT_HUB30#...
 CompanionPortNumber     : 0x0D (Port 13)
 -> CompanionPortChain   : 2-13
```

这表示 Port 1 (USB 2.0) 的伴生端口是 Port 13 (USB 3.0)。USB 3.0 设备会连接到伴生的 USB 3.0 端口上。

## 解析注意事项

1. XML 中的 `<text>` 内容使用 `&#xD;&#xA;` 编码换行符，解析时需要替换为实际换行
2. 字段值可能包含括号注释，如 `0x1FF7 (MAXHUB)`，提取时注意分离数值和注释
3. 某些字段可能不存在（如空端口没有设备描述符），解析时需要容错
4. 嵌套的 `<node>` 表示 USB 拓扑层级关系
5. 同一个物理 USB 设备可能在 USB 2.0 和 USB 3.0 Root Hub 下各有一个端口条目（Companion 关系），需要去重
