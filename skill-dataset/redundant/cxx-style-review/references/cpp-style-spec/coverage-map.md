# Coverage Map

This file maps every Markdown heading from the source-of-truth document to exactly one split document.

- Source-of-truth (archived): `./source-of-truth/C&Cpp编程规范-初稿v0.3.md`
- Note: The split documents contain the full original content, partitioned into non-overlapping line ranges.

## File Slices (Line Ranges)

| Split file | Source line range | Note |
| --- | --- | --- |
| `overview.md` | 1-117 | Preamble + Chapter "概述" (scope/principles/classification). |
| `style-naming.md` | 118-576 | Chapter "一. 风格规约" section "1-1 命名". |
| `style-formatting.md` | 577-864 | Chapter "一. 风格规约" section "1-2 格式". |
| `style-comments.md` | 865-949 | Chapter "一. 风格规约" section "1-3 注释". |
| `practice-files.md` | 950-1123 | Chapter "二. 实践规约" section "2-1 文件". |
| `practice-macros.md` | 1124-1228 | Chapter "二. 实践规约" section "2-2 预处理与宏运用". |
| `practice-control-flow.md` | 1229-1367 | Chapter "二. 实践规约" sections "2-3 条件控制语句" + "2-4 循环". |
| `practice-functions-and-general.md` | 1368-1569 | Chapter "二. 实践规约" section "2-5 函数" + "2-5 综合". |
| `practice-cpp-specific.md` | 1570-1730 | Chapter "二. 实践规约" section "2-6 其他C++规则". |
| `safety-types-and-data.md` | 1731-1829 | Chapter "三. 安全规约" section "3-1 变量类型与数据安全". |
| `safety-resources.md` | 1830-1896 | Chapter "三. 安全规约" section "3-2 资源使用". |
| `safety-threading-and-build.md` | 1897-2063 | Chapter "三. 安全规约" sections "3-3 进程与线程" + "3-3 其他". |

## Heading Map

| Source line | Level | Heading | Split file |
| --- | --- | --- | --- |
| 78 | `#` | 概述 | `overview.md` |
| 79 | `##` | 1 说明 | `overview.md` |
| 86 | `##` | 2 核心原则 | `overview.md` |
| 94 | `##` | 3 适用范围 | `overview.md` |
| 100 | `##` | 4 规则考量分类 | `overview.md` |
| 111 | `##` | 5 章节说明 | `overview.md` |
| 118 | `#` | 一. 风格规约 | `style-naming.md` |
| 120 | `##` | 1-1 命名 | `style-naming.md` |
| 123 | `###` | 1-1-1 文件 | `style-naming.md` |
| 165 | `###` | 1-1-2 宏 | `style-naming.md` |
| 215 | `###` | 1-1-3  变量 | `style-naming.md` |
| 340 | `###` | 1-1-4 常量 | `style-naming.md` |
| 359 | `###` | 1-1-5 枚举 | `style-naming.md` |
| 415 | `###` | 1-1-6 结构体 | `style-naming.md` |
| 440 | `###` | 1-1-7 函数 | `style-naming.md` |
| 480 | `###` | 1-1-8 C++命名空间与类 | `style-naming.md` |
| 537 | `###` | 1-1-9 综合 | `style-naming.md` |
| 577 | `##` | 1-2 格式 | `style-formatting.md` |
| 580 | `###` | 1-2-1 空格 | `style-formatting.md` |
| 723 | `###` | 1-2-2 缩进与换行 | `style-formatting.md` |
| 823 | `###` | 1-2-3 括号 | `style-formatting.md` |
| 865 | `##` | 1-3 注释 | `style-comments.md` |
| 868 | `###` | 1-3-1 文件首部/函数 注释格式 | `style-comments.md` |
| 917 | `###` | 1-3-2 细则 | `style-comments.md` |
| 950 | `#` | 二. 实践规约 | `practice-files.md` |
| 952 | `##` | 2-1 文件 | `practice-files.md` |
| 954 | `###` | 2-1-1 通用规则 | `practice-files.md` |
| 1034 | `###` | 2-1-2 C++规则 | `practice-files.md` |
| 1124 | `##` | 2-2 预处理与宏运用 | `practice-macros.md` |
| 1126 | `###` | 2-2-1 条件编译宏 | `practice-macros.md` |
| 1186 | `###` | 2-2-2 宏常量与宏函数 | `practice-macros.md` |
| 1229 | `##` | 2-3 条件控制语句 | `practice-control-flow.md` |
| 1231 | `###` | 2-3-1 if/if-else/if-else if-else 与 bool表达式 | `practice-control-flow.md` |
| 1292 | `###` | 2-3-2 switch-case | `practice-control-flow.md` |
| 1340 | `##` | 2-4 循环 | `practice-control-flow.md` |
| 1342 | `###` | 2-4-1 通用规则 | `practice-control-flow.md` |
| 1356 | `###` | 2-4-2 C++规则 | `practice-control-flow.md` |
| 1368 | `##` | 2-5 函数 | `practice-functions-and-general.md` |
| 1370 | `###` | 2-5-1 通用规则 | `practice-functions-and-general.md` |
| 1482 | `###` | 2-5-2 C++规则 | `practice-functions-and-general.md` |
| 1489 | `##` | 2-5 综合 | `practice-functions-and-general.md` |
| 1491 | `###` | 2-5-1 禁用的关键字/禁用的编码方式 | `practice-functions-and-general.md` |
| 1507 | `###` | 2-5-2 全局变量/结构体 | `practice-functions-and-general.md` |
| 1534 | `###` | 2-5-3 线程 | `practice-functions-and-general.md` |
| 1554 | `###` | 2-5-4 日志 | `practice-functions-and-general.md` |
| 1570 | `##` | 2-6 其他C++规则 | `practice-cpp-specific.md` |
| 1572 | `###` | 2-6-1 命名空间/类/结构体 | `practice-cpp-specific.md` |
| 1667 | `###` | 2-6-2 指针相关 | `practice-cpp-specific.md` |
| 1675 | `###` | 2-6-3 内存/线程/锁/文件等资源的使用与释放 | `practice-cpp-specific.md` |
| 1685 | `###` | 2-6-4 异常处理 | `practice-cpp-specific.md` |
| 1702 | `###` | 2-6-5 其他 | `practice-cpp-specific.md` |
| 1731 | `#` | 三. 安全规约 | `safety-types-and-data.md` |
| 1733 | `##` | 3-1 变量类型与数据安全 | `safety-types-and-data.md` |
| 1735 | `###` | 3-1-1 变量声明定义 | `safety-types-and-data.md` |
| 1756 | `###` | 3-1-2 变量使用 | `safety-types-and-data.md` |
| 1830 | `##` | 3-2 资源使用 | `safety-resources.md` |
| 1832 | `###` | 3-2-1 指针 | `safety-resources.md` |
| 1852 | `###` | 3-2-2 内存 | `safety-resources.md` |
| 1887 | `###` | 3-2-3 其他资源 | `safety-resources.md` |
| 1897 | `###` | 3-3 进程与线程 | `safety-threading-and-build.md` |
| 1898 | `###` | 3-3-1 变量的线程（进程）安全 | `safety-threading-and-build.md` |
| 1903 | `##` | 3-3 其他 | `safety-threading-and-build.md` |
| 1905 | `###` | 3-3-1 随机数的使用/异步安全函数 | `safety-threading-and-build.md` |
| 2051 | `###` | 3-3-2 工程构建与信息披露 | `safety-threading-and-build.md` |
