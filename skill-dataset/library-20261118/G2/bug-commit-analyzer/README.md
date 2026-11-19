# Bug Commit Analyzer

通过 git 历史 + GitLab API 定位 bug 引入点和搜索参考实现。

## 两大场景

| 场景 | 输入 | 输出 |
|------|------|------|
| **定位引入提交** | "录音有杂音，定位哪笔提交引入的" | 引入提交的 hash/diff + 修复建议 |
| **搜索参考实现** | "AD82120B 需要加 DRC 配置，搜参考" | 可参考的 commit 列表 + 实现模式 |

## 快速开始

### 1. 安装

将 `SKILL.md` 复制到 `~/.claude/skills/bug-commit-analyzer/SKILL.md`。

### 2. 配置 GitLab Token

使用远程搜索时需要。访问 https://gitlab.gz.cvte.cn/-/user_settings/personal_access_tokens，创建 Token：

- 名称：`work-agent-readonly`
- 权限：`read_api` + `read_repository`

将 Token 写入 `~/.bashrc`：

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
```

### 3. 使用

在 git 仓库中调用：

```
/bug-commit-analyzer
```

或直接描述问题：

```
/bug-commit-analyzer RK3576 录音有杂音，定位是哪笔提交引入的
```

首次使用时 skill 会自动检测 Token 是否已配置，未配置会给出提示。

## 工作流程

```
输入 → 信息收集 → 历史搜索(本地git) → [找不到?] → 远程GitLab搜索
                    ↓                                    ↓
                 影响评估 ←──────────────────────────────┘
                    ↓
                  输出结论
```

## 搜索能力

| 层级 | 方法 | 说明 |
|------|------|------|
| 本地 Commit 消息 | `git log --all --grep` | 跨分支关键词搜索 |
| 本地代码变更 | `git log --all -S` | 特定代码片段增删历史 |
| 本地代码行追踪 | `git blame` | 逐行修改人和时间 |
| 二分精确定位 | `git bisect` | 区间大时自动二分 |
| 远程项目搜索 | GitLab API | 未 clone 的项目/分支 |

## 输出内容

**场景1（定位引入点）**：
- 根因定位：可疑提交的 hash、作者、日期、diff
- 修复建议：具体文件路径和修改方案

**场景2（搜索参考）**：
- 历史参考：可参考的 commit 列表（含 diff 摘要）
- 实现建议：参考已有模式的具体方案

共用：风险评估 + 关联文件



## 行为准则

- 并行搜索：互不依赖的查询同时发起
- 本地优先：先本地 git，找不到再调 API
- 排除根提交：过滤 initial commit 避免噪音
- 跨客户参考：搜索其他客户分支的同类修改
