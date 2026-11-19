---
name: jira-batch-create
description: 从 Excel 批量创建/修改 Jira Issue，用于自动化测试 NG 问题登记和已有 Issue 批量修复
author: shishaoxian
version: 1.0.1
tags:
  - jira
  - batch
  - excel
  - automation
  - testing
---

# Jira 批量登记与修改 Skill

两大功能：
1. **批量创建**：从 Excel 测试结果提取 NG 问题，批量创建 Jira Issue
2. **批量修改**：对已创建的 Jira Issue 批量修改字段（标题、经办人、备注、标签等）

## 触发场景

**批量创建：**
- "批量创建 Jira Issue"
- "Excel 导入 Jira"
- "自动化测试结果登记到 Jira"
- "NG 问题批量登记"

**批量修改：**
- "批量修改 Jira Issue"
- "批量更新 Jira 标题"
- "批量修复 Jira 问题"
- "修改已创建的 Jira Issue"
- "批量修改经办人/标签/备注"

## 前置条件

### 1. mcp-atlassian 必须已配置

检查 `.mcp.json` 或 `.claude/settings.json` 中是否有 `atlassian` MCP server。

如果未配置，提供以下指引：

```json
// .mcp.json
{
  "mcpServers": {
    "atlassian": {
      "command": "/opt/homebrew/bin/mcp-atlassian",
      "args": [],
      "env": {
        "JIRA_URL": "https://your-jira-server.com",
        "JIRA_PERSONAL_TOKEN": "your-personal-access-token",
        "JIRA_SSL_VERIFY": "false",
        "TOOLSETS": "all"
      }
    }
  }
}
```

关键配置说明：
- `JIRA_PERSONAL_TOKEN`：不是 `JIRA_TOKEN`，必须是 `JIRA_PERSONAL_TOKEN`
- `JIRA_SSL_VERIFY`：自建 Jira 需设为 `false`
- `TOOLSETS`：必须设为 `all`，否则工具列表为空
- 安装：`pip3 install mcp-atlassian --break-system-packages`

### 2. 必须有包含测试结果的 Excel 文件

支持格式：.xlsx

## 工作流程

### Step 1: 收集基础信息（必须全部确认）

使用 AskUserQuestion 收集以下信息：

**必填信息：**

| 信息 | 示例 | 用途 |
|------|------|------|
| Excel 文件路径 | `docs/bug/xxx.xlsx` | 读取测试结果 |
| 平台名称 | `Platform-A` | Summary 格式 `[AI][平台]...` |
| 客户名称 | `Customer-X` | Summary 格式 `[AI][平台][客户]...` |
| Jira 项目 key | `PROJ` | Issue 所属项目 |
| 经办人邮箱 | `user@example.com` | Issue assignee |
| 状态列筛选值 | `NG` | 用于识别失败问题 |

**可选配置（有默认值）：**

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 导入隐藏行 | 否 | 是否包含 Excel 中被隐藏的行 |
| 优先级 | 高 | Issue priority |
| 严重程度 | 由用户指定 | 自定义字段（通过 search_fields 动态查找） |
| 标签 | 自动化测试问题 | Issue labels |
| 问题类型 | 缺陷 | Issue type |

### Step 2: 读取 Excel 并智能识别列

使用 Python openpyxl 读取 Excel，自动识别列映射。

**隐藏行处理：**
- 如果用户选择不导入隐藏行（默认），使用 openpyxl 检查行的 `hidden` 属性，跳过隐藏行
- 如果用户选择导入隐藏行，则读取所有行（包括隐藏行）

```python
from openpyxl import load_workbook

wb = load_workbook(file_path)
ws = wb.active

# 获取非隐藏行（默认行为）
visible_rows = []
for row in ws.iter_rows(min_row=2):  # 跳过表头
    row_idx = row[0].row
    if not ws.row_dimensions[row_idx].hidden:  # 跳过隐藏行
        visible_rows.append([cell.value for cell in row])

# 如果用户选择导入隐藏行，则不做过滤
```

**列名识别规则：**

| 字段 | 关键词匹配 | 必需 |
|------|-----------|------|
| module（模块） | 测试项目 / 模块 / 功能 / 分类 | 是 |
| title（标题） | 用例标题 / 标题 / 用例 | 是 |
| command（指令码） | 指令 / 命令 / command | 否 |
| description（描述） | 描述 / 说明 / 详细 | 否 |
| expected（期望结果） | 期望 / 预期 | 是 |
| actual（实际现象） | 实际 / 现象 / 测试现象 | 否 |
| precondition（预置条件） | 预置 / 条件 | 否 |
| status（状态） | 结果 / 状态 / 测试结果 | 是 |
| remark（备注） | 备注 / 注 | 否 |

**识别代码模板：**

```python
import pandas as pd

COLUMN_MAPPING_RULES = {
    'module':       ['测试项目', '模块', '功能', '分类'],
    'title':        ['用例标题', '标题', '用例', '测试用例'],
    'command':      ['指令', '命令', 'command'],
    'description':  ['描述', '说明', '详细'],
    'expected':     ['期望', '预期', '期望结果'],
    'actual':       ['实际', '现象', '实际现象', '测试现象'],
    'precondition': ['预置', '条件', '预置条件'],
    'status':       ['结果', '状态', '测试结果'],
    'remark':       ['备注', '注'],
}

def identify_columns(headers):
    mapping = {}
    for col_idx, header in enumerate(headers):
        header_str = str(header).strip().lower()
        for field, keywords in COLUMN_MAPPING_RULES.items():
            if field not in mapping:
                for kw in keywords:
                    if kw.lower() in header_str:
                        mapping[field] = col_idx
                        break
    return mapping
```

**识别后展示给用户确认：**

```
自动识别列映射：
- 模块(module): A列 "测试项目"
- 标题(title): B列 "用例标题"
- 指令码(command): C列 "指令"
- 描述(description): D列 "描述"
- 预置条件(precondition): E列 "预置条件"
- 期望结果(expected): F列 "期望结果"
- 状态(status): H列 "测试结果"
- 实际现象(actual): I列 "实际测试现象"
- 备注(remark): G列 "备注"

请确认映射是否正确？如需修改请告知。
```

如果识别有误，让用户手动指定列名或列号。

### Step 3: 筛选 NG 问题、处理合并单元格、预览

**3.1 筛选 NG 问题：**
```python
df = df.fillna(method='ffill')  # 处理合并单元格（前向填充）
ng_items = df[df[status_col] == 'NG']  # 筛选状态列值为用户指定的筛选值的行
```

**3.2 合并相同指令的问题（可选）：**
- 同一条指令的不同预置条件/场景，可合并为 1 个 Issue
- 在 Description 中列出所有场景

**3.3 生成预览列表（必须用户确认后才能创建）：**

展示完整的 Issue 创建计划：

```
## 预览：将创建 X 个 Jira Issue

| # | Summary | 模块 | 指令 | NG数 |
|---|---------|------|------|------|
| 1 | [AI][Platform-A][Customer-X] 功能A指令异常 (CMD-01) | 模块A | CMD-01 | 8 |
| 2 | [AI][Platform-A][Customer-X] 功能B未实现 (CMD-02) | 模块B | CMD-02 | 7 |
| ... |

项目: PROJ | 经办人: user@example.com | 优先级: 高 | 严重程度: B
标签: 自动化测试问题

确认后开始创建。是否继续？
```

**关键规则：必须等用户明确确认后才能调用 mcp__atlassian__jira_create_issue。**

### Step 4: 获取 Jira 必填字段

在创建前自动获取：

1. 查找自定义必填字段（如 "严重程度"）：
   - 调用 `mcp__atlassian__jira_search_fields` 关键词搜索
   - 获取 field_id（如 customfield_XXXXX）
   - 调用 `mcp__atlassian__jira_get_field_options` 获取可选值

2. 如果遇到新的必填字段错误：
   - 识别缺少的字段
   - 询问用户值
   - 重试创建

### Step 5: 批量创建 Issue

用户确认后，串行创建 Issue：

```
创建中... [1/27] PROJ-101 ✅
创建中... [2/27] PROJ-102 ✅
创建中... [3/27] ❌ 失败: xxx
...
```

**Issue 创建参数：**

```
mcp__atlassian__jira_create_issue(
  project_key: "{项目key}",
  summary: "[AI][{平台}][{客户}] {问题描述} ({指令码})",
  issue_type: "{问题类型}",
  assignee: "{经办人邮箱}",
  description: "<Description内容>",
  additional_fields: {
    "priority": {"name": "{优先级}"},
    "labels": ["{标签}"],
    "{严重程度字段ID}": {"value": "{严重程度值}"}
  }
)
```

**Summary 格式：**
```
[AI][{平台}][{客户}]{模块} {问题描述} ({指令码})
```

示例：`[AI][Platform-A][Customer-X] 功能A连接异常 (CMD-01 02)`

如果模块名称缺失，用测试用例标题作为描述。

**Description 格式（必须包含 AI 标识）：**

> **注意：** Jira Server 数据库不支持 4 字节 UTF-8 字符（如 emoji），使用 emoji 会导致 SQL 写入失败。
> AI 标识必须使用纯文本 + Jira wiki `{quote}` 格式。

```markdown
{quote}[AI] 此 Issue 由 AI (Claude Code) 自动创建于 {创建日期时间}{quote}

### 问题描述
{问题描述或标题}

### 测试环境
- 平台: {平台}
- 客户: {客户}
- 设备: {平台}-{客户}
- 测试时间: {测试日期}

### 预置条件
{预置条件}

### 期望结果
{期望结果}

### 实际现象
{实际现象}

### 备注
{备注}
```

### Step 6: 输出汇总报告

```
## Jira Issue 批量创建完成

### 成功：N 个
| # | Jira Key | Summary |
|---|----------|---------|
| 1 | PROJ-101 | [AI][Platform-A][Customer-X] 功能A连接异常 |
| ... |

### 失败：M 个
| # | 问题 | 错误原因 |
|---|------|----------|
| 1 | 功能B异常 | 必填字段缺失 |
| ... |

### Jira 链接
- 项目: https://{jira-server}/projects/{项目key}
- 查询: https://{jira-server}/issues/?jql=project={项目key} AND labels="{标签}" AND created >= -1d
```

## 常见问题与错误处理

### Q: mcp-atlassian 工具列表为空
A: 确保 `.mcp.json` 中设置了 `"TOOLSETS": "all"`，并且 `JIRA_PERSONAL_TOKEN` 正确（不是 `JIRA_TOKEN`）。

### Q: 创建失败 "xxx 是必填项"
A: Jira 项目可能有自定义必填字段。使用 `mcp__atlassian__jira_search_fields` 查找字段，`mcp__atlassian__jira_get_field_options` 获取可选值，添加到 `additional_fields` 中重试。

### Q: Excel 列名不标准
A: 识别完成后用户可手动修正映射，指定正确的列名或列号（如 "A列"、"第3列"）。

### Q: 合并单元格导致数据缺失
A: 使用 `df.fillna(method='ffill')` 前向填充处理。识别后提示用户确认数据是否完整。

### Q: Description 写入失败 "Incorrect string value"
A: Jira Server 数据库（MySQL latin1/utf8mb3）不支持 4 字节 UTF-8 字符（如 emoji）。Description 和 Summary 中禁止使用 emoji，AI 标识使用纯文本 `{quote}[AI] 此 Issue 由 AI (Claude Code) 自动创建于 {日期}{quote}` 格式。

## 反模式（禁止）

- 未经用户确认就创建/修改 Issue（必须先预览再确认）
- 遇到创建/修改失败就停止整个流程（应记录失败继续处理）
- 在 Summary 或 Description 中包含原始 Excel 行号等调试信息
- 并行创建/修改 Issue（应串行处理避免 API 限流）
- 重复创建已存在的 Issue（创建前检查是否有相同 Summary）
- 在 Summary 或 Description 中使用 emoji 等 4 字节 UTF-8 字符（Jira Server 数据库不支持）
- 硬编码自定义字段 ID（应通过 search_fields 动态查找）

---

# 批量修改功能

对已创建的 Jira Issue 批量修改字段。

## 支持修改的字段

| 字段 | MCP 参数 | 示例 |
|------|---------|------|
| 标题(summary) | `fields.summary` | 修改标题格式 |
| 描述(description) | `fields.description` | 补充 AI 标识 |
| 经办人(assignee) | `fields.assignee` | 批量转交 |
| 标签(labels) | `fields.labels` | 添加/修改标签 |
| 优先级(priority) | `fields.priority` | 批量调整优先级 |
| 备注(comment) | `mcp__atlassian__jira_add_comment` | 批量添加备注 |
| 自定义字段 | `additional_fields` | 批量调整（通过 search_fields 查找字段 ID） |

## 批量修改工作流程

### Step M1: 确定修改范围

用户提供修改范围，支持三种方式：

**方式 A：JQL 查询**
用户提供 JQL 条件，如：
```
project = PROJ AND labels = "自动化测试问题" AND summary ~ "[AI]"
```

**方式 B：Issue Key 列表**
用户直接提供：
```
PROJ-101, PROJ-102, PROJ-103, ...
```

**方式 C：标签筛选**
用户指定标签，如：`自动化测试问题`

根据用户选择调用对应的查询工具：

```
# 方式 A/C: JQL 查询
mcp__atlassian__jira_search(
  jql: "project = PROJ AND labels = '自动化测试问题'",
  limit: 50
)

# 方式 B: 逐个获取
mcp__atlassian__jira_get_issue(issue_key: "PROJ-101")
```

### Step M2: 收集修改内容

使用 AskUserQuestion 询问要修改哪些字段，以及修改规则。

**常见修改场景：**

**场景 1：修改标题格式**
```
修改规则：
- 旧格式：[AI][旧前缀] 功能描述 (CMD-01)
- 新格式：[AI][Platform-A][Customer-X] 功能描述 (CMD-01)

实现：字符串替换 "[AI][旧前缀]" -> "[AI][Platform-A][Customer-X]"
```

**场景 2：修改经办人**
```
将所有 Issue 的经办人从 A 改为 B
- 新经办人：another-user@example.com
```

**场景 3：补充 Description 中的 AI 标识**
```
在 Description 开头插入：
{quote}[AI] 此 Issue 由 AI (Claude Code) 自动创建于 {日期}{quote}
```

**场景 4：添加/修改标签**
```
- 添加标签：新标签名
- 或替换标签：旧标签 -> 新标签
```

**场景 5：批量添加备注**
```
为所有 Issue 添加备注：
"问题已确认，待排期修复。"
```

**场景 6：自定义字段修改**
```
修改严重程度：B -> A（字段 ID 通过 search_fields 动态查找）
```

### Step M3: 预览修改内容（必须用户确认）

展示完整的修改计划，**必须等用户确认后才执行**：

```
## 预览：将修改 N 个 Jira Issue

### 修改内容：Summary 标题格式修改
替换规则："[AI][旧前缀]" -> "[AI][Platform-A][Customer-X]"

| # | Issue Key | 当前 Summary | 修改后 Summary |
|---|-----------|-------------|--------------|
| 1 | PROJ-101 | [AI][旧前缀] 功能A连接异常... | [AI][Platform-A][Customer-X] 功能A连接异常... |
| 2 | PROJ-102 | [AI][旧前缀] 获取状态错误... | [AI][Platform-A][Customer-X] 获取状态错误... |
| ... |

确认后开始修改。是否继续？
```

**关键规则：必须等用户明确确认后才能调用 mcp__atlassian__jira_update_issue。**

### Step M4: 串行批量修改

用户确认后，逐个修改 Issue：

```
修改中... [1/N] PROJ-101 ✅
修改中... [2/N] PROJ-102 ✅
修改中... [3/N] PROJ-103 ❌ 失败: 权限不足
...
```

**修改调用示例：**

```
# 修改标题/经办人/标签/优先级等字段
mcp__atlassian__jira_update_issue(
  issue_key: "PROJ-101",
  fields: '{"summary": "[AI][Platform-A][Customer-X] 功能A连接异常"}'
)

# 修改多个字段
mcp__atlassian__jira_update_issue(
  issue_key: "PROJ-101",
  fields: '{"summary": "新标题", "assignee": "user@example.com", "labels": ["新标签"]}'
)

# 修改描述
mcp__atlassian__jira_update_issue(
  issue_key: "PROJ-101",
  fields: '{"description": "新的描述内容"}'
)

# 修改自定义字段（字段 ID 通过 search_fields 动态查找）
mcp__atlassian__jira_update_issue(
  issue_key: "PROJ-101",
  additional_fields: '{"customfield_XXXXX": {"value": "A"}}'
)

# 添加备注（不是修改字段，用专门的工具）
mcp__atlassian__jira_add_comment(
  issue_key: "PROJ-101",
  body: "问题已确认，待排期修复。"
)
```

**修改描述时保留原有内容的策略：**
1. 先用 `mcp__atlassian__jira_get_issue` 获取当前 description
2. 在原有内容前/后插入新内容
3. 用 `mcp__atlassian__jira_update_issue` 更新

### Step M5: 输出修改报告

```
## Jira Issue 批量修改完成

### 修改类型：Summary 标题格式
### 成功：N 个
| # | Issue Key | 修改后 Summary |
|---|-----------|--------------|
| 1 | PROJ-101 | [AI][Platform-A][Customer-X] 功能A连接异常 |
| ... |

### 失败：M 个
| # | Issue Key | 错误原因 |
|---|-----------|----------|
| 1 | PROJ-103 | 权限不足 |
| ... |
```

## 批量修改常见操作速查

### 标题批量替换

```
输入：
  - 目标 Issue：project = PROJ AND labels = "自动化测试问题"
  - 替换规则：将 "[AI][旧前缀]" 替换为 "[AI][Platform-A][Customer-X]"

流程：查询 -> 预览新旧对比 -> 确认 -> 逐个 update_issue
```

### 经办人批量转交

```
输入：
  - 目标 Issue：project = PROJ AND assignee = "old-user"
  - 新经办人：new-user@example.com

流程：查询 -> 预览列表 -> 确认 -> 逐个 update_issue(fields: {"assignee": "new-user@example.com"})
```

### Description 批量补充 AI 标识

```
输入：
  - 目标 Issue：project = PROJ AND labels = "自动化测试问题"
  - 在 Description 开头插入 AI 标识

流程：
  1. 查询所有目标 Issue
  2. 逐个 get_issue 获取当前 description
  3. 在开头插入 "{quote}[AI] 此 Issue 由 AI (Claude Code) 自动创建于 {日期}{quote}"
  4. 预览修改 -> 确认 -> 逐个 update_issue
```

### 标签批量操作

```
# 添加标签（保留原有标签）
获取当前 labels -> 追加新标签 -> update_issue

# 替换标签
直接 update_issue(fields: {"labels": ["新标签1", "新标签2"]})

# 删除特定标签
获取当前 labels -> 移除目标标签 -> update_issue
```

### 批量添加备注

```
输入：
  - 目标 Issue：project = PROJ AND labels = "自动化测试问题"
  - 备注内容："问题已确认，待排期修复。"

流程：查询 -> 预览 -> 确认 -> 逐个 add_comment
```
