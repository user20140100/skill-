---
name: gitlab-api
description: >-
  GitLab API 基础 skill：通过 curl 直接调用 GitLab REST API。 支持获取 commit/MR diff、评论 MR、合并
  MR、指派 MR、查用户 ID。
trigger_keywords:
  - gitlab
  - merge request
  - MR
  - 评论MR
  - 合并MR
  - commit
  - diff
version: '1'
author: yexiaojie
---

# GitLab API Skill

通过 curl 直接调用 GitLab REST API v4，无需 MCP Server。

## Setup

执行任何 API 调用前，先读取凭据：

```bash
cat ~/.claude/skills/gitlab-api/credentials.json
```

从 JSON 中提取 `GITLAB_BASE_URL` 和 `GITLAB_PAT`，后续所有 curl 请求使用：

```bash
curl -s --header "PRIVATE-TOKEN: $GITLAB_PAT" "$GITLAB_BASE_URL/api/v4/..."
```

## URL 解析规则

从用户提供的 GitLab URL 中提取 project path 和 iid/sha：

- **MR URL**: `https://gitlab.gz.cvte.cn/group/project/-/merge_requests/123` → project=`group/project`, iid=`123`
- **Commit URL**: `https://gitlab.gz.cvte.cn/group/project/-/commit/abc123` → project=`group/project`, sha=`abc123`
- **嵌套 group**: `https://gitlab.gz.cvte.cn/a/b/c/-/merge_requests/1` → project=`a/b/c`

project path 需要 URL 编码（`/` → `%2F`）用于 API 调用。

## 操作列表

### 1. 获取 MR 信息及所有 commit 的 diff

```bash
# 获取 MR 基本信息
curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/projects/$PROJECT/merge_requests/$IID"

# 获取 MR 的所有 changes (diff)
curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/projects/$PROJECT/merge_requests/$IID/changes"

# 获取 MR 的 commits 列表
curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/projects/$PROJECT/merge_requests/$IID/commits"
```

### 2. 获取单个 Commit 信息及 diff

```bash
# commit 详情
curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/projects/$PROJECT/repository/commits/$SHA"

# commit diff
curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/projects/$PROJECT/repository/commits/$SHA/diff"
```

### 3. 评论 MR (Add Note)

```bash
curl -s --header "PRIVATE-TOKEN: $PAT" \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"body": "评论内容（支持 Markdown）"}' \
  "$BASE/api/v4/projects/$PROJECT/merge_requests/$IID/notes"
```

### 4. 合并 MR

```bash
curl -s --header "PRIVATE-TOKEN: $PAT" \
  --request PUT \
  --data-urlencode "merge_commit_message=自定义 merge commit message" \
  --data-urlencode "should_remove_source_branch=false" \
  --data-urlencode "squash=false" \
  "$BASE/api/v4/projects/$PROJECT/merge_requests/$IID/merge"
```

参数均可选，留空则用 GitLab 默认值。

### 5. 指派 MR (Assign)

```bash
# 先查用户 ID
USER_ID=$(curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/users?username=USERNAME" | jq '.[0].id')

# 指派
curl -s --header "PRIVATE-TOKEN: $PAT" \
  --request PUT \
  --header "Content-Type: application/json" \
  --data "{\"assignee_id\": $USER_ID}" \
  "$BASE/api/v4/projects/$PROJECT/merge_requests/$IID"
```

### 6. 查用户 ID

```bash
curl -s --header "PRIVATE-TOKEN: $PAT" "$BASE/api/v4/users?username=USERNAME" | jq '.[0] | {id, name, username}'
```

## 通用规则

- 所有响应用 `jq` 格式化输出，只提取关键字段展示给用户
- diff 内容可能很长，展示时做适当截断或折叠
- 出错时展示 HTTP status 和 error message
- project path 中的 `/` 必须 URL 编码为 `%2F`
- 分页：默认 per_page=20，需要更多结果时加 `?per_page=100&page=N`
