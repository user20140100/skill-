---
name: super-commit
description: 超级智能 Git 提交助手。自动检测并安装 git/git-ai 环境，利用 AI 深度分析代码变更生成详细的 changelog 文档，按 Angular 规范生成中文 commit 信息，支持仅提交或推送到指定分支，推送失败自动回退保护代码安全。
author: yuanzihan
version: 1.0.0
---

# super-commit — 超级智能 Git 提交助手

全自动化 Git 提交流程：环境检测 → AI 变更分析 → changelog 生成 → Angular 规范提交 → 智能推送。

## 何时使用本技能

在以下场景中使用 super-commit：
- 用户说「记录一下」「提交代码」「commit」→ 仅执行 git commit
- 用户说「推送」「push」「推到远程」→ 执行 git commit + git push
- 用户说「推送到 dev 分支」「push 到 feature/xxx」→ 推送到指定分支
- 用户说「提交并推送」「记录并推送到 main」

## 触发关键词

记录、提交、commit、推送、push、推送代码、提交代码、记录修改、推到远程、git提交、代码入库

## 执行流程

**严格按以下顺序执行，每一步失败都要向用户报告并停止（推送失败需回退）。**

### 第 1 步：环境检测与安装

#### 1.1 检测 git

```bash
# 检查 git 是否可用
git --version
```

**如果 git 不存在**，按平台自动安装：

| 平台 | 安装命令 |
|------|----------|
| macOS | `xcode-select --install` 或 `brew install git` |
| Ubuntu/Debian | `sudo apt-get update && sudo apt-get install -y git` |
| CentOS/RHEL | `sudo yum install -y git` |
| Windows | 提示用户从 https://git-scm.com/download/win 下载安装 |

安装后重新验证 `git --version`，仍失败则**停止并报告**。

#### 1.2 检测 git-ai

```bash
# 检查 git-ai 是否可用
git-ai --version
```

**如果 git-ai 不存在**，自动安装：

| 平台 | 安装命令 |
|------|----------|
| macOS / Linux | `curl -fsSL "https://gitai.gz.cvte.cn/install.sh" \| API_BASE=https://gitai.gz.cvte.cn bash` |
| Windows (PowerShell) | `powershell -NoProfile -ExecutionPolicy Bypass -Command "[Environment]::SetEnvironmentVariable('API_BASE','https://gitai.gz.cvte.cn','Process'); irm https://gitai.gz.cvte.cn/install.ps1 \| iex"` |

安装后重新验证 `git-ai --version`，仍失败则**停止并报告**。

### 第 2 步：收集变更信息

```bash
# 确保在 git 仓库根目录
GIT_ROOT=$(git rev-parse --show-toplevel)

# 查看当前工作区状态
git status

# 查看暂存区��工作区的完整 diff
git diff
git diff --cached

# 获取当前分支名
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)

# 获取变更文件列表（已暂存 + 未暂存）
git diff --name-status
git diff --cached --name-status
```

**如果没有任何变更**（`git status` 显示 working tree clean），告知用户「没有需要提交的变更」并**停止**。

### 第 3 步：暂存所有变更

```bash
# 将所有变更添加到暂存区
git add -A
```

### 第 4 步：利用 git-ai prompt 分析变更

使用 `git-ai` 的 prompt 能力，基于当前暂存区的 diff 内容，分析本次修改的语义信息。

将 `git diff --cached` 的输出作为上下文传递给 AI 分析，提取以下信息：
- **修改摘要**：本次提交做了什么（一句话概括）
- **变更类型**：feat / fix / refactor / docs / style / test / chore / perf / ci / build
- **影响范围**：哪些模块/组件/功能受到影响
- **详细说明**：每个文件的修改内容与目的

### 第 5 步：生成 changelog 文件

在工程项目根目录下创建 `changelogs/` 目录（如果不存在），并生成以 commit hash 命名的 markdown 文件。

**注意**：此时尚未 commit，先生成临时文件名，commit 后用实际 hash 重命名。

```bash
# 创建 changelogs 目录
mkdir -p "${GIT_ROOT}/changelogs"
```

changelog 文件内容格式：

```markdown
# <commit_hash 前 8 位>

- **提交时间**：YYYY-MM-DD HH:mm:ss
- **提交类型**：<Angular 类型>
- **提交分支**：<当前分支名>

## 修改摘要

<一段话描述本次修改的目的和内容>

## 影响文件

| 文件路径 | 变更类型 | 说明 |
|----------|----------|------|
| src/xxx.ts | 修改 | <该文件的修改说明> |
| src/yyy.ts | 新增 | <该文件的新增说明> |
| ... | ... | ... |
```

### 第 6 步：生成 Angular 规范的中文 commit 信息

根据第 4 步的分析结果，生成符合 Angular Commit Convention 的**中文**提交信息。

**格式**：

```
<type>(<scope>): <简要描述>

<详细说明（可选）>
```

**type 取值**（根据实际变更判断）：

| type | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| docs | 文档变更 |
| style | 格式调整（不影响逻辑） |
| refactor | 重构（非新功能、非修复） |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具/辅助变更 |
| ci | CI/CD 配置变更 |
| build | 构建系统或外部依赖 |

**scope**：影响的模块/组件名（可选，从文件路径推断）。

**示例**：

```
feat(用户管理): 新增用户批量导入功能

- 支持 Excel/CSV 格式批量导入用户数据
- 新增导入进度展示和错误报告
- 增加导入数据校验规则
```

### 第 7 步：执行 git commit

```bash
# 将 changelog 文件也加入暂存
git add changelogs/

# 提交
git commit -m "<生成的 Angular 规范中文 commit 信息>"
```

提交成功后，获取实际的 commit hash：

```bash
COMMIT_HASH=$(git rev-parse HEAD)
SHORT_HASH=$(git rev-parse --short HEAD)
```

**重命名 changelog 文件**为实际的 commit hash：

```bash
mv "${GIT_ROOT}/changelogs/pending.md" "${GIT_ROOT}/changelogs/${SHORT_HASH}.md"
```

如果重命名后文件内容中有占位符，用实际 hash 替换。然后追加提交：

```bash
git add changelogs/
git commit --amend --no-edit
```

### 第 8 步：根据用户意图决定是否推送

**判断用户意图**：

| 用户表述 | 行为 |
|----------|------|
| 「记录」「提交」「commit」 | **仅 commit，不 push**。告知用户提交成功并显示 commit hash |
| 「推送」「push」「推到远程」 | **commit + push**，继续第 9 步 |
| 「推送到 xxx 分支」 | **commit + push 到指定分支**，继续第 9 步 |

如果仅需记录，到此**结束**，输出提交摘要：

```
✅ 提交成功
   Commit: <short_hash>
   分支:   <当前分支>
   信息:   <commit message 首行>
   Changelog: changelogs/<short_hash>.md
```

### 第 9 步：推送到远程

```bash
# 确定目标分支
# 如果用户指定了分支名 → 使用指定分支
# 如果用户未指定 → 使用当前所在分支
TARGET_BRANCH="${USER_SPECIFIED_BRANCH:-$CURRENT_BRANCH}"

# 推送
git push origin "${TARGET_BRANCH}"
```

#### 推送失败处理 ⚠️

**推送失败时必须自动回退到上一个执行断点，并提示用户：**

```bash
# 1. 回退 commit（保留工作区修改）
git reset --soft HEAD~1

# 2. 提示用户
echo "❌ 推送失败，已自动回退 commit（修改内容已保留在暂存区）"
echo "失败原因: <具体错误信息>"
echo ""
echo "常见原因及解决方案："
echo "  1. 远程分支有新提交 → 先执行 git pull --rebase 再重试"
echo "  2. 没有远程仓库权限 → 检查 SSH key 或 token 配置"
echo "  3. 远程分支不存在   → 使用 git push -u origin <branch> 创建"
echo "  4. 网络连接失败     → 检查网络后重试"
```

**回退策略**：
- 使用 `git reset --soft HEAD~1` 回退 commit，保留暂存区的所有修改
- changelog 文件保留在工作区���不删除
- 用户解决问题后可重新触发本技能

推送成功后输出：

```
✅ 推送成功
   Commit: <short_hash>
   分支:   <target_branch>
   远程:   origin/<target_branch>
   信息:   <commit message 首行>
   Changelog: changelogs/<short_hash>.md
```

## 注意事项

1. **不要在 commit 信息中使用英文**：type 关键字保持英文（feat/fix/...），scope 和描述使用中文
2. **changelog 文件必须使用 UTF-8 编码**
3. **推送失败必须回退**：使用 `git reset --soft HEAD~1`，绝不能 `--hard`，要保留用户的修改
4. **分支名处理**：用户可能说「推送到 dev」或「push 到 feature/login」，需要正确解析分支名
5. **合并冲突**：如果 `git add` 或 `git commit` 阶段发现合并冲突，停止并提示用户先解决冲突
6. **大文件警告**：如果 diff 内容超过 10000 行，提醒用户考虑拆分提交
7. **敏感文件检查**：commit 前检查是否包含 `.env`、`credentials`、`secret` 等敏感文件，发现则**警告用户**并等待确认

## 完整执行示例

### 示例 1：用户说「记录一下修改」

```
用户: 记录一下修改

执行步骤:
1. ✅ git 已安装 (v2.43.0)
2. ✅ git-ai 已安装 (v0.5.2)
3. ✅ 检测到 3 个文件变更
4. ✅ 已暂存所有变更
5. ✅ 变更分析完成：新增用户导入功能
6. ✅ 已生成 changelogs/a1b2c3d4.md
7. ✅ 提交成功

✅ 提交成功
   Commit: a1b2c3d4
   分支:   feature/user-import
   信息:   feat(用户管理): 新增用户批量导入功能
   Changelog: changelogs/a1b2c3d4.md
```

### 示例 2：用户说「推送到 dev 分支」

```
用户: 推送到 dev 分支

执行步骤:
1. ✅ git 已安装
2. ✅ git-ai 已安装
3. ✅ 检测到变更
4. ✅ 已暂存
5. ✅ 分析完成
6. ✅ changelog 已生成
7. ✅ 提交成功 (e5f6g7h8)
8. ✅ 推送到 origin/dev 成功

✅ 推送成功
   Commit: e5f6g7h8
   分支:   dev
   远程:   origin/dev
   信息:   fix(登录): 修复 SSO 回调地址错误导致登录失败
   Changelog: changelogs/e5f6g7h8.md
```

### 示例 3：推送失败自动回退

```
用户: 推送代码

执行步骤:
1. ✅ git 已安装
2. ✅ git-ai 已安装
3. ✅ 检测到变更
4. ✅ 已暂存
5. ✅ 分析完成
6. ✅ changelog 已生成
7. ✅ 提交成功 (i9j0k1l2)
8. ❌ 推送失败: rejected (non-fast-forward)
9. ↩️ 已自动回退 commit

❌ 推送失败，已自动回退 commit（修改内容已保留在暂存区）
   失败原因: 远程分支有新的提交，本地落后于远程
   建议: 执行 git pull --rebase 拉取最新代码后重试
```
