---
name: bug-commit-analyzer
description: Bug Commit Analyzer - 通过 git 历史定位问题引入点，搜索相关可参考的修改记录
author: liaoshengli
version: 0.0.1
---

# Bug Commit Analyzer

通过 git 历史定位问题并提供历史参考。两大核心任务：

1. **根因定位** — 根据问题描述或 log，查找 git 提交记录，定位问题引入点
2. **历史参考** — 搜索当前仓库及远程仓库中是否有同类问题的处理记录，提供可参考的修改方案

## 前置配置

### 本地 git 搜索（无需配置）

开箱即用，所有 `git log / blame / show / diff` 操作无需额外配置。

### 远程 GitLab API 搜索（可选）

内部 GitLab 实例为 `https://gitlab.gz.cvte.cn`。使用时需设置 PAT：

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
```

详细配置方法和 API 用法见 [references/gitlab-api.md](references/gitlab-api.md)。

## 核心能力

- 根据错误信息、关键字、堆栈信息在 git log 中搜索相关提交
- 使用 git blame 追踪具体代码行的变更历史
- 使用 git bisect 思路二分定位问题引入的提交范围
- 对比不同分支/平台（如 main vs release）的提交差异
- 分析 commit diff，判断某笔提交是否为问题根因
- 搜索已有的修复提交，确认问题是否已在他处解决
- 结合 git log、git diff、git show 构建完整的变更时间线
- 访问远程仓库，搜索其他分支/仓库中同类问题的处理记录
- 跨客户/跨机型参考，利用已有的类似修改作为模板
- 通过 GitLab REST API 访问未 clone 的项目/group

## 工作流程

收到问题描述后，按以下步骤进行。完整对话示例见 [references/examples.md](references/examples.md)。

### 阶段一：信息收集

1. **提取关键信息** — 从问题描述中提取：关键字、功能模块名、配置宏名、客户/机型名、文件名
2. **感知上下文** — 识别当前分支名、当前仓库路径，确定涉及的产品线和平台
3. **获取远程数据** — 执行 `git fetch --all --prune` 同步远程分支信息
4. **[P] 获取根提交** — 执行 `git rev-list --max-parents=0 --all | cut -c1-12` 获取所有分支的根提交，保存为 `$ROOTS`，后续所有 `git log` 命令统一用 `| grep -vE "$ROOTS"` 排除

### 阶段二：历史搜索（先找参考，再挖根因）

> **并行原则**：标记为 `[P]` 的步骤互不依赖，应在同一轮中并行发起，不要串行等待。

5. **[P] 搜索已有参考** — 对关键字并行执行 `git log --all --oneline --grep="<keyword>" | grep -vE "$ROOTS"`，跨所有本地+远程分支搜索。搜索 fix/bugfix/feature 类型的相关提交，关注 `[bugfix]`、`[feature]`、`[config]` 标签
6. **[P] 搜索代码变更** — 对每个代码片段并行执行 `git log --all -S "<code_snippet>" | grep -vE "$ROOTS"`，与步骤5并行执行
7. **追踪变更历史** — （场景1适用，场景2可跳过）基于步骤5/6的结果，对关键代码行使用 `git blame` 查看修改时间和作者
8. **分析可疑提交** — 对锁定的候选提交，查看 `git show` / `git diff` 确认变更内容

8.5 **git bisect 二分定位** — （仅场景1）当步骤5-8缩小了嫌疑区间但无法精确到单笔提交时启用。

触发条件（全部满足）：
- 知道问题大概什么时候引入的（如两周前、上个 tag 前）
- 当前问题可以复现验证
- 步骤5-8的 blame/log 搜索指向一个区间但无法确定具体是哪笔

```bash
git bisect start
git bisect bad HEAD
git bisect good <good_commit>     # 从已知正常的 tag/时间点获取
# 每轮二分后提示用户验证，回复 good/bad
git bisect reset                   # 完成后恢复
```

### 阶段二.5：跨仓库远程 GitLab 搜索（本地找不到时启用）

> 触发条件：阶段二的本地 git 搜索没有结果，或问题涉及未 clone 的仓库。
> 详细 API 用法见 [references/gitlab-api.md](references/gitlab-api.md)。

简要步骤：
- 自动检测 `$GITLAB_TOKEN` 是否有效，缺失时提示用户创建
- 从 remote URL 提取 group，查出 group ID
- 列出 group 下项目，按模块名/文件名筛选
- 按优先级搜索分支（客户/机型名 → 模块/功能名 → 全部最近活跃）
- 并行拉取各分支 commit 列表，获取 diff 和文件内容
- 跨客户分支对比，提取修复模式

### 阶段三：影响评估

> 三个维度互不依赖，并行执行。

16. **[P] 搜索符号引用** — 搜索关键宏/函数在整个代码库中的所有引用点
17. **[P] 搜索配置层级** — 对配置宏类问题，搜索完整覆盖链（全局默认 → 产品/客户 → 机型/板卡）
18. **[P] 跨客户对比** — 列出其他客户对同一配置项的值，判断当前设置是否为异常偏离

### 阶段四：输出

19. **给出结论** — 按场景调整输出重心：
    - **场景1（定位引入点）**：可疑提交（hash、作者、日期、commit message）及变更内容 + 修复建议
    - **场景2（搜索参考）**：可参考的 commit 列表（含 diff 摘要） + 实现建议
    - **共用**：风险评估 + 关联文件

## 使用方式

向我提供以下任一信息（会自动判断属于场景1还是场景2）：

**场景1 — 定位问题引入点：**
- 错误日志：完整的 error log、stack trace、crash dump
- 问题描述：发生了什么现象，什么场景下触发，涉及哪个客户/机型
- 复现信息：哪个版本/分支出现问题，之前的版本是否正常（用于 bisect）

**场景2 — 搜索参考实现：**
- 功能需求：需要实现什么功能、涉及的模块/芯片/接口
- 配置需求：需要修改什么配置项，目标值是什么
- 参考查询："有没有人做过类似的修改"、搜索某模块的历史实现

## 行为准则

- **并行搜索，减少等待** — 多个独立的 git log/grep/blame 查询应在同一轮中并行发出
- **先找参考，再挖根因** — 处理新问题时优先搜索是否有历史参考
- 通过 `git rev-list --max-parents=0 --all` 获取根提交，所有 `git log` 结果统一排除根提交
- 执行 `git fetch --all --prune` 同步远程数据后再搜索
- 优先使用 `git log --all --grep` 跨所有分支搜索，不要局限于当前分支
- 不仅找引入问题的提交，也要搜索可能的修复提交（关键字加 fix/repair/resolve 等变体）
- 搜索时注意区分不同客户的同类修改，如 `[bugfix][customer_a]` vs `[bugfix][customer_b]`
- 给结论时包含完整的 commit hash、作者、日期、commit message
- 如果找不到确定的可疑提交，列出所有候选并说明可能性高低
- 对配置类问题，搜索所有定义层级，构建完整的覆盖链路
- **本地优先，远程兜底** — 先在当前仓库用 git log/blame 搜索；仅当本地无结果时调用 GitLab API
- **远程搜索前置条件** — 使用 GitLab API 前检查 `$GITLAB_TOKEN`，未设置则提示用户
- **API 限流** — 批量并行查询时控制在 ~10 并发以内
