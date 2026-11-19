---
name: malong-daily-report-eus
description: >-
  码龙日报：一键采集多源信息（飞书日历/聊天/文档 + EUS 业务系统在线时长 + 当日 Claude Code/Codex 会话与 git
  提交），总结为简洁工作日报（含会议+开发精力占比，会议优先去重），存档到 ~/.dailylog/YYYY-MM-DD-工作日报.md
  并上传飞书个人空间。触发：/malong-daily-report
  [日期]，或用户说「生成今日/X日工作日报」「写日报」「整理今天的工作」「总结某天的工作」。
license: MIT
metadata:
  requires:
    bins:
      - lark-cli
      - python3
author: zhouyujie
version: 1.0.4
---

# 码龙日报（malong-daily-report-eus）

把每天散落在飞书日历、聊天、文档、代码开发、线下支持等工作痕迹，一键采集并总结成简洁工作日报，本地存档 + 上传飞书个人空间。

## 何时使用

用户输入 `/malong-daily-report-eus`，或说「生成今日工作日报」「写个日报」「整理一下今天的工作」「总结 X 月 X 日的工作」。

## 前置条件

- `lark-cli` 已 `auth login` 为 user 身份，具备 `search:message`、`calendar:calendar.event:read`、`drive` 搜索等权限。token `needs_refresh` 会自动刷新，无需手动处理。
- 首次使用时确认上传目标：默认飞书**个人空间根目录**；如需指定子目录，先取得 `folder_token`。
- **EUS 业务系统源**：默认自动从 `lark-cli auth status` 取当前用户姓名（如"周渝杰"）作为 EUS `username` 过滤，**全程零询问**。CVTE 姓名重名时 EUS 在名字加尾缀区分（如"曹晓飞15769"），lark 姓名与 EUS username 一致，不冲突。重名/异常等特殊情况可用 `--eus-account <CVTE账号>` 兜底。EUS 接口本身无鉴权，仅限内网。
- **EUS 时间范围**：默认回看**近 7 天**（`--days`，可调）。EUS 系统通常有约 1 天的数据更新延迟，**当天使用时长往往次日才入库**——因此日报默认展示近 7 天趋势而非仅当天；当天无记录时脚本自动提示"系统更新延迟，属正常"，并可次日用 `--date yesterday` 补查。

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
| 代码与开发 | Claude Code/Codex 会话 `claude_sessions.py` + 活跃项目 `git log` |
| 业务系统使用 | EUS 在线时长 `eus_online.py`（按 lark 姓名 + 近 7 天，无鉴权） |

选项：`--no-lark`（离线仅代码源）、`--no-code`（仅飞书源）、`--no-eus`（跳过 EUS）、`--me <open_id>`（默认自动获取）、`--eus-account <acc>`（EUS 用 account 兜底）。

### 3. 提炼总结（由你完成）
读取素材输出，**过滤非工作内容**（挪车、约球、美容、私人感慨、纯寒暄），按主题归类：
项目推进 / 会议 / 问题答疑与跟进 / 文档撰写 / 业务系统使用 / 代码开发 / 线下支持他人 / 团队管理与协调。

> 代码开发部分重点参考 Claude Code 与 Codex 会话标题、用户请求和工具活动 —— 它们最能反映当日实际产出（写了哪些文档、做了哪些技术决策、验证了什么）。两类会话均纳入精力占比；同一会话的重复记录只按专注片段计算。

> ⚠️ **EUS 业务系统使用段必须保留逐日逐应用明细，严禁压缩成一句话汇总** —— 明细是采集脚本特意取回的数据，用户明确要求保留，丢明细就是 bug。格式硬要求：
> - 表格三列：`日期 | 在线时长 | 应用明细`，**逐日一行**；应用明细用「应用名 时长」点列拼接（如 `采购管理 61.8m · EUS 41.1m · CPLM 12.1m`），保留素材里的每个应用与分钟数，不得合并/省略。
> - 表前一句汇总（近 N 天合计分钟数 + 主应用），表后一句趋势（峰值日、主应用切换）。
> - 当天无记录时，表格里单列一行「暂无 | 系统更新延迟，数据通常次日入库，可次日补查」，照搬脚本提示，不要删。
> - 无在线记录的休息日也要列出行（`— | 无在线记录`），保持近 N 天连续可读。

### 4. 生成日报 Markdown
精力占比放最前（一眼看到时间花在哪），其余按主题分条。结构：
```
# 工作日报 · <日期>（星期X）

## ⏱ 精力占比（估算）
- 📅 会议 — Xh（Y%）（如有）
- 💻 项目A — Xh（Y%）
- 💻 项目B — Xh（Y%）
> 会议 + Claude Code/Codex 净开发（两类开发活动均已扣除与会议重叠时段，不重复计）；不含聊天、线下支持。

## 一、今日完成
- 分条，每条一个事项 + 关键产出/结论（重要任务可标注估算耗时）
- 含「业务系统使用（EUS · 近 N 天明细）」子段，**按第 3 步规则用表格保留逐日逐应用明细**（含休息日空行 + 当天延迟提示行），不得仅给汇总
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
| `scripts/claude_sessions.py` | 扫描 `~/.claude/projects/*/*.jsonl` 与 `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`，提取 Claude Code/Codex 开发活动与专注片段；接收 `--meetings-json` 并入飞书会议，**重叠时段会议优先去重**；末尾 `@@ACTIVE_DIRS@@` 供 collect.sh 跑 git log |
| `scripts/eus_online.py` | 查 EUS 接口（无鉴权）取当前用户近 N 天（默认 7）各业务系统在线时长（分钟），按天分组输出 markdown 段；默认从 lark 自动取姓名过滤，`--account` 兜底，取不到姓名时输出 `@@EUS_NEED_NAME@@`；当天无记录时提示系统更新延迟 |
| `scripts/eus_app_map.json` | EUS appId → {name, desc} 映射（52 应用，已剥离 app_secret/gitlab token），让输出可读 |

## 边界

- 只读采集，不缓存任何 token/密钥；上传为**创建新文档**（非覆盖，无 high-risk）。
- 飞书源依赖网络与 user token；离线用 `--no-lark` 仍可得代码/开发部分。
- 时区固定 `+08:00`（`collect.sh` 的 `TZ_OFFSET`，跨时区可改）。
- 各数据源精确命令、字段与排错见 [`references/data-sources.md`](references/data-sources.md)。
