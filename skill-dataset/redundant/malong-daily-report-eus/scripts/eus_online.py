#!/usr/bin/env python3
"""
EUS 业务系统在线时长采集（malong-daily-report 数据源之一）

功能：查询当前用户最近 N 天使用各业务系统的在线时长，输出一段 markdown，
     供 collect.sh 拼进日报素材。用 EUS xiooview dataview 接口（无鉴权）。

用户身份解析（默认全自动，零询问）：
  1. --account 指定 → 直接用 account 过滤（最唯一，兜底）
  2. --name 指定 → 用 username 过滤
  3. 都未指定 → 从 lark-cli auth status 取 userName（如"周渝杰"），用 username 过滤
  CVTE 姓名重名时 EUS 在名字加尾缀区分（如"曹晓飞15769"），lark userName 与 EUS username 一致，不冲突。

时间范围：--days N（默认 7）。从目标日期 --date 往前数 N 天，单次请求用 or 串联多日期 eq
         一次查回（N 天 = 1 次请求），按天分组展示（当天数据常因 EUS 系统更新延迟未入库，故默认回看 7 天）。

鉴权：EUS 接口本身无鉴权（内网直连），不带 cookie。

输入：
  - app 映射：同目录 eus_app_map.json（app_id → {name, desc}）
输出：stdout 一段 markdown（## 近期业务系统使用（EUS））

用法：
  python3 eus_online.py --date today                  # 默认 lark 姓名自动过滤，近 7 天
  python3 eus_online.py --date today --days 7
  python3 eus_online.py --date 2026-06-29 --account zhouyujie  # 重名/特殊情况兜底
"""
import os
import json
import subprocess
import argparse
import requests
from datetime import datetime, timedelta

_DIR = os.path.dirname(os.path.abspath(__file__))
APP_MAP_FILE = os.path.join(_DIR, "eus_app_map.json")

URL = "https://eus.gz.cvte.cn/api/xiooview/dataview/getData"
DV_PROG_NO = "user_sys_online_time"
SOURCE_NO = "pgtest_eus"
PAGE_SIZE = 50000
TIMEOUT = 60

WEEK_CN = ["一", "二", "三", "四", "五", "六", "日"]


def resolve_date_obj(s: str):
    """返回 date 对象。支持 today/yesterday/YYYY-MM-DD。"""
    today = datetime.now().date()
    if s == "today":
        return today
    if s == "yesterday":
        return today - timedelta(days=1)
    return datetime.strptime(s, "%Y-%m-%d").date()


def get_lark_username() -> str:
    """从 lark-cli auth status 取当前用户姓名（identities.user.userName）。失败返回空串。"""
    try:
        out = subprocess.run(
            ["lark-cli", "auth", "status", "--verify"],
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode != 0 or not out.stdout:
            return ""
        d = json.loads(out.stdout)
        return (d.get("identities", {}).get("user", {}).get("userName") or "").strip()
    except Exception:
        return ""


def load_app_map() -> dict:
    try:
        with open(APP_MAP_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _cond(field, value, option="eq", conn="and"):
    return {"field": field, "value": value, "option": option, "type": "string", "conn": conn}


def query_eus_days(field: str, value: str, date_strs: list):
    """单次请求查多个日期：username/account eq + (start_time eq D1 OR start_time eq D2 OR ...)。

    用 or 串联多个日期的 eq 条件，避免逐日多次请求。自动翻页。
    field='account' 或 'username'。
    """
    if not date_strs:
        return []
    # 多日期 or 组：第一个条件 conn=and 桥接外层，其余 conn=or
    date_conds = []
    for i, d in enumerate(date_strs):
        date_conds.append(_cond("start_time", d, "eq", "and" if i == 0 else "or"))
    all_rows, page = [], 1
    while True:
        body = {
            "pageNum": page, "pageSize": PAGE_SIZE, "total": 50,
            "querys": [
                {"conn": "and", "conditions": [_cond(field, value)]},
                {"conn": "and", "conditions": date_conds},
                {"conditions": [], "conn": "and"},
            ],
            "dvProgNo": DV_PROG_NO, "sourceNo": SOURCE_NO, "sourceType": "pg",
        }
        r = requests.post(URL, json=body, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
        result = r.json()
        if str(result.get("status")) != "0":
            raise RuntimeError(f"EUS 接口失败: {result.get('message') or result}")
        data = result.get("data") or {}
        rows = data.get("data") or []
        all_rows.extend(rows)
        if not rows or len(rows) < PAGE_SIZE:
            break
        page += 1
    return all_rows


def app_label(app_id: str, app_map: dict) -> str:
    info = app_map.get(app_id) or {}
    name = (info.get("name") or "").strip()
    desc = (info.get("desc") or "").strip()
    if name and desc and name != desc:
        return f"{name}（{desc}）"
    return name or desc or (app_id[:8] + "…")


def main():
    ap = argparse.ArgumentParser(description="EUS 业务系统在线时长采集")
    ap.add_argument("--date", default="today", help="目标日期 today/yesterday/YYYY-MM-DD（默认 today）")
    ap.add_argument("--days", type=int, default=7, help="回看天数，从目标日期往前数（默认 7）")
    ap.add_argument("--name", default=None, help="用户姓名（如 周渝杰）；默认从 lark 自动取")
    ap.add_argument("--account", default=None, help="CVTE SSO 账号（如 zhouyujie），最唯一的兜底方式")
    args = ap.parse_args()

    end_date = resolve_date_obj(args.date)
    # 从最早到目标日期，逐日
    dates = [end_date - timedelta(days=i) for i in range(args.days - 1, -1, -1)]

    # 身份解析：account 优先 → name → lark 自动取 name
    if args.account:
        field, value = "account", args.account.strip()
    else:
        name = (args.name or "").strip() or get_lark_username()
        if not name:
            print("## 近期业务系统使用（EUS）\n")
            print("@@EUS_NEED_NAME@@")
            print("（无法自动获取用户姓名。请用 `--name <姓名>` 或 `--account <CVTE账号>` 指定。）")
            return
        field, value = "username", name

    app_map = load_app_map()

    # 单次 or 查询取回全部日期数据
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    try:
        all_rows = query_eus_days(field, value, date_strs)
    except Exception as e:
        print("## 近期业务系统使用（EUS）\n")
        print(f"（EUS 采集失败：{e}）")
        return

    # 按 startTime 分组
    per_day = {}
    for r in all_rows:
        ds = r.get("startTime") or ""
        per_day.setdefault(ds, []).append(r)

    print("## 近期业务系统使用（EUS）\n")
    print(f"用户 **{value}** · 近 {args.days} 天（{dates[0].strftime('%Y-%m-%d')} ~ {dates[-1].strftime('%Y-%m-%d')}）\n")

    today_str = datetime.now().date().strftime("%Y-%m-%d")
    today_rows = per_day.get(today_str, [])
    grand_total = 0.0
    grand_count = 0

    for d in dates:
        ds = d.strftime("%Y-%m-%d")
        rows = per_day.get(ds, [])
        total = sum(float(r.get("sum") or 0) for r in rows)
        grand_total += total
        grand_count += len(rows)
        wd = WEEK_CN[d.weekday()]
        if rows:
            rows.sort(key=lambda r: float(r.get("sum") or 0), reverse=True)
            print(f"**{ds}（周{wd}）** — {len(rows)} 个应用 · {total:.1f} 分钟")
            for r in rows:
                app_id = r.get("appId", "")
                mins = float(r.get("sum") or 0)
                print(f"  - {app_label(app_id, app_map)} — {mins:.1f} 分钟")
        else:
            tag = ""
            if ds == today_str:
                tag = "（当天数据通常因 EUS 系统更新延迟尚未入库，属正常）"
            print(f"**{ds}（周{wd}）** — 无在线记录{tag}")
        print()

    # 当天 0 条时的全局提示
    if not today_rows:
        print(f"> ⚠️ 今天（{today_str}）暂无 EUS 在线记录：EUS 系统通常有 1 天左右的数据更新延迟，"
              f"当天使用时长往往次日才会入库。可明天用 `--date yesterday` 补查，或参考上方近 7 天数据。\n")

    print(f"> 近 {args.days} 天合计：{grand_count} 条记录 · {grand_total:.1f} 分钟（约 {grand_total/60:.1f} 小时）")


if __name__ == "__main__":
    main()
