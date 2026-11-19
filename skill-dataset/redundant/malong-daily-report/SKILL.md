---
name: malong-daily-report
description: >-
  码龙日报：一键采集多源信息（飞书日历/聊天/文档 + 当日 Claude Code 会话与 git
  提交），总结为简洁工作日报（含会议+开发精力占比，会议优先去重），存档到 ~/.dailylog/<日期>-工作日报.md
  并上传飞书个人空间。触发：/malong-daily-report
  [日期]，或用户说「生成今日/X日工作日报」「写日报」「整理今天的工作」「总结某天的工作」。
version: 1.0.1
author: zhaodongsheng
license: MIT
tags:
  - 日报
  - 工作日报
  - daily-report
  - 飞书
  - lark
  - Claude Code
  - 精力管理
  - energy
  - productivity
agents:
  - claude-code
  - cursor
  - codex
  - gemini
  - opencode
  - workagent
metadata:
  requires:
    bins:
      - lark-cli
      - python3
---

# 码龙日报（malong-daily-report）

把每天散落在飞书日历、聊天、文档、代码开发、线下支持等工作痕迹，一键采集并总结成简洁工作日报，本地存档 + 上传飞书个人空间。

## 何时使用

用户输入 `/malong-daily-report`，或说「生成今日工作日报」「写个日报」「整理一下今天的工作」「总结 X 月 X 日的工作」。

## 前置条件

- `lark-cli` 已 `auth login` 为 user 身份，具备 `search:message`、`calendar:calendar.event:read`、`drive` 搜索等权限。token `needs_refresh` 会自动刷新，无需手动处理。
- 首次使用时确认上传目标：默认飞书**个人空间根目录**；如需指定子目录，先取得 `folder_token`。

## 完整流程

### 1. 确定日期
用户未指定 → 默认 `today`；支持 `yesterday` 或 `YYYY-MM-DD`。

### 2. 采集素材（由脚本完成，核心）
```bash
bash <本 skill 目录>/scripts/collect.sh --date <YYYY-MM-DD>
```
脚本采集以下源（**每源独立容错，互不影响**）：

| 段 | 来源 |
|---|---|
| 今日会议 | 飞书日历 `calendar +agenda` |
| 我发出的消息 | 飞书聊天 `im +messages-search --sender <我>` |
| @我的消息 | 飞书聊天 `im +messages-search --is-at-me` |
| 今日编辑/创建文档 | 飞书云空间 `drive +search --mine/--created-by-me` |
| 代码与开发 | Claude Code 会话 `claude_sessions.py` + 活跃项目 `git log` |

选项：`--no-lark`（离线仅代码源）、`--no-code`（仅飞书源）、`--me <open_id>`（默认自动获取）。

### 3. 提炼总结（由你完成）
读取素材输出，**过滤非工作内容**（挪车、约球、美容、私人感慨、纯寒暄），按主题归类：
项目推进 / 会议 / 问题答疑与跟进 / 文档撰写 / 代码开发 / 线下支持他人 / 团队管理与协调。

> 代码开发部分重点参考 Claude Code 会话标题与用户请求 —— 它最能反映当日实际产出（写了哪些文档、做了哪些技术决策、验证了什么）。

### 4. 生成日报 Markdown
精力占比放最前（一眼看到时间花在哪），其余按主题分条。结构：
```
# 工作日报 · <日期>（星期X）

## ⏱ 精力占比（估算）
- 📅 会议 — Xh（Y%）（如有）
- 💻 项目A — Xh（Y%）
- 💻 项目B — Xh（Y%）
> 会议 + Claude Code 净开发（CC 已扣除与会议重叠时段，不重复计）；不含聊天、线下支持。

## 一、今日完成
- 分条，每条一个事项 + 关键产出/结论（重要任务可标注估算耗时）
## 二、进行中 · 思考
## 三、明日计划
```

### 5. 本地存档
```bash
mkdir -p ~/.dailylog
```
写入 `~/.dailylog/<YYYY-MM-DD>-工作日报.md`。

### 6. 上传飞书个人空间
`drive +import` 的 `--file` **必须是相对路径**（限当前目录内），因此先 cd 到 ~/.dailylog（用子 shell 隔离）：
```bash
( cd ~/.dailylog && lark-cli drive +import --type docx \
    --file ./<YYYY-MM-DD>-工作日报.md --name "工作日报 · <YYYY-MM-DD>" )
```
从返回 JSON 的 `data.url` 取文档链接。指定子目录时加 `--folder-token <token>`。

### 7. 回显
在对话展示最终日报正文 + 本地路径 + 飞书文档链接。

## 关键脚本

| 文件 | 作用 |
|---|---|
| `scripts/collect.sh` | bash 主编排：解析日期/身份，采集飞书 + 代码各源，输出分段 markdown 素材 |
| `scripts/claude_sessions.py` | 扫描 `~/.claude/projects/*/*.jsonl` 提取 CC 开发活动与专注片段；接收 `--meetings-json` 并入飞书会议，**重叠时段会议优先去重**；末尾 `@@ACTIVE_DIRS@@` 供 collect.sh 跑 git log |

## 边界

- 只读采集，不缓存任何 token/密钥；上传为**创建新文档**（非覆盖，无 high-risk）。
- 飞书源依赖网络与 user token；离线用 `--no-lark` 仍可得代码/开发部分。
- 时区固定 `+08:00`（`collect.sh` 的 `TZ_OFFSET`，跨时区可改）。
- 各数据源精确命令、字段与排错见 [`references/data-sources.md`](references/data-sources.md)。
