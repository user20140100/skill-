---
name: jira-log-assistant
description: "Analyze Android device issues reported in Jira: fetch issue details and log attachments, run log analysis via android-log-analysis skill, and post results back as a Jira comment. Use when the user provides a Jira issue ID or URL and asks for issue analysis, log analysis, Jira 日志分析, Jira 问题分析, or mentions analyzing a Jira ticket with logs."
author: zhonghongyu
---

# Jira Log Analysis Assistant (Jira 日志分析助手)

从 Jira issue 获取问题描述和日志附件，自动完成 Android 日志分析，并将分析报告回写到 Jira 评论。

---

## Phase 0: Prerequisites Check

按顺序检查，任一项失败则**停止并告知用户**。

### 0.1 Jira MCP 配置检查

验证 `jira` MCP 服务器已配置且可用：

```
调用 jira-get_jira_info 获取一个测试 issue（使用用户提供的 issue）
  ├─ 成功 → MCP 可用，继续
  └─ 失败 → 告知用户需在 Cursor MCP 设置中配置 jira 服务器，停止
```

### 0.2 Jira REST API Token 获取

Token 用于下载附件和回写评论（MCP 不支持这些操作）。

**读取顺序**：

1. 读取环境变量 `SKILL_JIRA_ASSISTANT_TOKEN`
2. 若为空，**必须要求用户提供**，提示：
   > 需要 Jira API Token 以下载附件和回写分析结果。
   > 请提供您的 Jira 个人访问令牌（Personal Access Token），或将其设置到环境变量 `SKILL_JIRA_ASSISTANT_TOKEN` 中。
3. 收到 token 后，用以下命令验证有效性：

```bash
curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" \
  "https://jira.cvte.com/rest/api/2/myself" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Token OK: {d.get(\"displayName\",\"?\")} ({d.get(\"name\",\"?\")})')
"
```

验证失败则要求重新提供，**不猜测、不跳过**。

---

## Phase 1: Parse Input & Fetch Issue

### 1.1 解析 Jira ID

从用户输入中提取 Jira Issue Key，支持两种格式：

| 输入格式 | 示例 | 提取结果 |
|---|---|---|
| Issue Key | `XBS250014-270` | `XBS250014-270` |
| Jira URL | `https://jira.cvte.com/browse/XBS250014-270` | `XBS250014-270` |

提取正则：`([A-Z][A-Z0-9_]+-\d+)`

### 1.2 获取 Issue 信息

使用 `jira-get_jira_info` MCP 工具获取 summary 和 description。

### 1.3 提取问题上下文

从 description 中提取以下信息（供日志分析阶段使用），缺失则标注"未提供"：

| 上下文项 | 说明 |
|---|---|
| 问题现象 | 用户观察到的表现 |
| 操作步骤 | 触发问题的操作流程 |
| 异常时间 | 问题发生的时间点或时间范围 |
| 应用/进程名称 | 涉及的应用包名或进程名 |
| 复现概率 | 必现/偶现/概率 |
| 设备信息 | 型号、序列号等 |

### 1.4 概括 Issue

用 2-3 句话概括问题，输出给用户确认。

---

## Phase 2: Download & Extract Attachments

### 2.1 获取附件列表

```bash
curl -s --max-time 30 \
  -H "Authorization: Bearer $TOKEN" \
  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}?fields=attachment"
```

### 2.2 筛选日志附件

按以下优先级筛选，忽略图片/视频等非日志文件：

| 优先级 | 文件特征 | 说明 |
|---|---|---|
| P0 | `bugreport*.zip`, `bugreport*.txt` | Android bugreport |
| P1 | `logcat*.log`, `logcat*.txt`, `*.log` | Logcat 日志 |
| P2 | `tombstone*`, `anr_*`, `traces.txt` | 崩溃/ANR 日志 |
| P3 | `dmesg*`, `last_kmsg*`, `kmsg*` | 内核日志 |
| P4 | `*.zip`, `*.gz`, `*.tar.gz` | 压缩包（可能含日志） |

若无日志附件，告知用户并停止。

### 2.3 下载与解压

```bash
WORK_DIR="jira_${ISSUE_KEY}"
mkdir -p "$WORK_DIR"

# 下载每个日志附件
curl -s --max-time 120 \
  -H "Authorization: Bearer $TOKEN" \
  -o "$WORK_DIR/$FILENAME" "$ATTACHMENT_CONTENT_URL"

# 解压 .zip / .gz
cd "$WORK_DIR" && unzip -o "$FILENAME" 2>/dev/null
```

工作目录结构：`jira_<ISSUE_KEY>/`

---

## Phase 3: Log Analysis

### 3.1 调用 android-log-analysis Skill

读取并执行 `android-log-analysis` Skill（路径：`/config/.cursor/skills/android-log-analysis/SKILL.md`）。

### 3.2 传递 Jira 上下文

将 Phase 1.3 提取的问题上下文作为 android-log-analysis 的 Optional Inputs：

| android-log-analysis 参数 | 来源 |
|---|---|
| Log path | Phase 2 的工作目录路径 |
| 时间范围 | Jira description 中的"异常时间" |
| 现象描述 | Jira summary + description 中的"实际结果" |
| 操作描述 | Jira description 中的"操作步骤" |
| 怀疑方向 | 根据现象和操作推断（可选） |

### 3.3 增强分析

在日志分析过程中，利用 Jira 上下文增强问题识别：

1. **进程聚焦**：若 Jira 提供了应用/进程名称，优先分析该进程的日志
2. **时间聚焦**：若 Jira 提供了异常时间，优先分析该时间窗口
3. **现象关联**：将日志中发现的异常与 Jira 描述的现象进行匹配验证
4. **操作链追溯**：根据操作步骤，在日志中追溯从操作触发到异常发生的事件链

---

## Phase 4: Upload Results to Jira

### 4.1 准备评论内容

将 android-log-analysis 输出的 `.md` 报告文件内容读取为评论正文。

在评论开头添加标识头：

```
{panel:title=AI 日志分析报告|borderColor=#0747A6|bgColor=#DEEBFF}
本报告由 Jira Log Analysis Assistant 自动生成。
分析时间: <YYYY-MM-DD HH:MM>
{panel}

<报告正文>
```

### 4.2 发送评论到 Jira

```bash
curl -s --max-time 30 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}/comment" \
  -d @- <<'PAYLOAD'
{
  "body": "<评论内容，需转义 JSON 特殊字符>"
}
PAYLOAD
```

**JSON 转义注意**：评论内容中的双引号、换行符、反斜杠需正确转义。建议使用 `python3 -c` 生成 JSON payload：

```bash
python3 -c "
import json, sys
content = open('$REPORT_FILE').read()
header = '{panel:title=AI 日志分析报告|borderColor=#0747A6|bgColor=#DEEBFF}\n本报告由 Jira Log Analysis Assistant 自动生成。\n分析时间: $(date \"+%Y-%m-%d %H:%M\")\n{panel}\n\n'
payload = json.dumps({'body': header + content})
sys.stdout.write(payload)
" | curl -s --max-time 30 \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -X POST \
  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}/comment" \
  -d @-
```

### 4.3 验证与通知

- 检查 HTTP 响应码（201 = 成功）
- 成功：告知用户评论已发布，附 Jira 链接
- 失败：显示错误信息，将报告文件路径告知用户作为备用

---

## Constraints

1. **Token 不可跳过** — 无有效 token 时必须停止，不使用其他认证方式
2. **日志附件必须存在** — 无日志附件时告知用户并停止，不凭空分析
3. **评论内容不编造** — 上传的评论内容必须完全来自日志分析报告
4. **Jira 域名** — 默认使用 `https://jira.cvte.com`，如用户提供的 URL 指向其他域名则使用该域名
5. **android-log-analysis Skill 为必要依赖** — 若该 Skill 不存在则告知用户并停止
6. **本地报告保留** — 即使上传成功，本地 `.md` 报告文件也保留不删除

## Error Handling

| 场景 | 处理 |
|---|---|
| Jira MCP 未配置 | 提示用户配置，停止 |
| Token 无效/过期 | 提示重新提供，不继续 |
| Issue 不存在 | 报告 issue key 无效，停止 |
| 无日志附件 | 告知用户该 issue 无日志文件，停止 |
| 附件下载失败 | 报告失败的附件，尝试其他附件 |
| 日志分析 Skill 缺失 | 提示用户安装 android-log-analysis Skill |
| 评论上传失败 | 显示错误，提供本地报告路径作为备用 |
