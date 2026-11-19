# GitLab API 远程搜索参考

当本地 git 搜索无结果，或问题可能涉及未 clone 的仓库时使用的远程搜索方法。

## Token 配置与检测

内部 GitLab 实例：`https://gitlab.gz.cvte.cn`，API 地址：`https://gitlab.gz.cvte.cn/api/v4`

创建 PAT：访问 https://gitlab.gz.cvte.cn/-/user_settings/personal_access_tokens
- Token name: `work-agent-readonly`
- Scopes: `read_api` + `read_repository`

写入 `~/.bashrc`：
```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
```

### Token 自动检测脚本

发起 API 调用前执行：

```bash
# 1. 检查环境变量
if [ -n "$GITLAB_TOKEN" ]; then
  # 2. 验证 token 有效性
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "https://gitlab.gz.cvte.cn/api/v4/user")
  if [ "$STATUS" = "200" ]; then
    echo "GITLAB_TOKEN 有效"
  else
    echo "GITLAB_TOKEN 已失效（HTTP $STATUS），需要重新创建"
    # 触发提示
  fi
else
  # 3. 搜索 shell 配置文件中是否有 glpat- 开头的 token
  FOUND=$(grep -rh 'glpat-' ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null | head -1)
  if [ -n "$FOUND" ]; then
    echo "在配置文件中发现 token 但未加载，请执行: source ~/.bashrc"
  else
    echo "未找到 GITLAB_TOKEN，需要创建"
    # 触发提示
  fi
fi
```

### Token 缺失/失效时的提示文案

如检测到 token 缺失或失效，输出以下提示后**暂停等待**：

> 未检测到有效的 GitLab 访问令牌。请按以下步骤创建：
> 1. 访问 https://gitlab.gz.cvte.cn/-/user_settings/personal_access_tokens
> 2. 填写 Token name: `work-agent-readonly`
> 3. 勾选 scopes: `read_api` + `read_repository`
> 4. 点击 Create 后复制生成的 token（格式为 `glpat-...`）
> 5. 执行 `export GITLAB_TOKEN="<你的token>"` 并追加到 `~/.bashrc`
>    或直接告诉我 token，我会帮你配置

## API 搜索步骤

> 对一个项目是顺序依赖的（查 group → 列项目 → 查分支 → 读文件），但涉及**多个项目时应对各项目并行操作**。
> 所有请求带 `-H "PRIVATE-TOKEN: $GITLAB_TOKEN"`。

### 步骤 9：确定 group 信息

从当前 git remote URL 自动提取 group 路径，查出 group ID：

```bash
# 从 remote URL 提取 group 路径
# 如 git@gitlab.gz.cvte.cn:my-group/my-project.git → my-group
GROUP=$(git remote get-url origin | sed 's|.*[:/]||; s|/.*||')
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/groups?search=$GROUP" | python3 -c \
  "import sys,json; g=json.load(sys.stdin); print(g[0]['id'] if g else 'NOT_FOUND')"
```

### 步骤 10：列出 group 下项目并匹配

搜出所有项目，根据模块名/文件名筛选相关项目：

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/groups/<group_id>/projects?include_subgroups=true&per_page=100" | \
  python3 -c "import sys,json; [print(p['id'], p['path_with_namespace']) for p in json.load(sys.stdin)]"
```

筛选出相关项目后，按优先级获取分支（利用 API 的 `search` 参数直接过滤）：

```bash
# 优先级1：直接搜索客户/机型名
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/branches?search=<customer_name>&per_page=50"

# 优先级2：搜索模块/功能名
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/branches?search=<module_name>&per_page=50"

# 优先级3：未找到时，拉取全部分支再按"最近活跃"筛选
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/branches?per_page=100"
```

涉及多个项目时，各项目并行查询。

### 步骤 11：搜索提交历史

对匹配的分支，**并行**拉取各分支 commit 列表并筛选关键词：

```bash
# 获取分支最近提交（可用 &since=YYYY-MM-DD 缩小范围）
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/commits?ref_name=<branch>&per_page=50"
```

### 步骤 12：获取提交 diff

锁定可疑提交后，获取完整变更内容：

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/commits/<sha>/diff" | \
  python3 -m json.tool
```

### 步骤 13：读取文件内容

读取特定分支上某个文件的原始内容：

```bash
# 文件路径需 URL 编码，路径中的 / 替换为 %2F
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/files/<path_encoded>/raw?ref=<branch>"
```

### 步骤 14：分支对比

对比有修复的分支与问题分支的差异：

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/projects/<project_id>/repository/compare?from=<base>&to=<target>" | \
  python3 -c "import sys,json; [print(d['new_path'],d['diff'][:300]) for d in json.load(sys.stdin).get('diffs',[])]"
```

### 步骤 15：跨客户分支对比

找到同类问题已修复的客户分支后：
- 读取目标分支对应文件，与当前分支对比，提取修复模式
- 关注配置宏值的差异、新增/删除的逻辑分支、边界处理

## 注意事项

- **项目 ID 支持路径编码**：`projects/:id` 中的 `:id` 可以是数字 ID 或 URL 编码的项目路径，如 `my-group%2Fmy-project`
- **高级搜索依赖**：`groups/:id/search?scope=blobs/commits` 和 `projects/:id/search?scope=blobs` 依赖 Elasticsearch/Zoekt 后端索引。如实例未启用高级搜索，这些端点可能返回 400 或空结果，此时需要通过"列项目→列分支→查提交→读文件"的路径进行搜索
- **API 限流**：批量并行查询时控制在 ~10 并发以内
- **远程结果需二次确认**：GitLab API 返回的 commit 仅是线索，关键 commit 应再调 `commits/:sha/diff` 看完整 diff