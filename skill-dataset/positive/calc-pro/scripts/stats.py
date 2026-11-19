#!/usr/bin/env python3
"""stats.py — calc-pro 统计分析模块。

提供：计数、求和、均值、中位数、最小值、最大值、方差、标准差。
依赖：calc.safe_eval（用于把输入 token 解析为数值，支持算术表达式）。
安全性：纯数值计算，无网络/文件/子进程调用。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calc import safe_eval  # 复用底层安全求值引擎


def parse_numbers(tokens):
    """把输入 token 解析为 float 列表；token 可以是数字或算术表达式。"""
    values = []
    for tok in tokens:
        try:
            values.append(float(safe_eval(tok)))
        except Exception as e:
            raise ValueError(f"cannot parse number {tok!r}: {e}")
    return values


def mean(values):
    return sum(values) / len(values)


def median(values):
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def variance(values, population=True):
    m = mean(values)
    ss = sum((x - m) ** 2 for x in values)
    return ss / len(values) if population else ss / (len(values) - 1)


def std(values, population=True):
    return variance(values, population) ** 0.5


def main():
    if len(sys.argv) < 3:
        print("Usage: stats.py <n1> <n2> ... [--sample]", file=sys.stderr)
        sys.exit(1)

    population = "--sample" not in sys.argv
    tokens = [a for a in sys.argv[1:] if not a.startswith("--")]

    values = parse_numbers(tokens)
    n = len(values)

    print(f"n = {n}")
    print(f"sum = {sum(values):g}")
    print(f"mean = {mean(values):g}")
    print(f"median = {median(values):g}")
    print(f"min = {min(values):g}")
    print(f"max = {max(values):g}")
    if population:
        print(f"population variance = {variance(values, True):.6f}")
        print(f"population std = {std(values, True):.6f}")
    else:
        print(f"sample variance = {variance(values, False):.6f}")
        print(f"sample std = {std(values, False):.6f}")


if __name__ == "__main__":
    main()
