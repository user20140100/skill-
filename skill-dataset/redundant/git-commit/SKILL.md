---
name: git-commit
description: >
  Create standardized git commits for Bytello Share team with automatic type
  detection, version bumping, Jira integration, and push confirmation. Use when
  the user asks to commit code, create a commit, or mentions "提交", "commit",
  "push". This skill guides through a complete workflow: sync branches → analyze
  changes → detect type → bump version → write message → select Jira → confirm &
  create commit → confirm push.
version: 1.0.15
author: zhangfan3427
---

# Git Commit Skill

为 Bytello Share C++ 团队创建标准化的 git commit，包含自动类型检测、版本号更新、Jira 关联和推送确认。

## 触发时机与前置必要条件

- **适用范围**：仅适用于远程仓库位于 `gitlab.gz.cvte.cn` 的项目。先执行 `git remote get-url origin` 验证；若不属于该 GitLab 实例，说明此 skill 不适用并跳过加载本skill，直接参考历史提交进行创建。
- 用户要求提交代码（"帮我提交"、"commit these changes"、"提交代码"）
- 用户明确提到 "commit" 或 "提交"
- 用户完成开发工作需要提交变更

## 临时提交（最高优先级）

若用户明确表明本次是“临时提交”（包括同义表达），则忽略本 skill 的其他所有规则并跳过所有检查，直接按用户要求创建提交。不要执行同步、版本号更新、Jira 关联、pre-commit、提交格式校验或提交前确认；除非用户明确要求，否则不要推送。

## 完整流程

### 步骤一：同步当前分支与主分支

提交前先同步远程提交，避免基于过期分支创建提交：

1. 获取当前分支名并执行 `git fetch origin`。
2. 若当前分支已配置上游分支，执行 `git pull --rebase --autostash` 拉取当前分支的最新提交；若未配置上游分支则跳过拉取，不要擅自设置上游分支。
3. 通过 `refs/remotes/origin/HEAD` 识别主分支（通常为 `main` 或 `master`）。如果当前分支不是主分支，且相对主分支没有独有提交，可视为刚从主分支切出：先通过 `git fetch origin <主分支>` 更新远程主分支，再执行 `git rebase --autostash origin/<主分支>`。
4. 若 pull 或 rebase 发生冲突，停止后续提交流程，解决冲突并完成 rebase 后再继续；禁止跳过冲突或使用强制推送掩盖问题。

```bash
current_branch=$(git branch --show-current)
git fetch origin

# 已配置上游分支时，拉取当前分支最新提交
if git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
  git pull --rebase --autostash
fi

# 识别远程主分支
main_branch=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
main_branch=${main_branch#origin/}

# 当前分支相对主分支没有独有提交时，同步并 rebase 到最新主分支
if [ -n "$main_branch" ] && [ "$current_branch" != "$main_branch" ] && \
   [ "$(git rev-list --count "origin/$main_branch..HEAD")" -eq 0 ]; then
  git fetch origin "$main_branch"
  git rebase --autostash "origin/$main_branch"
fi
```

若无法从 `origin/HEAD` 识别主分支，询问用户主分支名称，不要自行猜测。

### 步骤二：分析变更

执行以下命令收集变更信息：

```bash
# 1. 查看暂存状态
git status

# 2. 查看暂存的文件统计
git diff --cached --stat

# 3. 查看暂存的详细变更
git diff --cached

# 4. 查看当前版本号，若不存在则跳过版本号相关的配置。常见的版本号文件如 conanfile.py、setup.py
grep "version = " conanfile.py || grep "version:" conanfile.py

# 5. 查看当前分支
git branch --show-current
```

### 步骤三：Pre-commit 检查

检查 pre-commit 环境：

```bash
# 1. 检查 pre-commit 配置文件是否存在
test -f .pre-commit-config.yaml && echo "config exists"

# 2. 检查 pre-commit 工具是否已安装
command -v pre-commit &>/dev/null && echo "tool installed"

# 3. 检查 pre-commit 是否已安装到默认 Git hook 路径
test -x .git/hooks/pre-commit && echo "hook installed" || echo "hook not installed"
```

若配置文件不存在，跳过本步骤。

若配置文件存在但 pre-commit 工具未安装，询问用户是否安装：

```python
question(questions=[
    {
        "header": "Pre-commit",
        "question": "检测到 .pre-commit-config.yaml 但系统未安装 pre-commit 工具，是否安装？",
        "options": [
            {"label": "安装", "description": "执行 pip install pre-commit"},
            {"label": "跳过", "description": "跳过 pre-commit 检查"},
        ]
    }
])
```

若选择"安装"：

```bash
pip install pre-commit
```

若配置文件存在、工具已安装但未安装到 git hook，询问用户是否安装：

```python
question(questions=[
    {
        "header": "Pre-commit",
        "question": "pre-commit 未安装到 git hook，是否安装？",
        "options": [
            {"label": "安装并执行", "description": "执行 pre-commit install 后运行检查"},
            {"label": "跳过", "description": "跳过 pre-commit 检查"},
        ]
    }
])
```

若选择"安装并执行"：

```bash
pre-commit install
```

**配置文件存在、工具已安装且已安装到 git hook 后**，执行 pre-commit 检查：

```bash
pre-commit run
```

#### 检查结果处理

- **检查通过**：继续后续流程
- **pre-commit 自动修复了文件**（如格式化）：重新 `git add` 暂存修改后继续
- **检查失败**：必须修复问题后重试，**禁止跳过或忽略**。处理流程：
  1. 向用户展示 pre-commit 输出的错误信息
  2. 修复所有报告的问题
  3. 重新 `git add` 暂存修改
  4. 重新执行 `pre-commit run` 直至通过
  5. 通过后才可继续后续提交流程

> **禁止使用 `--no-verify` 跳过 pre-commit 检查，任何情况下均不允许。**

#### 提交后发现 pre-commit 错误的处理

若提交已创建但发现 pre-commit 检查存在被忽略的错误，必须：

1. 撤销提交：`git reset --soft HEAD~1`
2. 修复所有 pre-commit 报告的问题
3. 重新暂存：`git add .`
4. 确认 `pre-commit run` 通过
5. 重新创建提交

### 步骤四：推断提交信息

#### 提交类型

根据变更内容自动推断：

| 类型 | 触发条件 | 版本变更 |
|------|----------|----------|
| `feature` | 新增文件、新增功能、新增 API | minor (X.Y.0) |
| `bugfix` | 修复错误、异常处理、崩溃修复 | patch (X.Y.Z) |
| `improve` | 小改进、优化、重构单文件 | patch (X.Y.Z) |
| `refactor` | 代码重构、架构调整 | patch (X.Y.Z) |
| `depend` | 依赖更新、版本锁定 | patch (X.Y.Z) |
| `build` | CI/CD、构建配置、编译选项、配置文件 | patch (X.Y.Z) |
| `doc` | 文档、README、注释 | patch (X.Y.Z) |
| `test` | 测试文件、测试用例 | patch (X.Y.Z) |
| `style` | 代码格式、命名规范 | patch (X.Y.Z) |
| `chore` | 杂项，非必要不使用 | patch (X.Y.Z) |

#### 版本号

- 若 `conanfile.py` 中版本号已手动修改，使用现有版本号
- 否则自动递增：feature → minor，其他 → patch
- 任何修改都必须更新版本号，严禁创建和上一个提交版本号一样的提交

#### 提交描述（首行摘要）

- 描述应当描述**目的**（例如：“实现了xx功能”、“解决了xx问题”），而不是写如何做的。
- 具体如何做的实现细节应当写在 `how` 字段中，不要混入首行描述中。

#### why/how/influence

| 提交类型 | why/how/influence |
|----------|-------------------|
| `bugfix` | **必填**，根据变更内容自动生成 |
| `feature`/`improve`/`refactor`/`depend`/`build`/`test`/`chore` | 建议填写，根据变更内容自动生成 |
| `doc`/`style` | 不填写 |

#### Jira

- 仅 `feature`/`improve`/`bugfix` 类型需要关联
- 调用 MCP-Atlassian 获取 Jira 列表，查询过滤条件使用 `status in (新建, 处理中, 重新打开, 开发中, 打回, 重新打回, Reopened, 已验证-待合入) AND assignee in (currentUser())`，自动匹配最相关的

### 步骤五：更新版本号

若版本号未手动修改，自动更新并暂存：

```bash
# 更新版本号
sed -i 's/version = "X.Y.Z"/version = "X.Y.W"/' conanfile.py

# 暂存
git add conanfile.py
```

### 步骤六：最终确认并提交

若提交携带自动匹配的 Jira ID，在最终确认前通过 MCP-Atlassian 获取该 Jira 的标题、经办人和当前状态，并与 Jira ID 一起展示，避免关联错误；用户明确指定的 Jira ID 可省略这些详情。未分配经办人时显示“未分配”；查询失败时明确说明无法核实，不要猜测。更换为其他自动匹配的 Jira 后，重新获取并展示对应信息，再确认提交。

**使用 `question` 工具一次性展示所有信息**：

```python
question(questions=[
    {
        "header": "确认提交",
        "question": "即将创建以下提交，请确认或修改：\n\n"
                    "提交类型: feature\n"
                    "版本号: 1.3.0\n"
                    "描述: 添加用户登录接口\n"
                    "Jira: PROJ-123\n"
                    "Jira 标题: 支持用户登录认证\n"
                    "Jira 经办人: 张三\n"
                    "Jira 状态: 开发中\n"
                    "why: 需要支持用户身份认证功能\n"
                    "how: 实现 JWT token 验证和 session 管理\n"
                    "influence: 认证模块",
        "options": [
            {"label": "确认提交", "description": "使用上述信息创建提交"},
            {"label": "修改提交类型", "description": "更改为其他类型"},
            {"label": "修改版本号", "description": "手动指定版本号"},
            {"label": "修改描述", "description": "编辑提交描述"},
            {"label": "修改 Jira", "description": "更换或取消 Jira 关联"},
            {"label": "取消", "description": "放弃本次提交"},
        ]
    }
])
```

根据用户选择处理：
- **确认提交**：直接创建提交
- **修改提交类型**：列出所有类型供选择
- **修改版本号**：提供 major/minor/patch 选项
- **修改描述**：让用户输入新描述
- **修改 Jira**：列出 Jira 选项
- **取消**：终止流程

### 步骤七：执行提交

**禁止使用多个 `-m` 参数**，因为 git 会在每个 `-m` 之间自动插入空行，导致 commit-msg hook 校验失败。必须使用单个 `-m` 将所有内容放在一个参数中。

```bash
# Bash / Zsh：使用 $'...' 语法（\n 会被 shell 解释为换行）
git commit -m $'[feature][1.3.0][PROJ-123] 实现了用户登录接口\nwhy: 需要支持用户身份认证功能\nhow: 实现 JWT token 验证和 session 管理\ninfluence: 认证模块'

# PowerShell：使用双引号 + 反引号 n（`n 是 PS 的换行转义）
git commit -m "[feature][1.3.0][PROJ-123] 实现了用户登录接口`nwhy: 需要支持用户身份认证功能`nhow: 实现 JWT token 验证和 session 管理`ninfluence: 认证模块"
```

### 步骤八：确认推送

#### 8.1 检查当前分支

```bash
git branch --show-current
```

#### 8.2 保护分支处理

若当前分支为以下**保护分支**，询问是否创建新分支：
- `main` 或 `master`（主分支）
- 以 `release/` 或 `release-` 开头的分支（发布分支）

```python
question(questions=[
    {
        "header": "分支选择",
        "question": "当前在保护分支，是否创建新分支推送？",
        "options": [
            {"label": "创建新分支", "description": "输入新分支名称"},
            {"label": "直接推送", "description": f"在当前分支 ({current_branch}) 上推送"},
            {"label": "暂不推送", "description": "稍后手动处理"},
        ]
    }
])
```

若选择创建新分支，让用户输入分支名称后执行：

```bash
git checkout -b <new-branch>
git push -u origin <new-branch>
```

#### 8.3 普通分支处理

对于非保护分支，正常确认推送：

```python
question(questions=[
    {
        "header": "推送",
        "question": "提交创建成功！是否推送到远程仓库？",
        "options": [
            {"label": "推送", "description": "执行 git push"},
            {"label": "暂不推送", "description": "稍后手动推送"},
        ]
    }
])
```

## 特殊情况处理

### 完善刚创建的提交

若当前变更仅用于完善刚创建的提交（例如修复该提交引入的构建错误或逻辑异常），则不走常规提交信息、版本号和 Jira 流程，直接创建 fixup 提交：

```bash
git commit --fixup=HEAD
```

创建 fixup 提交前仍须完成适用的 pre-commit 检查；fixup 提交应仅包含对该目标提交的修复。

### 无暂存文件

自动执行 `git add .` 暂存所有文件，无需确认：

```bash
git add .
```

若没有任何变更（既无暂存也无未暂存），提示用户并终止流程。

### 混合类型变更

建议拆分，但允许合并：

```python
question(questions=[
    {
        "header": "混合类型",
        "question": "检测到变更包含多种类型，建议拆分为多个独立提交",
        "options": [
            {"label": "合并提交", "description": "使用推荐类型创建提交"},
            {"label": "取消", "description": "我将重新整理暂存区"},
        ]
    }
])
```

## 提交信息格式

```
[<类型>][<版本号>][<jira号>] <描述>
why: <原因>
how: <方法>
influence: <影响>
```

> 💡 **说明**：
> `<描述>`：描述应当描述**目的**（如实现了xx功能，解决了xx问题），而不是具体如何做的。具体实现细节（how）应该写在下面的 `how` 中。

**示例**：

```
[feature][1.3.0][PROJ-123] 实现了用户登录接口
why: 需要支持用户身份认证功能
how: 实现 JWT token 验证和 session 管理
influence: 认证模块
```

## 关键规则

1. **一次确认**：所有信息在最终确认时一次性展示，无需逐步确认
2. **允许修改**：确认时提供修改各字段的选项
3. **保护分支**：在 `main`/`master` 或 `release*` 分支推送前询问是否创建新分支
4. **一个提交只做一件事**：不混合不相关的变更
5. **版本号必须更新**：仓库里任何文件的修改都必须更新版本号。feature → minor bump，其他 → patch bump
6. **提交描述的侧重点**：描述（首行摘要）应当描述**目的**（例如实现了xx功能，解决了xx问题），而不是具体如何做的。具体实现细节（how）应该写在 `how:` 中。
7. **Jira 规则**：仅 feature/improve/bugfix 类型关联 Jira
8. **使用中文描述**：提交描述和详细段落均使用中文（团队约定）
9. **推送前确认**：询问用户是否推送
10. **Pre-commit 检查**：若存在 `.pre-commit-config.yaml` 且已安装到 git hook，在 `git add` 后自动执行检查
11. **Pre-commit 强制通过**：禁止使用 `--no-verify` 跳过检查；禁止忽略 pre-commit 中的任何错误；若提交已创建但发现存在被忽略的错误，必须撤销提交、修复问题后重新创建提交
12. **完善新提交**：若变更仅修复刚创建提交引入的构建错误或逻辑异常，直接使用 `git commit --fixup=HEAD` 创建 fixup 提交

## 语言偏好

- 提交信息使用中文（团队约定）
- 与用户交互使用用户使用的语言
