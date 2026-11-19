---
name: mr-suggestion
description: Fetch and apply GitLab MR code review suggestions. Use when the user mentions MR review suggestions, code review suggestions, MR建议, 代码审核, or wants to fix code based on review feedback.
version: 1.0.0
author: zhaobo
---

# MR Code Review Suggestions

获取 MR（Merge Request）的 AI 代码审核建议（gitlab-aicr），分析并直接在代码库中应用修复。

## 前置条件

- Python 3 已安装（macOS 自带，Windows 需确认 `python` 或 `python3` 可用）
- 项目根目录存在 `.mr-suggestion.json` 配置文件

## 配置

在项目根目录创建 `.mr-suggestion.json`：

```json
{
  "api_base_url": "https://aicr.gz.cvte.cn/core/suggestions",
  "auth_token": "your-auth-token",
  "project_id": "12345",
  "page_size": 100,
  "status": "open"
}
```

| 字段 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `api_base_url` | 是 | API 地址 | - |
| `auth_token` | 是 | 授权令牌 | - |
| `project_id` | 是 | GitLab 项目 ID | - |
| `page_size` | 否 | 每页返回数量 | 10 |
| `status` | 否 | 建议状态过滤 | `open` |

配置文件含敏感信息，建议添加到 `.gitignore`。示例配置见 [config.example.json](config.example.json)。

如果配置文件不存在，提示用户创建，并参考示例。

## 工作流

### 第一步：获取建议列表

执行 Python 脚本获取指定 MR 的建议。

#### 脚本定位

脚本文件名为 `fetch_suggestions.py`，位于本 Skill 目录下的 `scripts/` 子目录中。
Agent 需按以下优先级查找脚本路径：

1. **相对于本文件定位**（推荐）：本 SKILL.md 同级的 `scripts/fetch_suggestions.py`
2. **按已知路径查找**：在项目根目录下搜索以下常见位置：
   - `.cursor/skills/mr-suggestion/scripts/fetch_suggestions.py`（Cursor）
   - `.claude/skills/mr-suggestion/scripts/fetch_suggestions.py`（Claude）
   - `.agents/skills/mr-suggestion/scripts/fetch_suggestions.py`（通用）
3. **全局搜索**：在项目中搜索文件名 `fetch_suggestions.py`

找到脚本后，将其完整路径记为 `<SCRIPT_PATH>`。

#### 执行命令

根据操作系统选择执行方式：

- macOS / Linux：使用 bash，Python 命令为 `python3`
- Windows：优先使用 PowerShell，Python 命令为 `python`

```bash
# macOS / Linux
python3 <SCRIPT_PATH> <mr_iid> [page_size] [status]
```

```powershell
# Windows (PowerShell)
python <SCRIPT_PATH> <mr_iid> [page_size] [status]
```

#### 参数说明

- `mr_iid`（必填）：MR 的 IID 编号
- `page_size`（可选）：覆盖配置中的分页大小
- `status`（可选）：覆盖配置中的状态过滤

脚本输出 JSON，结构如下：

```json
{
  "project_id": "string",
  "page": 1,
  "page_size": 10,
  "total": 5,
  "data": [
    {
      "id": 123,
      "score": 8,
      "label": "bug",
      "file_path": "src/utils.ts",
      "description": "问题描述",
      "suggestion_content": "建议内容",
      "existing_code": "原始代码",
      "improved_code": "改进后代码",
      "language": "typescript",
      "mr_url": "https://...",
      "source_branch": "feature/xxx",
      "target_branch": "main"
    }
  ]
}
```

### 无建议处理

如果返回的 `data` 为空数组（`total` 为 0），说明该 MR 没有审核问题，直接告知用户：

> MR {mr_iid} 没有待处理的审核建议，代码审核已通过，无需修改。

此时跳过后续所有步骤，不再展示表格或分析优先级。

### 第二步：展示建议摘要

解析 JSON 后，先展示汇总表格：

```
| ID | 评分 | 标签 | 文件 | 描述 |
|----|------|------|------|------|
```

然后逐条展示详细信息，包含：问题描述、建议内容、现有代码、改进代码。

### 第三步：分析优先级

根据评分判断修复优先级：

- **score >= 7**：高优先级，建议立即修复
- **score >= 5**：中等优先级，建议评估
- **score < 5**：低优先级，可选修复

### 第四步：应用修复

当用户要求应用某条建议的修复时：

1. 根据建议的 `file_path` 定位项目中的文件
2. 读取文件内容，找到 `existing_code` 对应的代码段
3. 用 `improved_code` 替换 `existing_code`
4. 报告修改内容和位置

如果 `file_path` 为空，提示用户手动指定文件。

如果文件中找不到 `existing_code` 的精确匹配，尝试模糊匹配（忽略空白差异），或提示用户确认位置。

## 批量操作

当用户要求修复所有高优先级建议时：

1. 筛选 score >= 7 的建议
2. 按文件分组
3. 逐个应用修复（同一文件的修复按行号从后往前应用，避免行号偏移）
4. 汇总报告所有修改
