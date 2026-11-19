---
name: calc-pro
description: 专业计算套件，基于官方 calculator 扩展。提供安全算术、统计分析与财务计算（复利/贷款/定投/平均回报率）。多脚本模块化依赖，无外部依赖。
compatibility: Python 3.10+，无外部依赖
metadata:
  author: 杨宇涵
---

# Calc Pro

专业计算套件，在官方 calculator 基础上扩展出**统计分析**与**财务计算**能力，
用于解决 LLM 直接心算容易出错的精确数值任务。

## 用途

提供一套安全、可复用的命令行计算工具，覆盖三类任务：

- 算术表达式与单位换算（底层引擎 `calc.py`）
- 统计分析（`stats.py`：均值/中位数/方差/标准差）
- 财务计算（`finance.py`：复利终值/贷款月供/定投终值/平均回报率）

## Agent 指令

1. 阅读本 SKILL.md，了解三个子模块的能力与命令格式。
2. 根据用户问题选择正确的脚本执行（见下方「脚本与依赖关系」）。
3. 从脚本输出中读取精确结果，报告给用户。

## 脚本与依赖关系

本 skill 由 4 个脚本组成，脚本之间存在模块化依赖（调用链）：

```
scripts/
├── calc.py      # 底层引擎：AST 白名单安全求值、百分比、单位换算（无内部依赖）
├── stats.py     # 统计模块：依赖 calc.safe_eval 解析输入
├── finance.py   # 财务模块：依赖 calc.safe_eval + stats.mean
└── cli.py       # 统一入口：依赖 calc / stats / finance
```

## 命令用法

```bash
# 算术（底层引擎）
python scripts/calc.py "2 + 3 * 4"            # Result: 14
python scripts/calc.py "15% of 200"           # Result: 30
python scripts/calc.py "100 celsius to fahrenheit"

# 统计（stats.py）：总体标准差
python scripts/stats.py 12 15 18 22 25 27 31 35 40 45 8 9 14 19 23 28 33 38 42 50
# 输出 n / sum / mean / median / min / max / population variance / population std
# 加 --sample 可改为样本标准差

# 财务（finance.py）
python scripts/finance.py loan 1000000 0.045 30        # 月供/总还款/总利息
python scripts/finance.py compound 100000 0.07 20      # 复利终值/总利息
python scripts/finance.py annuity 5000 0.06 10         # 定投终值
python scripts/finance.py avg-return 0.05 0.08 0.12    # 平均回报率

# 统一入口（cli.py）
python scripts/cli.py stats 1 2 3 4 5
python scripts/cli.py finance loan 1000000 0.045 30
```

## 输出格式

- 算术：单行 `Result: <value>`
- 统计：多行键值对（`population std = <value>` 等）
- 财务：多行键值对（`monthly payment = <value>` 等）

## 安全性

本 skill 保持与官方 calculator 相同的安全等级，且不引入任何外部依赖：

- 表达式求值使用 **AST 白名单**，不使用内置 `eval()`；
- 无网络请求、无文件系统读写、无子进程/命令执行；
- 无敏感路径读取（不访问 `~/.ssh`、`.env` 等）、无硬编码密钥；
- 仅使用 Python 标准库，兼容沙盒环境。

## 限制

- 统计仅支持一组独立数值，不支持数据表/CSV 输入。
- 财务计算采用固定年利率，不含浮动利率/提前还款等场景。
