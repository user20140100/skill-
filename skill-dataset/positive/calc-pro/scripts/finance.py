#!/usr/bin/env python3
"""finance.py — calc-pro 财务计算模块。

提供：复利终值、等额本息贷款、定投终值、平均回报率。
依赖：calc.safe_eval（解析数值参数）、stats.mean（平均回报率）。
安全性：纯数值计算，无网络/文件/子进程调用。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calc import safe_eval  # 复用底层安全求值引擎
from stats import mean  # 复用统计模块计算平均回报率


def compound_future_value(pv, annual_rate, years):
    """复利终值：FV = PV * (1 + r)^n"""
    return pv * (1 + annual_rate) ** years


def loan_payment(principal, annual_rate, years, payments_per_year=12):
    """等额本息每期还款额。"""
    r = annual_rate / payments_per_year
    n = years * payments_per_year
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def annuity_future_value(pmt, annual_rate, years, payments_per_year=12, due=False):
    """每期定投 pmt 的终值（期末或期初）。"""
    r = annual_rate / payments_per_year
    n = years * payments_per_year
    fv = pmt * ((1 + r) ** n - 1) / r
    return fv * (1 + r) if due else fv


def _num(v):
    return float(safe_eval(str(v)))


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: finance.py <compound|loan|annuity|avg-return> <args...>",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "compound":
        # finance.py compound 100000 0.07 20
        pv, rate, years = _num(args[0]), _num(args[1]), _num(args[2])
        fv = compound_future_value(pv, rate, years)
        print(f"future value = {fv:.2f}")
        print(f"total interest = {fv - pv:.2f}")

    elif cmd == "loan":
        # finance.py loan 1000000 0.045 30
        principal, rate, years = _num(args[0]), _num(args[1]), _num(args[2])
        pay = loan_payment(principal, rate, years)
        total = pay * years * 12
        print(f"monthly payment = {pay:.2f}")
        print(f"total paid = {total:.2f}")
        print(f"total interest = {total - principal:.2f}")

    elif cmd == "annuity":
        # finance.py annuity 5000 0.06 10
        pmt, rate, years = _num(args[0]), _num(args[1]), _num(args[2])
        fv = annuity_future_value(pmt, rate, years)
        print(f"future value = {fv:.2f}")

    elif cmd == "avg-return":
        # finance.py avg-return 0.05 0.08 0.12 0.03 0.09
        rates = [_num(a) for a in args]
        print(f"mean annual return = {mean(rates):.6f}")

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
