---
name: git-commit-msg
version: 1.2.0
author: baotian
description: |
  智能生成 Git Commit Message 并提交代码。

  触发场景：当用户提到"提交代码"、"commit"、"帮我提交"、"生成commit message"、"写个提交信息"、"暂存并提交"、"保存更改到git"等与代码提交相关的请求时使用此技能。

  功能：自动分析代码变更、学习项目提交风格、生成规范的 commit message。每次提交前必须询问是否有关联的 Jira 链接，如有则自动添加评论到 Jira 并将 Jira 状态流转为"自测中"。不会自动推送（需用户手动推送）。
---

# Git Commit 技能

帮助用户生成符合项目风格的 commit message 并完成代码提交，支持 Jira 关联。

## 核心原则

- **不自动推送**：只执行 `git commit`，推送必须由用户手动完成
- **学习项目风格**：从 git log 中学习项目的 commit message 风格
- **用户确认**：生成 message 后必须让用户确认或修改
- **敏感文件提醒**：发现可能的敏感文件时提醒用户
- **必须询问 Jira**：每次提交前**必须**询问用户是否有关联的 Jira 链接，这是必要步骤
- **Jira 集成**：如果有 Jira，根据代码改动自动添加评论到 Jira，**并将 Jira 状态流转为"自测中"**

---

## 执行流程

### 1. 检查 Remote 仓库

```bash
git remote -v
```

- 如果有多个 remote，使用 AskUserQuestion 询问用户要提交到哪个源
- 如果只有一个 remote，直接使用，跳过询问

---

### 2. 收集项目信息

并行执行以下命令获取完整上下文：

```bash
git status                    # 查看变更文件
git diff --stat               # 变更统计
git diff --staged             # 已暂存的差异
git diff                      # 未暂存的差异
git log --oneline -20         # 最近20条提交（学习项目风格）
git branch -vv                # 查看分支追踪关系
```

---

### 3. 检查敏感文件

扫描变更文件列表，如果发现以下类型的文件，提醒用户确认：

- `.env`、`.env.local`、`.env.*`
- `credentials`、`secrets`、`keys`
- `*.pem`、`*.key`、`*.p12`
- 包含 `password`、`token`、`api_key` 的文件
- `config/local.*`、`config/production.*`

**提醒方式**：使用 AskUserQuestion 让用户选择：
- 继续提交（已确认无敏感信息）
- 取消，先检查这些文件

---

### 4. 分析改动内容并整理上下文

根据 git diff 分析变更，**生成改动总结**：

#### 改动类型判断

| 改动特征 | Type |
|----------|------|
| 新增功能、新增 API、新文件 | feat |
| 修复 Bug、错误处理、异常修复 | fix |
| 重命名、移动、删除、提取代码 | refactor |
| 格式化、空白、注释、缩进 | style |
| 文档更新、README、注释文档 | docs |
| 性能优化、缓存、算法改进 | perf |
| 测试用例、测试配置 | test |
| 构建脚本、依赖管理、项目配置 | build |
| CI/CD 配置、自动化流程 | ci |
| .gitignore、.editorconfig 等杂项 | chore |
| 回滚之前的提交 | revert |

#### 生成改动总结

整理以下信息，用于后续 Jira 评论和 commit message：

```markdown
## 改动总结

### 改动原因
[为什么需要这次改动？解决了什么问题？]

### 解决方案
[采用了什么方案？核心改动点是什么？]

### 主要改动
- 文件1: [改动说明]
- 文件2: [改动说明]
- ...

### 影响范围
[哪些模块/功能会受到影响]
```

**分析维度**：
- 改动类型（type）
- 影响范围：哪些模块/文件
- 改动规模：小（<50行）/ 中（50-200行）/ 大（>200行）
- 是否破坏性：是否影响 API/接口兼容性

---

### 5. 学习项目 Commit 风格

分析 git log 中的历史提交，识别：

**格式类型**：
- Conventional Commits：`feat: xxx` 或 `feat(scope): xxx`
- 自定义格式：如 `[模块] 描述`、`模块: 描述`
- 简单描述：纯文本描述

**语言偏好**：
- 中文为主 → 生成中文 message
- 英文为主 → 生成英文 message
- 混合 → 优先使用中文

**格式细节**：
- 是否使用 scope（模块前缀）
- 是否有 body（详细说明）
- 常用的 type 前缀

---

### 6. 询问 Jira 关联（必要步骤）

**⚠️ 这是必要步骤，每次提交前必须询问！**

使用 AskUserQuestion 询问用户：

> **是否有需要关联的 Jira 链接？**
>
> 如果有，提交后会自动在 Jira 添加评论（包含改动原因、解决方案、主要改动），**并将 Jira 状态流转为"自测中"**，同时在 commit message 中备注 Jira 链接。

选项：
1. **有 Jira 链接** → 用户提供链接，继续流程
2. **没有 Jira** → 跳过 Jira 相关步骤
3. **取消** → 不提交

**如果用户提供了 Jira 链接**：
1. 从链接中提取 Jira ID（正则：`/browse/([A-Z]+-\d+)`）
2. 验证链接格式是否正确
3. 保存 Jira ID 和 URL，用于后续步骤

---

### 7. 生成 Commit Message

#### Conventional Commits 格式（推荐）

```
<type>: <subject>

[可选 body]

[可选 footer]
```

**重要规则**：
- **不使用 scope**：`feat: xxx` 而非 `feat(module): xxx`
- **subject 规则**：
  - 英文：原形动词开头，首字母小写，结尾无句号
  - 中文：动词开头，简洁明了
- **body 规则**（可选）：说明为什么改，列出主要改动点
- **footer 规则**：
  - 破坏性变更用 `BREAKING CHANGE:`
  - **Jira 链接**：如果有 Jira，添加 `Jira: https://jira.cvte.com/browse/XXX-123`

#### 带 Jira 的 Commit Message 示例

```
fix: 修复空指针异常导致崩溃

- 添加空值检查，防止 NullPointerException
- 优化异常处理逻辑，提高代码健壮性

Jira: https://jira.cvte.com/browse/SEEWOOS-12345
```

#### 简单描述格式

如果项目不使用 Conventional Commits，使用项目原有格式：

```
<简短描述>

<详细说明（可选）>

Jira: <URL>
```

---

### 8. 用户确认 Commit Message

使用 AskUserQuestion 展示生成的 commit message，让用户选择：

1. **使用此 message 提交** → 继续流程
2. **修改 message** → 用户提供新内容，重新确认
3. **重新生成** → 选择不同的 type 或调整描述
4. **取消** → 不提交

---

### 9. 写入 Jira 评论并流转状态（如有 Jira）

如果用户提供了 Jira 链接，在提交前必须完成以下**两个操作**：

#### 9.1 写入 Jira 评论

使用 `jira_add_comment` 写入评论：

```
jira_add_comment(issue_key="{JIRA-ID}", body=评论内容)
```

#### MCP 工具不可用时的 curl fallback

如果 `jira_add_comment` 工具未加载到当前会话（MCP 服务器已配置但工具不可用），使用 Jira REST API 作为 fallback：

**从 settings.json 中读取配置**（读取用户目录下 `settings.json` 中 `mcpServers.mcp-atlassian` 的 `env` 字段），提取：
- `JIRA_URL`：Jira 服务地址
- `JIRA_PERSONAL_TOKEN`：认证 token

**调用方式**（从 Jira URL 中提取 issueId，用于 DELETE 操作）：

```bash
# 1. 获取 issueId（删除评论时需要）
curl -s -H "Authorization: Bearer {TOKEN}" "{JIRA_URL}/rest/api/2/issue/{JIRA-ID}" | python -c "import sys,json; print(json.load(sys.stdin)['id'])"

# 2. 添加评论
# 3. 删除评论（如需要）
curl -s -o /dev/null -w "%{http_code}" -X DELETE "{JIRA_URL}/rest/api/2/issue/{JIRA-ID}/comment/{COMMENT_ID}" -H "Authorization: Bearer {TOKEN}"
```

**⚠️ Windows 中文编码注意事项**：

在 Windows bash 环境下，**禁止**直接在 curl `-d` 参数中内联中文或其他非 ASCII 字符，bash shell 编码会导致乱码（中文变成 `??????`）。

**正确做法**：先用 `Write` 工具将 JSON 写入临时文件，再用 `curl --data-binary @file` 发送：

```
# 步骤 1：用 Write 工具写入临时文件
Write(file_path="{项目目录}/jira_comment.json", content=JSON字符串)

# 步骤 2：用 curl 发送文件内容
curl -s -w "\n%{http_code}" -X POST "{JIRA_URL}/rest/api/2/issue/{JIRA-ID}/comment" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer {TOKEN}" \
  --data-binary @"{项目目录}/jira_comment.json"

# 步骤 3：发送成功后删除临时文件
rm "{项目目录}/jira_comment.json"
```

如果发送后发现乱码，立即用 DELETE API 删除乱码评论，然后用文件方式重新发送。

#### Jira 评论模板

```markdown
**代码提交说明**

### 改动原因
{改动原因}

### 解决方案
{解决方案}

### 主要改动
- {文件1}: {改动说明}
- {文件2}: {改动说明}

### 备注
{其他需要说明的内容}

---
Commit: {commit_hash}
Branch: {branch_name}
```

#### 9.2 流转 Jira 状态为"自测中"（必要步骤）

**⚠️ 这是必要步骤，有 Jira 链接时必须执行！**

Jira 的工作流通常是链式的，可能需要**多步流转**才能到达目标状态。例如常见的流转链：

```
新建 → 开发中 → 自测中
```

从"新建"状态无法直接跳到"自测中"，必须先经过"开发中"。因此需要**循环查询并逐步流转**。

##### 流转算法

```
1. 调用 jira_get_transitions 获取当前可用的 transitions
2. 检查 transitions 中是否有"自测"相关的目标：
   - 有 → 直接执行 jira_transition_issue 流转到"自测中"，结束
   - 没有 → 进入步骤 3
3. 选择中间过渡状态，优先级：
   - 包含"开发"的 transition（如"开发"、"开始开发"）
   - 包含"In Progress"的 transition
   - 其他合理的正向流转状态
4. 执行 jira_transition_issue 流转到中间状态
5. 回到步骤 1，再次查询可用 transitions（循环，直到到达"自测中"）
6. 安全阈值：最多循环 5 次，防止无限循环
```

##### 匹配规则

在每一步的 transitions 列表中，按以下优先级匹配：

1. **"自测"** 相关（如"自测中"、"转自测"、"开始自测"）→ 目标状态，执行后结束循环
2. **"开发"** 相关（如"开发"、"开始开发"）→ 中间状态，执行后继续循环
3. 如果既没有"自测"也没有"开发"，使用 AskUserQuestion 让用户选择

#### 错误处理

- 如果 Jira 评论写入失败，提示用户但不阻断提交流程
- 提示内容：`⚠️ Jira 评论写入失败，但可以继续提交代码`
- 如果状态流转失败，提示用户但不阻断提交流程
- 提示内容：`⚠️ Jira 状态流转失败，请手动将 Jira 状态改为"自测中"`

---

### 10. 执行提交

用户确认后执行：

```bash
# 如果有未暂存的文件，先询问是否暂存
git add <files>  # 仅添加用户确认的文件

# 提交
git commit -m "<message>"
```

**提交后提醒**：
> 提交成功！如需推送到远程仓库，请手动执行 `git push`。

---

## Type 类型定义

| Type | 说明 | 中文示例 | 英文示例 |
|------|------|----------|----------|
| `feat` | 新功能 | feat: 添加用户登录接口 | feat: add user login API |
| `fix` | Bug 修复 | fix: 修复内存泄漏问题 | fix: resolve memory leak |
| `docs` | 文档更新 | docs: 更新 API 使用说明 | docs: update API documentation |
| `style` | 代码格式（不影响逻辑） | style: 统一代码缩进格式 | style: unify code indentation |
| `refactor` | 重构（非新功能、非修复） | refactor: 提取公共解码逻辑 | refactor: extract common decode logic |
| `perf` | 性能优化 | perf: 优化视频解码性能 | perf: optimize video decoding |
| `test` | 添加/更新测试 | test: 添加解码器单元测试 | test: add decoder unit tests |
| `build` | 构建系统/依赖 | build: 升级依赖版本 | build: upgrade dependencies |
| `ci` | CI/配置变更 | ci: 添加 GitHub Actions 配置 | ci: add GitHub Actions config |
| `chore` | 维护/杂项 | chore: 更新 .gitignore 规则 | chore: update .gitignore |
| `revert` | 回滚提交 | revert: 撤销登录功能 | revert: revert login feature |

---

## 示例

### 示例 1：新功能（中文项目，无 Jira）

```
feat: 添加用户认证模块

- 实现 JWT token 生成和验证
- 添加登录/登出接口
- 用户模型增加密码加密
```

### 示例 2：Bug 修复（带 Jira）

```
fix: 修复分享链接中AI摘要按钮显示问题

- 修复按钮在特定条件下不显示的问题
- 优化组件渲染逻辑

Jira: https://jira.cvte.com/browse/SEEWOOS-235479
```

### 示例 3：重构

```
refactor: 简化数据库连接逻辑

- 提取公共连接池配置
- 统一错误处理方式
```

---

## Jira 集成说明

### 前置条件

确保已配置 mcp-atlassian MCP 服务器。配置可以从以下两个位置加载（按优先级）：

1. **项目级配置**：当前项目的 `.claude.json` 文件
2. **用户级配置**：用户目录下的 `settings.json` 文件（如 `C:\Users\{用户名}\.claude\settings.json`）

#### 项目级配置示例（`.claude.json`）

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": ["uvx", "mcp-atlassian"],
      "environment": {
        "JIRA_URL": "https://jira.cvte.com",
        "JIRA_PERSONAL_TOKEN": "your_token_here",
        "JIRA_SSL_VERIFY": "false"
      }
    }
  }
}
```

#### 用户级配置示例（`C:\Users\{用户名}\.claude\settings.json`）

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": ["uvx", "mcp-atlassian"],
      "environment": {
        "JIRA_URL": "https://jira.cvte.com",
        "JIRA_PERSONAL_TOKEN": "your_token_here",
        "JIRA_SSL_VERIFY": "false"
      }
    }
  }
}
```

**注意**：如果两个位置都有配置，项目级配置优先。

### 可用工具

- `jira_get_issue` - 获取 Issue 信息
- `jira_add_comment` - 添加评论（有 Jira 时**必须**调用）
- `jira_get_transitions` - 获取可用状态转换（有 Jira 时**必须**调用）
- `jira_transition_issue` - 切换 Issue 状态（有 Jira 时**必须**调用，流转为"自测中"）

### 状态流转逻辑

Jira 工作流是链式的，可能需要**多步流转**（如"新建"→"开发中"→"自测中"）。必须循环查询 transitions 并逐步推进，直到到达"自测中"。

```
jira_add_comment → 循环 { jira_get_transitions → jira_transition_issue } → 到达"自测中"
     (评论)              (查可用状态)       (逐步流转)
```

1. **添加评论**：根据代码改动内容生成评论并写入 Jira
2. **循环查询可用转换**：调用 `jira_get_transitions` 获取当前可用的 transitions
3. **匹配并流转**：
   - 有"自测"相关 transition → 执行流转，结束循环
   - 没有 → 选"开发"等中间状态执行流转，继续循环
4. **安全阈值**：最多循环 5 次，防止无限循环
5. **失败兜底**：如果无法自动匹配，提示用户手动操作

---

## 注意事项

1. **永远不要自动推送**：这是硬性规则，推送必须由用户手动执行
2. **敏感文件检查**：发现敏感文件必须提醒，由用户决定是否继续
3. **尊重项目风格**：生成的 message 必须符合项目已有的风格
4. **简洁优先**：小改动用简短的 message，大改动才需要详细的 body
5. **不使用 scope**：即使项目历史中有 scope，新提交也不使用
6. **必须询问 Jira**：每次提交前必须询问用户是否有关联的 Jira 链接，这是必要步骤，不能跳过
7. **有 Jira 必须添加评论**：如果用户提供了 Jira 链接，必须根据代码改动内容添加评论到 Jira
8. **有 Jira 必须流转状态**：如果用户提供了 Jira 链接，**必须将 Jira 状态流转为"自测中"**，这是硬性要求
9. **Jira 失败不阻断**：Jira 评论写入或状态流转失败不应阻断代码提交
10. **Windows 中文编码**：curl 请求中包含中文时，必须先用 `Write` 工具写临时文件，再用 `--data-binary @file` 发送，禁止直接内联非 ASCII 字符
11. **MCP 工具 fallback**：如果 `jira_add_comment` 不可用，主动读取 `settings.json` 中的 Jira 配置，用 curl 调 REST API 作为替代方案
