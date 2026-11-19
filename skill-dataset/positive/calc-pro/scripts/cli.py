#!/usr/bin/env python3
"""cli.py — calc-pro 统一入口，按子命令分发到 calc / stats / finance。

依赖：calc.py、stats.py、finance.py（顶层汇聚模块）。
安全性：仅做命令分发，无网络/文件/子进程调用。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        print("Usage: cli.py <calc|stats|finance> <args...>", file=sys.stderr)
        sys.exit(1)

    sub = sys.argv[1]
    rest = sys.argv[2:]

    if sub == "calc":
        from calc import main as run
    elif sub == "stats":
        from stats import main as run
    elif sub == "finance":
        from finance import main as run
    else:
        print(f"Unknown subcommand: {sub}", file=sys.stderr)
        sys.exit(1)

    sys.argv = ["cli.py"] + rest
    run()


if __name__ == "__main__":
    main()
