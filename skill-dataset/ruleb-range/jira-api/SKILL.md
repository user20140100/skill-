---
name: jira-api
description: >-
  Jira API 基础 skill：通过 curl 直接调用 Jira REST API。 支持查 issue、评论、工时、JQL 查询、创建
  issue、月度汇总等 15+ 操作。
trigger_keywords:
  - jira
  - issue
  - 工时
  - 备注
  - JQL
  - 工单
  - 缺陷
  - 单子
version: '1.1'
author: yexiaojie
---

# Jira API Skill

通过 curl 直接调用 Jira REST API v2，无需 MCP Server。

## Setup

执行任何 API 调用前，先读取凭据：

```bash
cat ~/.claude/skills/jira-api/credentials.json
```

从 JSON 中提取 `JIRA_BASE_URL` 和 `JIRA_PAT` 的值，后续所有 curl 请求中直接使用字面量（不要用 shell 变量，避免管道/子 shell 中展开失败）：

```bash
curl -s -H "Authorization: Bearer <PAT字面量>" -H "Content-Type: application/json" "<BASE_URL字面量>/rest/api/2/..."
```

> **注意**：下面的示例模板中 `$JIRA_PAT` / `$JIRA_BASE_URL` 是占位符，执行时务必替换为从 credentials.json 读取的字面量值。

## 操作列表

### 1. 连接测试

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/serverInfo"
```

### 2. 当前用户

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/myself"
```

### 3. 查 Issue

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY"
```

提取关键字段：`key`, `summary`, `status.name`, `assignee.displayName`, `priority.name`, `created`, `updated`, `description`。

自定义字段说明：
- `customfield_10505`：开发工程师
- `customfield_10002`：故事点
- `customfield_10303`：难易程度
- `customfield_12003`：**要求完成时间**（即用户所说的"到期"/"截止"，优先使用此字段而非 `duedate`）

### 4. Issue 变更历史

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY?expand=changelog" | jq '.changelog.histories'
```

### 5. 创建 Issue

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" -H "Content-Type: application/json" \
  -X POST "$JIRA_BASE_URL/rest/api/2/issue" \
  -d '{
    "fields": {
      "project": {"key": "PROJECT_KEY"},
      "summary": "标题",
      "issuetype": {"name": "任务"},
      "description": "描述（可选）",
      "assignee": {"name": "username（可选）"},
      "customfield_10505": {"name": "developer_username（可选）"}
    }
  }'
```

### 6. 获取评论

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY/comment?maxResults=50&orderBy=-created"
```

### 7. 添加评论

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" -H "Content-Type: application/json" \
  -X POST "$JIRA_BASE_URL/rest/api/2/issue/$KEY/comment" \
  -d '{"body": "评论内容"}'
```

### 8. 获取工时

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY/worklog"
```

### 9. 添加工时

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" -H "Content-Type: application/json" \
  -X POST "$JIRA_BASE_URL/rest/api/2/issue/$KEY/worklog" \
  -d '{
    "timeSpentSeconds": 3600,
    "comment": "工作内容（可选）",
    "started": "2026-05-15T10:00:00.000+0800"
  }'
```

`started` 可选，不填则默认当前时间。

### 10. 更新工时

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" -H "Content-Type: application/json" \
  -X PUT "$JIRA_BASE_URL/rest/api/2/issue/$KEY/worklog/$WORKLOG_ID" \
  -d '{
    "timeSpentSeconds": 7200,
    "comment": "更新后的备注（可选）",
    "started": "2026-05-15T10:00:00.000+0800"
  }'
```

### 11. JQL 查询

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" -H "Content-Type: application/json" \
  -X POST "$JIRA_BASE_URL/rest/api/2/search" \
  -d '{
    "jql": "YOUR_JQL_HERE",
    "maxResults": 50,
    "fields": ["key","summary","status","assignee","priority","created","updated","customfield_10505","customfield_12003","duedate"]
  }'
```

### 12. 本周到期（Preset）

**注意：「到期」= `customfield_12003`（要求完成时间），不要用 `duedate`。**
**JQL 中不能用 `developer`，改用 `"cf[10505]"`。**

JQL:
```
"cf[10505]" = currentUser() AND "cf[12003]" >= startOfWeek() AND "cf[12003]" <= endOfWeek() AND resolution = Unresolved ORDER BY "cf[12003]" ASC
```

### 13. 本月已解决（Preset）

JQL:
```
developer = currentUser() AND statusCategory = Done AND resolved >= startOfMonth() ORDER BY resolved DESC
```

### 14. 我的未解决（Preset）

JQL:
```
developer = currentUser() AND resolution = Unresolved ORDER BY updated DESC
```

### 15. 按时间段查询

JQL:
```
developer = currentUser() AND updated >= "YYYY-MM-DD" AND updated <= "YYYY-MM-DD" ORDER BY updated DESC
```

### 16. 获取关联 GitLab 链接

从三个来源收集：

```bash
# Remote Links
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY/remotelink"

# 评论中提取
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY/comment" | jq -r '.comments[].body' | grep -oE 'https://gitlab[^\s)]*'

# 工时备注中提取
curl -s -H "Authorization: Bearer $JIRA_PAT" "$JIRA_BASE_URL/rest/api/2/issue/$KEY/worklog" | jq -r '.worklogs[].comment // empty' | grep -oE 'https://gitlab[^\s)]*'
```

### 17. 月度汇总

组合 JQL 查询 + 工时聚合：

1. 用 JQL 查出时间范围内有活动的 issue
2. 对每个 issue 获取 worklog
3. 按 issue 汇总工时，计算总工时

默认时间范围：上月26日 ~ 本月25日。

### 18. 用户工时统计

同月度汇总逻辑，聚焦于工时数据：

1. JQL 查出相关 issue
2. 汇总每日/每周工时
3. 输出统计表格

### 19. 转"测试中"流程（新建 → 处理中 → 测试中）

需两步流转，且有前置条件：

1. **新建 → 处理中**：transition id `71`，无必填字段
2. **处理中 → 测试中**：transition id `91`，需填以下必填字段：
   - `customfield_11006`（测试环境）：文本，如 `"整机测试"`
   - `customfield_12007`（导入的分支）：多选 checkbox，如 `[{"id":"21203"}]`（系统-develop）
   - `customfield_19201`（测试方法）：文本，如 `"功能验证"`
   - `customfield_19202`（任务描述）：文本，如 `"按需求完成开发"`
   - `customfield_19204`（自检结论）：文本，如 `"自检通过"`
   - `worklog`（耗费时间）：通过 update 添加，如 `"update":{"worklog":[{"add":{"timeSpent":"1h"}}]}`
3. **前置条件**：`customfield_12009`（规格描述 checklist）所有项必须 `checked: true`，否则流转会 400。先 GET checklist → 全部设 checked=true → PUT 更新，再执行 transition。

## 通用规则

- 所有响应用 `jq` 格式化，只展示关键字段（无 jq 时用 python3 替代）
- JQL 中**不能用 `developer`**，必须用 `"cf[10505]"` 匹配开发工程师（`developer` 字段在此 Jira 实例不可用）
- 用户说「到期」「截止」「要求完成」时，均使用 `customfield_12003`（要求完成时间），而非 `duedate`
- 更新 `customfield_12003` 时使用 PUT `/rest/api/2/issue/$KEY`，body: `{"fields": {"customfield_12003": "YYYY-MM-DDT09:00:00.000+0800"}}`
- 分页：默认 maxResults=50，需更多时增大或用 `startAt` 翻页
- 时间格式：ISO 8601，带时区 `+0800`
- 出错时展示 HTTP status 和 error message
- issue key 从用户消息或 URL (`https://jira.cvte.com/browse/XXX-123`) 中提取
