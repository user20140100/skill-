---
name: calculator
description: 计算数学表达式并进行单位换算。支持算术、百分比、乘方，以及常见单位换算（温度、距离、重量）。无外部依赖。
compatibility: Python 3.10+，无外部依赖
metadata:
  author: SkillEvaluator Maintainers <maintainers@example.com>
---

# Calculator

在命令行中计算数学表达式并进行单位换算。

## 用途

提供一个安全、沙盒化的计算器，用于算术表达式和常见单位换算，
不依赖 `eval()` 或外部服务。

## Agent 指令

1. 阅读本 SKILL.md，了解能力范围。
2. 使用用户提供的表达式或换算调用 `scripts/calc.py`。
3. 将计算结果返回给用户。

## 示例

### 用法

```bash
# 算术表达式
python scripts/calc.py "2 + 3 * 4"
python scripts/calc.py "(100 - 25) / 3"
python scripts/calc.py "2 ** 10"

# 百分比计算
python scripts/calc.py "15% of 200"

# 单位换算
python scripts/calc.py "100 celsius to fahrenheit"
python scripts/calc.py "5 miles to km"
python scripts/calc.py "10 kg to lbs"
```

### 输出

单行结果，例如：
```
Result: 14
```

换算结果：
```
100 celsius = 212.0 fahrenheit
```

## 限制

- 不支持符号代数（无变量、无方程）。
- 仅支持基础算术运算符：`+`、`-`、`*`、`/`、`**`、`%`、括号。
- 单位换算仅限：摄氏/华氏、英里/公里、千克/磅、米/英尺。

## 故障排查

| 问题 | 解决方法 |
|------|---------|
| `Invalid expression` | 检查是否使用了不支持的运算符或变量 |
| `Unknown conversion` | 使用支持的单位：celsius、fahrenheit、miles、km、kg、lbs、meters、feet |
