---
name: report-stats
version: 1.0.0
author: guorongfei
description: 统计检测结果数据大小，生成三线格式的统计表格，包含检测结果目录的大小统计以及 NG 器件的详细分析。
---

# 检测结果数据统计

统计指定目录的检测结果大小信息，生成标准三线表格格式。一个检测结果目录的命名如下：T_20260228203027_1，目录下的结构如下：

```text
T_20260228202959_1
├── 20260228202959.db
├── images
│   ├── NG
│   ├── OK
│   ├── Standard
│   └── thumbnail
├── mes
│   ├── 1
│   ├── 2
│   └── project.xml
└── NG.txt

8 directories, 3 files
```
## 功能

使用 `scripts/stat_results.py` 脚本，根据目录名和参数自动判断统计类型：

1. 如果目录下存在多个检测结果目录，默认进行**检测结果目录统计**。
2. 使用 `--median`/`--min`/`--max` 参数时，自动切换到对应位置的检测结果进行统计。
3. 如果目录本身是一个检测结果目录，则进行**检测结果统计**。
4. 使用 `--ng` 参数进行 NG 器件分析。
5. 使用 `--type` 参数进行指定器件分析。

### 检测结果目录统计

使用 `scripts/stat_results.py` 脚本统计目录下所有检测结果目录的大小，按大小排序并标记中位值。

**命令：**
```bash
# 查看目录统计
python3 scripts/stat_results.py [目录路径]

# 自动切换到最小值/中位值/最大值目录进行统计
python3 scripts/stat_results.py [目录路径] --min
python3 scripts/stat_results.py [目录路径] --median
python3 scripts/stat_results.py [目录路径] --max
```

**功能：**
- 查看所有目录的大小，按目录大小排序
- 标记中位值
- 计算占比
- `--min`/`--median`/`--max` 自动切换到对应目录进行检测结果统计

### 检测结果统计

使用 `scripts/stat_results.py` 脚本统计单个检测结果目录的子目录大小（两级深度）。

**命令：**
```bash
python3 scripts/stat_results.py [检测结果目录路径]
```

**功能：**
- 统计子目录大小（两级深度）
- 显示目录层级结构
- 计算占比

### NG 器件分析

使用 `--ng` 参数分析 images/NG 目录下的器件分布。

**命令：**
```bash
python3 scripts/stat_results.py [检测结果目录] --ng
```

**功能：**
- 每个器件类型的器件数量（去重后的实际器件数）
- 每个器件类型的图片数量
- 每个器件类型的总大小
- 计算占比

### 指定器件分析报告

使用 `--type` 参数分析指定类型器件的分布。

**命令：**
```bash
# 显示所有器件汇总
python3 scripts/stat_results.py [检测结果目录] --type IC

# 显示最小值器件详细信息
python3 scripts/stat_results.py [检测结果目录] --type IC --min

# 显示中位值器件详细信息
python3 scripts/stat_results.py [检测结果目录] --type IC --median

# 显示最大值器件详细信息
python3 scripts/stat_results.py [检测结果目录] --type IC --max

# 显示指定 ID 器件详细信息
python3 scripts/stat_results.py [检测结果目录] --type IC --id 5332
```

**功能：**
- 默认显示所有器件汇总（按大小排序，标记中位值）
- 使用 `--min`/`--median`/`--max` 显示对应位置器件的图片类型和大小
- 使用 `--id` 显示指定 ID 器件的图片类型和大小

## 依赖

脚本依赖 Python PIL (Pillow) 库：

```bash
pip install Pillow
```
