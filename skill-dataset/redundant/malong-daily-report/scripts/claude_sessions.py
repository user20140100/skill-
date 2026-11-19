#!/usr/bin/env python3
"""
claude_sessions.py — 扫描 Claude Code 会话历史 + 飞书会议，产出当日精力看板与开发活动明细。

数据源:
  - Claude Code 会话: ~/.claude/projects/<dashed>/*.jsonl（每行一条 JSON 事件）
  - 飞书会议(可选): `calendar +agenda --format json` 的输出文件，经 --meetings-json 传入

精力看板口径（去重，避免双计）:
  - 把同一天同一会话里相邻记录间隔 ≤ gap 阈值 的归为一个「专注片段」。
  - CC 专注片段与会议区间重叠时，**重叠部分归会议、从 CC 扣除**（会议优先）。
  - 全天总精力 = 会议并集时长 + CC 净开发时长。
  - 注：是估算而非精确计时；只覆盖 CC 开发 + 会议，不含聊天/线下。

输出: markdown 段（stdout）；末尾 @@ACTIVE_DIRS@@<tab>dir1<tab>dir2... 供 collect.sh 跑 git log。
依赖: 纯标准库

用法:
    python3 claude_sessions.py --date 2026-06-16
    python3 claude_sessions.py --date today --meetings-json /tmp/meetings.json --gap-minutes 15
"""
import argparse
import glob
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# 本地时区（用系统当前时区推断）
LOCAL = datetime.now().astimezone().tzinfo

# 视为系统注入/非真实用户输入的前缀标记
SYS_MARKERS = (
    "<system-reminder>", "<command-name>", "<command-message>", "<local-command",
    "Caveat:", "[Request interrupted", "<bash-input>", "<bash-stdout>",
)


def parse_date(s):
    today = datetime.now(LOCAL).date()
    if s == "today":
        return today
    if s == "yesterday":
        return today - timedelta(days=1)
    return datetime.strptime(s, "%Y-%m-%d").date()


def parse_ts(ts):
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def focus_segments(times, gap_seconds, min_action_minutes):
    """把排序后的时间戳切成专注片段，返回 [(start, end, minutes), ...]。
    相邻间隔 ≤ gap_seconds 视为同一片段；片段时长=末-首；单条交互记 min_action_minutes。"""
    if not times:
        return []
    segs, cur = [], [times[0]]
    for t in times[1:]:
        if (t - cur[-1]).total_seconds() <= gap_seconds:
            cur.append(t)
        else:
            segs.append(cur)
            cur = [t]
    segs.append(cur)
    out = []
    for s in segs:
        if len(s) == 1:
            t = s[0]
            out.append((t, t + timedelta(minutes=min_action_minutes), float(min_action_minutes)))
        else:
            d = (s[-1] - s[0]).total_seconds() / 60.0
            out.append((s[0], s[-1], d))
    return out


def subtract_meetings(seg_start, seg_end, meetings):
    """从区间 [seg_start, seg_end] 中扣除所有会议区间，返回剩余子区间 [(s, e), ...]。"""
    pieces = [(seg_start, seg_end)]
    for ms, me, _ in meetings:
        new = []
        for ps, pe in pieces:
            if me <= ps or ms >= pe:  # 不相交
                new.append((ps, pe))
            else:  # 相交：保留两侧不重叠部分
                if ms > ps:
                    new.append((ps, ms))
                if me < pe:
                    new.append((me, pe))
        pieces = new
    return pieces


def meetings_union_minutes(meetings):
    """会议区间并集时长（分钟），避免会议彼此重叠时重复计。"""
    if not meetings:
        return 0.0
    spans = sorted((s, e) for s, e, _ in meetings)
    total = 0.0
    cs, ce = spans[0]
    for s, e in spans[1:]:
        if s > ce:
            total += (ce - cs).total_seconds() / 60.0
            cs, ce = s, e
        else:
            ce = max(ce, e)
    total += (ce - cs).total_seconds() / 60.0
    return total


def load_meetings(path, target):
    """从 agenda JSON 文件解析当日会议，返回 [(start, end, summary), ...]。"""
    meetings = []
    if not path:
        return meetings
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        return meetings
    evs = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(evs, dict):
        evs = evs.get("events") or evs.get("items") or []
    for e in evs:
        if not isinstance(e, dict):
            continue
        st = e.get("start_time") or {}
        et = e.get("end_time") or {}
        sdt = parse_ts(st.get("datetime")) if isinstance(st, dict) else None
        edt = parse_ts(et.get("datetime")) if isinstance(et, dict) else None
        if not (sdt and edt) or edt <= sdt:
            continue
        if sdt.astimezone(LOCAL).date() != target:
            continue
        meetings.append((sdt, edt, e.get("summary") or "(无标题)"))
    meetings.sort(key=lambda x: x[0])
    return meetings


def extract_user_text(msg):
    c = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        texts, is_tool_result = [], False
        for b in c:
            if isinstance(b, dict):
                if b.get("type") == "tool_result":
                    is_tool_result = True
                elif b.get("type") == "text":
                    texts.append(b.get("text", ""))
            elif isinstance(b, str):
                texts.append(b)
        if is_tool_result:
            return None
        return "\n".join(t for t in texts if t) or None
    return None


def is_real_prompt(txt):
    if not txt:
        return False
    s = txt.strip()
    if not s:
        return False
    if any(m in s[:60] for m in SYS_MARKERS):
        return False
    if len(s) > 500:
        return False
    return True


def extract_tool_uses(msg):
    c = msg.get("content") if isinstance(msg, dict) else None
    names = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                names.append(b.get("name", "?"))
    return names


def short(path):
    home = os.path.expanduser("~")
    return path.replace(home, "~", 1) if path.startswith(home) else path


def hmm(minutes):
    minutes = int(round(minutes))
    h, m = divmod(minutes, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def main():
    ap = argparse.ArgumentParser(description="当日精力看板（Claude Code + 会议，去重）与开发活动明细")
    ap.add_argument("--date", default="today", help="today|yesterday|YYYY-MM-DD（默认 today）")
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--gap-minutes", type=int, default=15, help="专注片段切断阈值（分钟，默认 15）")
    ap.add_argument("--min-action-minutes", type=float, default=1.0, help="单条交互估算时长（分钟，默认 1）")
    ap.add_argument("--meetings-json", default="", help="飞书日历 agenda JSON 文件路径（可选）")
    args = ap.parse_args()

    target = parse_date(args.date)
    gap_seconds = args.gap_minutes * 60
    meetings = load_meetings(args.meetings_json, target)
    meeting_total = meetings_union_minutes(meetings)

    files = glob.glob(os.path.join(args.projects_dir, "*", "*.jsonl"))
    sessions = []
    for jf in files:
        try:
            fh = open(jf, encoding="utf-8")
        except Exception:
            continue
        title, sid, day_recs, times = None, None, [], []
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            t = o.get("type")
            if t == "ai-title" and o.get("aiTitle"):
                title = o["aiTitle"]
            if not sid and o.get("sessionId"):
                sid = o["sessionId"]
            ts = parse_ts(o.get("timestamp"))
            if not ts:
                continue
            if ts.astimezone(LOCAL).date() != target:
                continue
            day_recs.append(o)
            times.append(ts)
        fh.close()
        if not day_recs:
            continue
        times.sort()
        cwds = sorted({r.get("cwd") for r in day_recs if r.get("cwd")})
        prompts, tools = [], Counter()
        for r in day_recs:
            if r.get("type") == "user":
                txt = extract_user_text(r.get("message") or {})
                if is_real_prompt(txt):
                    prompts.append(txt.strip())
            elif r.get("type") == "assistant":
                tools.update(extract_tool_uses(r.get("message") or {}))
        # 专注片段 → 扣除会议 → 净时长
        segs = focus_segments(times, gap_seconds, args.min_action_minutes)
        net = 0.0
        for ss, se, _ in segs:
            for ps, pe in subtract_meetings(ss, se, meetings):
                net += (pe - ps).total_seconds() / 60.0
        sessions.append(dict(
            title=title or "(无标题)", sid=sid or os.path.basename(jf)[:8],
            cwds=cwds, prompts=prompts, tools=tools, n=len(day_recs), duration=net,
        ))

    out = [f"### 精力与开发活动（Claude Code + 会议）\n"]

    by_dir = defaultdict(list)
    for s in sessions:
        key = s["cwds"][0] if s["cwds"] else "(未知目录)"
        by_dir[key].append(s)
    dir_dur = {d: sum(s["duration"] for s in ss) for d, ss in by_dir.items()}
    cc_total = sum(dir_dur.values())
    grand_total = meeting_total + cc_total

    out.append(f"当日 {target}：{len(sessions)} 个 CC 会话、{len(by_dir)} 个项目目录、"
               f"{len(meetings)} 场会议；估算总精力 **{hmm(grand_total)}**（会议 {hmm(meeting_total)} + CC 净开发 {hmm(cc_total)}）。\n")

    # 精力占比看板
    out.append(f"**⏱ 精力占比（估算 · 会议优先去重，gap≤{args.gap_minutes}min）**")
    rows = []
    if meeting_total > 0:
        rows.append(("📅 会议", meeting_total))
    for d, dmin in sorted(dir_dur.items(), key=lambda x: -x[1]):
        if dmin > 0:
            rows.append(("💻 " + short(d), dmin))
    for label, dmin in rows:
        pct = (dmin / grand_total * 100) if grand_total else 0
        out.append(f"- {label} — {hmm(dmin)}（{pct:.0f}%）")
    if meeting_total > 0:
        out.append("")  # 会议标题明细
        out.append("  会议明细：")
        for ms, me, summary in meetings:
            mm = (me - ms).total_seconds() / 60.0
            hh = ms.astimezone(LOCAL).strftime("%H:%M")
            out.append(f"  - {hh} {summary} — {hmm(mm)}")
    out.append("")
    if meeting_total > 0:
        out.append("> CC 开发已扣除与会议重叠时段，不重复计入；总精力 = 会议 + CC 净开发。\n")

    # 任务耗时 Top（CC，去重后）
    task_dur = defaultdict(float)
    for s in sessions:
        task_dur[s["title"]] += s["duration"]
    top_tasks = [(t, dm) for t, dm in sorted(task_dur.items(), key=lambda x: -x[1]) if dm >= 5][:8]
    if top_tasks:
        out.append("**📌 CC 任务耗时 Top**（会话标题聚合，≥5 分钟，已去会议重叠）")
        for t, dm in top_tasks:
            out.append(f"- {t} — {hmm(dm)}")
        out.append("")

    # 项目明细
    for d, slist in sorted(by_dir.items(), key=lambda kv: -dir_dur[kv[0]]):
        total_tools = Counter()
        for s in slist:
            total_tools.update(s["tools"])
        out.append(f"#### {short(d)}（{len(slist)} 个会话，净 {hmm(dir_dur[d])}）")
        if total_tools:
            tstr = "、".join(f"{k}×{v}" for k, v in total_tools.most_common(8))
            out.append(f"- 工具使用: {tstr}")
        for s in sorted(slist, key=lambda x: -x["duration"]):
            out.append(f"- 会话「{s['title']}」（净 {hmm(s['duration'])}，{s['n']} 条记录）")
            for p in s["prompts"][:5]:
                p1 = p.replace("\n", " ").strip()
                if len(p1) > 110:
                    p1 = p1[:110] + "…"
                out.append(f"  - 请求: {p1}")
        out.append("")
    print("\n".join(out))

    active = sorted({d for d in by_dir if d and d != "(未知目录)"})
    print("@@ACTIVE_DIRS@@" + ("\t" + "\t".join(active) if active else ""))


if __name__ == "__main__":
    main()
