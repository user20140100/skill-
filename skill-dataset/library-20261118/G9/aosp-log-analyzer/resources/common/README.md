# 经验文件模板说明

本目录用于存放 AOSP 日志分析的经验知识文件。

## 目录结构

```
resources/
├── common/           # 跨平台通用经验
├── mtk/              # MTK 平台特有经验
├── qualcomm/         # Qualcomm 平台特有经验
├── realtek/          # Realtek 平台特有经验
└── amlogic/          # Amlogic 平台特有经验
```

## 经验文件命名规范

- 按问题类型或模块命名，使用小写英文 + 下划线
- 示例：`native_crash_patterns.md`、`anr_common_causes.md`、`camera_crash.md`

## 经验文件格式

每个 .md 文件应包含以下结构（字段可根据实际情况增减）：

```markdown
# [问题标题]

## 适用平台
[MTK / Qualcomm / Realtek / Amlogic / 通用]

## 问题现象
简要描述用户可感知的问题表现

## 典型日志特征
用于日志匹配的关键模式（可包含正则表达式）

## 根因
问题的根本原因分析

## 解决方案
修复方式、代码修改、配置调整等

## 关联信息
相关链接、补丁ID、配置文件路径等
```
