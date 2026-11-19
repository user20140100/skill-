# 数据源参考（data-sources）

码龙日报各数据源的精确命令、字段与边界。collect.sh 已封装，本文件供调试/扩展参考。

## 通用
- 我的 open_id：`lark-cli auth status --verify` → `.identities.user.openId`（user 身份）。
- 日期变量：`D`=当日 `YYYY-MM-DD`、`D2`=次日；聊天用 ISO 带时区 `+08:00`，drive 用纯日期。

## 1. 飞书日历（会议）
```bash
lark-cli calendar +agenda --as user --start "$D" --end "$D" --format pretty
```
- scope：`calendar:calendar.event:read`；必须 `--as user`，bot 身份返回空。
- 无日程时输出 `No events in this time range.`

## 2. 飞书聊天（我发出的消息）
```bash
lark-cli im +messages-search --query '' --sender "$ME" \
  --start "${D}T00:00:00+08:00" --end "${D}T23:59:59+08:00" \
  --page-size 50 --page-all --format pretty
```
- scope：`search:message`；user-only。
- `--query ''` 空（活动回顾不要塞关键词）；按时间范围 + sender 收敛。
- 工作总结务必 `--page-all` 翻完，单页不够。
- pretty 表格含 applink/position 噪音列，collect.sh 已 `grep -vE 'applink|message_position'`。

## 3. 飞书聊天（@我的消息）
```bash
lark-cli im +messages-search --query '' --is-at-me \
  --start "${D}T00:00:00+08:00" --end "${D}T23:59:59+08:00" --format pretty
```
- 反映别人派给我的任务/被点名讨论，补充工作输入面。

## 4. 飞书文档（今日编辑/创建）
```bash
# 我编辑过
lark-cli drive +search --mine --edited-since "$D" --edited-until "$D2" --format pretty
# 我创建
lark-cli drive +search --created-by-me --created-since "$D" --created-until "$D2" --format pretty
```
- `--mine`=我 owner；`--created-by-me`=我原创创建；`--edited-since/until`/`--created-since/until` 支持绝对日期。
- `my_edit_time` 为小时级聚合，跨日 since/until 不受影响。

## 5. Claude Code/Codex 开发活动（claude_sessions.py）
- 数据源：`~/.claude/projects/<dashed-path>/*.jsonl`，每行一条 JSON 事件。
- Codex 数据源：`~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`，按目标日期扫描；会话工作目录取 `session_meta.payload.cwd`，标题取 `~/.codex/session_index.jsonl` 的 `thread_name`。
- 关键字段：
  - `type`：`user`/`assistant`/`ai-title`/`system`/`attachment` 等
  - `timestamp`：ISO8601 UTC（`...Z`），按本地日期过滤
  - `cwd`：记录当时的工作目录（真实路径，用于聚合活跃项目）
  - `ai-title`→`aiTitle`：会话标题
  - `user`/`assistant`→`message.content`：内容（str 或 list；list 含 `text`/`tool_use`/`tool_result` 块）
  - `tool_use`→`name`：工具名（Bash/Edit/Write/Read/Task/WebSearch...）
- 过滤规则：排除 `tool_result`（工具结果不是用户输入）、系统注入（`<system-reminder>`/`<command-name>` 等）、超长粘贴。
- 末尾输出 `@@ACTIVE_DIRS@@\t<dir1>\t<dir2>`，collect.sh 据此跑 git log。
- Codex 只将 `response_item` 纳入活动时长；用户输入读取 `message` 的 `input_text`，工具调用读取 `function_call`/`custom_tool_call`。两类会话统一按专注片段计算，并标注来源，避免把系统事件和工具结果误当成用户工作。

## 6. Git 提交
对当日活跃项目目录：
```bash
git -C "<dir>" log --all --since="${D} 00:00" --until="${D} 23:59" --pretty=format:"- %h %an: %s"
```
- 仅对 Claude Code/Codex 当日活跃的目录执行，避免全盘扫描噪音。

## 7. git-ai（可选增强，默认不依赖）
- 已装但 `git-ai search --since` 未实现、`prompts.db` 常空；如需启用：`git-ai prompts --since 1`（相对天数）。
- 代码提交用原生 `git log` 最可靠。

## 8. 专注时长估算（claude_sessions.py，精力占比来源）
精力占比基于 Claude Code/Codex 会话活动**估算**，非精确计时：
- 取当天每个会话所有记录的 timestamp，排序。
- 相邻记录间隔 ≤ `--gap-minutes`（默认 15）归为同一**专注片段**；超过则切断（视为离开键盘）。
- 片段时长 = 末条 − 首条；单条交互（孤立记录）记 `--min-action-minutes`（默认 1 分钟）。
- 按 cwd 聚合到项目、按 aiTitle 聚合到任务，算占比。

口径与局限：
- 只反映 Claude Code/Codex 内的开发投入，**不含**会议（日历）、飞书聊天、线下支持。
- 单条交互真实时长不可知（一次复杂 Bash 可能数分钟），1 分钟为保守均值。
- gap 阈值影响结果：调小（如 5min）更严格、总时长下降；调大（如 30min）更宽松。
- 调参：`claude_sessions.py --gap-minutes 10 --min-action-minutes 2`。

### 会议并入与去重（重要，避免双计）
- 会议来自 `calendar +agenda --format json`（collect.sh 采成临时 JSON 传给 `--meetings-json`）。
- **会议优先去重**：Claude Code/Codex 专注片段与会议区间重叠的部分归「会议」、从开发时长扣除——避免开会时边用开发工具被双计。
- 全天总精力 = 会议并集时长 + Claude Code/Codex 净开发时长；去重**守恒**（重叠时间从开发时长转会议，总精力不变，仅占比重分配）。
- 会议区间自身也做并集，避免会议彼此重叠重复计。
- 已验证：注入一场与 CC 重叠的会议，总精力守恒、CC 净时长相应下降、会议出现占比。

## 9. EUS 业务系统在线时长（eus_online.py）

业务系统使用时长（采购管理/SCM、EUS、资源中心等各应用当日在线分钟数），补日报"业务系统使用"维度。

- **接口**：`POST https://eus.gz.cvte.cn/api/xiooview/dataview/getData`（内网，**无鉴权**，不带 cookie）。
- **过滤格式**：外层 key 为 `querys`（英文复数，带 s），每个条件用 `field`（英文）+ `option`（仅 `eq`；gte/lte 服务端报 `finnalOption is not a function`）。按 `username`（lark 姓名）+ `start_time` 当天 eq 过滤。
- **时间范围**：`--days N`（默认 7），从 `--date` 往前数 N 天，**单次请求**用 `conn:"or"` 串联多个 `start_time eq` 一次查回（N 天 = 1 次请求），按天分组展示。EUS 系统有约 1 天数据更新延迟，**当天使用时长往往次日才入库**，故默认回看近 7 天而非仅当天；当天无记录时自动提示"系统更新延迟，属正常"。
- **用户身份解析**：默认从 `lark-cli auth status --verify` 取 `identities.user.userName`（如"周渝杰"）作 EUS `username` 过滤，零询问。CVTE 姓名重名时 EUS 在名字加尾缀区分（如"曹晓飞15769"），与 lark 姓名一致不冲突。`--account <SSO账号>` 作最唯一兜底；取不到姓名时输出 `@@EUS_NEED_NAME@@`。
- **请求体**：`pageNum/pageSize/total/querys/dvProgNo=user_sys_online_time/sourceNo=pgtest_eus/sourceType=pg`。
- **响应**：`data.data` 为行数组（每行一个应用一条记录，含 `appId/username/account/sum/startTime/minStartTime/maxEndTime`）；**`data.total` 是假值**（=pageSize+1，仅"还有更多"信号），不可信，分页用"本页返回 < pageSize"。
- **app 名映射**：`scripts/eus_app_map.json`（app_id → {name, desc}），由 `eus_app_data.csv` 转换，**已剥离 app_secret / gitlab token**。
- **单位**：`sum` 字段为**分钟**。
- **容错**：接口失败只输出提示，不阻断日报。
- 注意：`sourceNo=pgtest_eus` 是测试库，数据含大量脏日期（年份 9223/8223/2102 等），但当天 eq 过滤不受影响。

## 排错

| 现象 | 原因 | 处理 |
|---|---|---|
| 聊天段"未获取到 open_id" | auth status 解析失败 | `collect.sh --me <open_id>` 显式传入 |
| 某源"采集失败" | 网络/权限/scope 缺失 | 单独跑该命令看报错；缺 scope 用 `lark-cli auth login --scope <x>` |
| Claude Code 段为空 | 当日无会话 / projects 目录非默认 | 确认 `~/.claude/projects`；`claude_sessions.py --projects-dir <path>` |
| Git 段为空 | 当日无提交（正常）或目录非 git 仓库 | 属正常，开发活动以会话为准 |
| EUS 段含 `@@EUS_NEED_NAME@@` | lark 取不到用户姓名 | `collect.sh --eus-account <CVTE账号>` 或 `--name <姓名>` 重跑 |
| EUS 段"采集失败" | 内网不通 / 接口异常 | 单独跑 `eus_online.py --account <acc> --date <d>` 看报错；确认在 CVTE 内网 |
| EUS 当天无记录（近 7 天有历史） | EUS 约 1 天数据更新延迟，当天时长次日才入库 | 属正常；可次日用 `--date yesterday` 补查当天 |
