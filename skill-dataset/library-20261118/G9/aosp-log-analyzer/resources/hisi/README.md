# HiSilicon (海思) 平台经验目录

存放 HiSilicon 平台特有的日志分析经验。

## 平台识别特征
- CPU 型号包含 `Hi37` 系列：`Hi3751V352`、`Hi3798`、`Hi3716` 等
- U-Boot 版本通常基于 2019.07 或更新
- 日志中出现 `hisi-sdhci`、`hiusb` 关键字
- SDK 命名格式：`HiDPTSmartSDK`、`HiSTBAndroid`
- 板型通常为 `HI3751V350_DEMO_BOARD` 等
- 常见厂商：CVTE(兆驰)、其他 TV/STB 方案商

## 常见产品形态
- Smart TV (智能电视)
- OTT Box (网络机顶盒)
- IPTV Box (运营商机顶盒)

## 文件命名示例
- `uboot_upgrade_fail.md` — U-Boot 升级失败问题
- `panel_init_error.md` — Panel/TCON 初始化问题
- `standby_wakeup.md` — 待机唤醒问题
- `emmc_boot_issue.md` — eMMC 启动问题
- `slave_boot_error.md` — 从核启动问题
