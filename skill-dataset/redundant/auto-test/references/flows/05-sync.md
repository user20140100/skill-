# 05. 增量同步子流程

## 目标

源码已发生变更（commit 已落）的前提下，按五层链路把变更拉齐到测试资产：

```text
源码 commit → doc → nl → spec → run
```

本流程是"检测 + 双路径更新 + 收尾"，不重写已有主体，只追加增量补丁与重生成下游。

## 前置条件

进入本流程前必须满足，任一不过停止并回退到对应上游：

- 入口自检（`SKILL.md §2.1`）若返回 `warningCode=NOT_INITIALIZED` 或 `STATE_CORRUPTED`，**禁止进入本流程**，必须先回 `01-init.md`。
- `01-init.md` 已完成（含 post-commit hook 装好、`.auto-test/sync-state.json` 已写初值、`.auto-test/scripts/*.mjs` 已就位）
- `.auto-test/sync-state.json` 存在且 `lastSyncedCommit` 非空
- 入口自检（见 `SKILL.md`「入口自检」段）算出 `pending > 0`，并已得到用户授权"现在跑同步"
- git 工作区干净（`git status --porcelain` 为空）
- 当前分支不落后 `origin`（`git fetch && git log HEAD..origin/HEAD` 为空）

任一不过：停止并报告修复路径（让用户先 commit / pull --rebase）。

## 事故级硬约束（本流程专属）

- **禁止重写 doc 主体**。doc-update agent 只能 append 变更段，主对话也不允许直接 Edit 旧 doc 的非 frontmatter 段
- **禁止跳过 LLM 判定环节直接广播**。commit → 受影响 doc 的映射必须由 LLM 在 Step 1.5 显式判定并向用户确认，不允许"看起来相关就标"。dirty 标记沿着 `judgedDocKey → linkedNl → linkedSpec` 传播
- **禁止 manualPin=true 的 nl/spec 被覆盖**。Step 3/5 必须显式跳过
- **禁止主对话替用户 commit / push**。Step 7 finalize 后只能提示，不能 `git commit`
- **禁止改源码**。本流程只动 doc/nl/spec 与 sync-state，绝不修被测项目源码

## Agent 启动协议

沿用 `02 / 03 / 04` 的启动方式：generalPurpose subagent + 模板绝对路径。

| 场景 | 模板（绝对路径） | 作用 |
| --- | --- | --- |
| doc 增量更新（双路径） | `~/.claude/skills/auto-test/agents/doc-update.agent.md` | 按 git-ai 或 inventory-diff 模式 append 变更段 |
| 重扫源码出新 outline（兜底用） | `~/.claude/skills/auto-test/agents/code-fact.agent.md` | mode=inventory-diff 路径下重扫产生新 outline |
| 重生成 dirty nl | `~/.claude/skills/auto-test/agents/nl-author.agent.md` | doc 改后基于新 doc 重写对应 nl |
| 重生成 dirty spec | `~/.claude/skills/auto-test/agents/generator.agent.md` | nl 改后按 03-nl-spec 规则重写对应 spec |

实际调用把 `~` 展开为绝对路径。

## 步骤 0：环境检查

```bash
# 1. 工作区干净（允许 sync-log.jsonl 存在变更，因为 hook 在每次 commit 后会追加）
git status --porcelain | grep -v '^.. \.auto-test/sync-log\.jsonl$'
# 输出非空 → 停止，提示用户先 commit / stash

# 2. 不落后 origin
git fetch
git log HEAD..origin/HEAD --oneline
# 输出非空 → 停止，提示用户 git pull --rebase
```

任一不过 → 停止并报告，禁止"自动 stash / 自动 rebase"。

> `sync-log.jsonl` 是团队共享文件，post-commit hook 会在它上面追加，工作区出现该文件的变更属于正常态，不应阻塞 sync。其它任何文件 dirty 仍要求用户先处理。

## 步骤 1：聚合 pending

调用入口自检脚本拿 pending 全量：

```bash
node ~/.claude/skills/auto-test/scripts/sync_check.mjs --root <项目根>
```

**v0.3 注意**：`sync_check` 只输出 commit SHA 列表和 `hasGitAi` 标志。不包含 diff 文件列表、commit message、prompts。这些信息在步骤 1.2 按需获取。

输出 schema：

```json
{
  "pending": <int>,
  "items": [
    { "commit": "<sha>" }
  ],
  "hasGitAi": true|false,
  "lastSyncedCommit": "<sha>",
  "lastSyncAt": "<ISO>"
}
```

## 步骤 1.2：按需获取 commit 上下文

对每个 pending commit，根据 `hasGitAi` 分路径获取上下文信息：

### 路径 A：有 git-ai

```bash
# 1. 获取用户对话
git-ai search --commit <sha> --json

# 2. 获取变更文件列表和 commit message
git diff --name-only <sha>~1..<sha>
git log -1 --pretty=%B <sha>
```

从 `git-ai search` 输出中提取用户意图：
- 只取 `prompts[*].messages` 中 `type=user` 的条目的 `text` 字段
- **过滤噪音**：
  - 跳过 `<ide_` 开头的文本（IDE 自动注入的选区/文件信息）
  - 跳过超过 200 字的 user message（大概率是 skill/system prompt 注入）
- 将过滤后的 user messages 按时间排序，作为"用户意图摘要"

最终每个 commit 的上下文结构：

```json
{
  "commit": "<sha>",
  "message": "<commit message>",
  "diff": ["src/...", "..."],
  "mode": "git-ai",
  "userIntents": ["帮我同步 docs", "先做测试报告看板"]
}
```

### 路径 B：无 git-ai

```bash
git diff <sha>~1..<sha>              # 完整 diff（含内容，用于语义推断）
git log -1 --pretty=%B <sha>          # commit message
```

上下文结构：

```json
{
  "commit": "<sha>",
  "message": "<commit message>",
  "diff": ["src/...", "..."],
  "mode": "plain"
}
```

### 黑名单过滤

两种路径下，均对 `diff` 文件列表应用 syncIgnore 黑名单（`sync_common.mjs` 的 `DEFAULT_SYNC_IGNORE` + `.auto-test/config.json` 的 `syncIgnore`）。过滤后无文件的 commit 跳过，不进入步骤 1.5。

将所有 commit 的上下文汇总写入 `.auto-test/.tmp/sync/commit-contexts.json`。

## 步骤 1.5：LLM 判定 commit → 受影响 doc

> 设计动机：v0.1 用 doc frontmatter 的 `linkedSrc` 做正向白名单反查，横切文件必然漏。v0.2 改为黑名单 + LLM 语义判定。v0.3 进一步引入 git-ai 用户对话作为判定信号。

### 1.5.1：准备 doc 清单

扫描 `.auto-test/docs/**/*.md`，提取每个 doc 的：

- 路径（相对项目根）
- frontmatter `docKey`、`title`
- 正文首段（限 200 字以内的概述，足够 LLM 理解 doc 范围）
- frontmatter `linkedSrc`（可选 hint，不存在不报错；存在则作为 LLM 判定的辅助信号）
- frontmatter `linkedNl`

汇总成 `.auto-test/.tmp/sync/doc-catalog.json`：

```json
{
  "docs": [
    {
      "docKey": "success",
      "path": ".auto-test/docs/success.md",
      "title": "提交成功页（路由 /success）",
      "summary": "<首段 200 字>",
      "linkedSrcHint": ["src/pages/SuccessPage", "src/router/index.tsx"],
      "linkedNl": ["../case/nl/success/back-to-survey-03.md"]
    }
  ]
}
```

### 1.5.2：让 LLM 做映射

主对话直接做（不必委托 subagent，输入信息有限）。对每个 pending commit：

输入：
- commit message
- diff 文件列表（已被黑名单过滤）
- mode=git-ai 时附 `userIntents`（步骤 1.2 提取的用户意图摘要）
- 完整 doc 清单（1.5.1 产出）

判定原则：
- **git-ai 模式下优先看用户意图**。用户对话直接表达了改动目的（如"修改首页按钮文案"），比 diff 文件名更准确
- **其次看 commit message 与 diff 的语义指向**。例如 commit message 提到"success 页"或 diff 命中 `src/pages/SuccessPage/**` → 命中 success doc
- **横切文件**（如 `src/i18n/*`、`src/theme/*`、`src/utils/*`）：结合用户意图（优先）或 commit message + diff 内容判断具体影响哪几个 doc；不要简单地标记为"影响所有 doc"
- **`linkedSrcHint` 命中可作为强信号但非必要条件**
- **判定不到任何 doc** 的 commit 标 `hitDocs: []`，并给出 `reason`，让用户决定是否需要补建 doc

输出（写入 `.auto-test/.tmp/sync/commit-doc-mapping.json`）：

```json
{
  "mappings": [
    {
      "commit": "abc1234",
      "message": "fix(i18n): 修改'回到首页'文案为小写'home'",
      "hitDocs": ["success"],
      "reason": "用户意图：修改首页返回按钮文案；i18n key result.returnToHome 在 SuccessPage 使用",
      "confidence": "high|medium|low"
    },
    {
      "commit": "def5678",
      "message": "chore: bump deps",
      "hitDocs": [],
      "reason": "依赖升级，未发现影响业务文档"
    }
  ]
}
```

### 1.5.3：向用户确认

把 mapping 表打印给用户：

```text
本次 sync 的 commit → doc 映射判定如下：

  abc1234 fix(i18n): 修改'回到首页'文案为小写'home'
    → success.md  [confidence: high] 原因：i18n key result.returnToHome 在 SuccessPage 使用

  def5678 chore: bump deps
    → 未识别 doc      原因：依赖升级，未发现影响业务文档（可忽略 / 标记需关注？）

请确认（yes 全部接受 / edit 修改某条 / skip <commit> 忽略某条）
```

- 用户接受后，进入 Step 2，按 docKey 聚合用 1.5.2 的 mapping 结果（不再用 linkedSrc 反查）
- 用户对某条 commit 选 edit → 主对话允许追加/移除 hitDocs 后重新打印
- 用户对某条 commit 选 skip → 该 commit 不参与 Step 2，但 Step 7 推进 sync-state 时仍计入"已消费"
- 全部 commit `hitDocs` 都是 `[]` 且用户全 skip → 直接跳到 Step 7（仅推进 sync-state，不更新任何 doc/nl/spec）

按 **docKey** 聚合（多个 commit 影响同一 doc → 合并到一个处理单元）：

```json
{
  "<docPath>": {
    "commits": ["abc...", "def..."],
    "hasGitAi": true,
    "userIntentsByCommit": {"abc...": ["修改首页按钮文案"]},
    "diffByCommit": {"abc...": [...], "def...": [...]},
    "messages": {"abc...": "...", "def...": "..."},
    "linkedNl": ["...", "..."]
  }
}
```

`linkedNl` 来自 doc 的 frontmatter `linkedNl` 字段；缺字段时停止并报告（doc 没有正确建立链路就不能跑增量）。

## 步骤 2：双路径更新 doc

`for each docKey`：

### 路由判定

```text
hasGitAi 且该 docKey 至少一个 commit 有 userIntents → 方案 A
其余（无 git-ai 或 userIntents 为空）                  → 方案 B
```

只要有一个 commit 带用户意图就走方案 A，其余 commit 仅贡献 diff 文件名作为辅助上下文。

### 方案 A：语义路径

1. 把该 doc 涉及的所有 commit 的 userIntents + diff/message 写到临时文件 `.auto-test/.tmp/sync/<docKey>-context.json`
2. 委托 `doc-update.agent.md`：
   ```text
   Launch a generalPurpose subagent with prompt:

   请先读取并严格遵循 ~/.claude/skills/auto-test/agents/doc-update.agent.md。

   任务：按 git-ai 模式 append 变更段到指定 doc
   输入：
   - mode: git-ai
   - 旧 doc 路径：<绝对路径>
   - 旧 doc sha256：<hash>
   - 上下文 JSON：.auto-test/.tmp/sync/<docKey>-context.json（含 userIntents）
   - commit 列表：[abc, def]
   - 输出路径：与旧 doc 同路径覆盖
   约束：只追加变更段，绝不改主体；幂等检测重复段直接跳过。
   输出：按模板返回 {path, mode, status, ...} 摘要
   ```
3. 接收 agent 摘要，更新本流程内存中的"已处理 docKey 列表"

### 方案 B：兜底路径

1. 委托 `code-fact.agent.md` 重扫 `componentRoot` 下与该 docKey 相关的源码：
   ```text
   任务：重扫源码生成新 outline，输出到 .auto-test/.tmp/sync/<docKey>-outline-new.md
   ```
2. 主对话直接读 `.auto-test/.tmp/sync/<docKey>-outline-new.md` 与现有 doc 正文（`.auto-test/docs/<docKey>.md` 的非 frontmatter 部分）进行**语义对比**，归类为：新增 feature / 删除 feature / 文案变更 / 字段变更 / 行为变更，写入 `.auto-test/.tmp/sync/<docKey>-inventory-diff.md`
3. 委托 `doc-update.agent.md`：
   ```text
   任务：按 inventory-diff 模式 append 变更段到指定 doc
   输入：
   - mode: inventory-diff
   - 旧 doc 路径：<绝对路径>
   - 上下文 JSON：包含 inventoryDiff（指向上一步 .md）+ diff + message
   - 输出路径：与旧 doc 同路径覆盖
   约束：措辞保守（"根据源码改动推断"），不能编造意图
   ```

> outline 较大（>500 行）时，主对话不要把全文喂回 doc-update agent，让 agent 直接读临时文件路径。

## 步骤 3：标 dirty nl

`for each` Step 2 已更新的 docKey：

1. 读 doc frontmatter 的 `linkedNl` 列表
2. 对每个 nl 路径读 frontmatter：
   - `manualPin: true` → **跳过**（人工锁定）
   - `deprecated: true` → **跳过**（已废弃）
   - 否则 → 加 `dirtySince: <最早未同步的 commit hash>` 字段（已存在则保留较旧值）
3. 用 Edit 工具写回（仅改 frontmatter，不动正文）

## 步骤 4：增量更新 dirty nl

**默认走增量 patch，不走全量重写**。理由：nl 多为简短中文用例，文案 / 字段 / 提示语级改动占比最高；全量重写会浪费 token 并丢失人手痕迹。

`for each` 标了 `dirtySince` 的 nl（串行，不并行）：

### 4.1：委托 `nl-author.agent.md` 决策（mode=incremental）

```text
任务：判断该 nl 在本次 doc 变更下需要如何调整
输入：
- mode: incremental
- nl 路径：<旧 nl 绝对路径>
- doc 路径：<新版 doc>
- doc 本次变更段：<Step 2 写入的 ## 变更 @ <commit-short> @ <ts> 段落原文>
- plan 路径：<frontmatter.planRef>
- 是否有代码事实摘要：<config.componentRoot 有则 true>
约束：
- 决策必须从 {unchanged | patch | new | delete} 四选一，禁止 rewrite
- patch 必须返回 search/replace 字符串对（旧串需在 nl 中唯一），主进程统一应用
- new 用于变更引入了原 nl 未覆盖的新行为，要求给出新 nl 文件草稿（含 frontmatter）
- delete 用于变更移除了某个功能（不真删文件，主进程会改 frontmatter.deprecated=true）
输出：结构化 JSON
{
  "action": "unchanged|patch|new|delete",
  "reason": "<一句话原因>",
  "patches": [{"old": "<旧串>", "new": "<新串>"}, ...],
  "newNl": {"path": "...", "frontmatter": {...}, "body": "..."},
  "deprecateReason": "..."
}
```

### 4.2：主进程应用结果

- `action=unchanged`：什么都不做，仅 finalize 时摘除 `dirtySince`
- `action=patch`：主进程对每个 `{old, new}` 在 nl 文件上做 Edit；**old 在文件中必须唯一**，命中 0 次或 ≥2 次直接拒绝并报告（agent 定位错位）
- `action=new`：主进程按 `newNl.path` 写入新文件，并在 doc 的 `linkedNl` 数组追加该路径
- `action=delete`：主进程在 nl 的 frontmatter 加 `deprecated: true` 与 `deprecatedReason`、`deprecatedSince: <commit>`；**不删文件**；后续步骤 5/6 跳过该 nl

### 4.3：硬约束

- nl 的 `caseId` / `docRef` / `planRef` 不允许 patch 修改
- patch 后的 nl 仍需通过 nl-author 的"每条预期可追溯到操作步骤""behaviorRefs 必填"等校验；主进程在应用 patch 后做一次轻量自检，不通过则回退本次 patch 并报告
- agent **禁止**直接 Edit nl 文件，必须返回 patches 让主进程统一应用

## 步骤 5：增量更新 dirty spec

**默认走增量 patch，不走全量重写**。spec 的改动按"是否需要重新探查页面"二分。

`for each` Step 4 处理过的 nl（含 patch / new；unchanged 跳过；delete 走 5.4 的废弃流程）：

### 5.1：定位 spec

- nl frontmatter 的 `linkedSpec` 有 → 用旧 spec 路径
- 无（来自 `action=new`）→ 按 03-nl-spec 命名约定推算新 spec 路径，转 03 流程做全量生成
- 旧 spec frontmatter `manualPin: true` → 跳过
- 旧 spec frontmatter `deprecated: true` → 跳过（不应出现，报告异常）

### 5.2：委托 `generator.agent.md` 决策（mode=incremental）

```text
任务：判断该 spec 在 nl 变更下需要如何调整
输入：
- mode: incremental
- spec 路径：<旧 spec 绝对路径>
- 新版 nl 路径
- nl 本次 patch 摘要（步骤 4 产出的 patches 列表）
- _selectors.ts / _mocks.ts 路径
- baseUrl / storageStatePath
约束：
- 决策必须从 {unchanged | patch-static | patch-dynamic | delete} 四选一，禁止 rewrite
- patch-static：纯文本类（断言文案、URL 字符串、selector 名引用），不需要打开浏览器
- patch-dynamic：涉及页面行为变化（按钮新增、跳转目标变了、表单结构变化），必须用 `playwright-cli` 重新探查具体那一段后，再返回 patches 与/或 _selectors.ts / _mocks.ts 的回写内容
- delete：仅在 nl action=delete 时使用
输出：结构化 JSON
{
  "action": "unchanged|patch-static|patch-dynamic|delete",
  "reason": "...",
  "specPatches": [{"old": "...", "new": "..."}, ...],
  "selectorsPatches": [{"old": "...", "new": "..."}, ...],
  "mocksPatches": [{"old": "...", "new": "..."}, ...],
  "exploredEvidence": "<patch-dynamic 必填，简要列出本次使用的 playwright-cli session、打开了哪些页面、snapshot 文件或关键输出、读到了哪些事实>"
}
```

### 5.3：主进程应用 + smoke

- 应用 specPatches / selectorsPatches / mocksPatches（同样 old 必须唯一）
- patch 完后**必须**跑一次 smoke：`PLAYWRIGHT_JSON_OUTPUT_FILE=<reportPath> npx playwright test <specPath> --reporter=json` 单条（禁止用 stdout 重定向，RTK 会截断）
- smoke 不通过 → 进入 04-spec-run 的 healer 五类根因分诊；若 healer 仍失败，把 spec 的 `dirtySince` 保留，不进入步骤 7 finalize（避免推进 sync-state 把失败掩盖）

### 5.4：废弃流程（action=delete）

- 把 spec 顶部所有 `test(...)` 改成 `test.skip(...)` 并在 skip 第一参后追加 `// deprecated: <reason>`
- 在 spec 文件 frontmatter（顶部 `/* ... */` 注释块的链路四元组之外）追加 `// deprecated: true` 标记
- 不进 04-spec-run 的回归范围

### 5.5：硬约束

- spec 顶部链路四元组（nl/plan/doc/caseId）不允许 patch 修改
- patch 不允许引入裸 selector（必须仍走 `_selectors.ts`），不允许引入 inline `page.route`（必须仍走 `_mocks.ts`）
- agent **禁止**直接 Edit spec 文件，必须返回结构化 patches 让主进程统一应用
- agent 决策为 `patch-dynamic` 但 `exploredEvidence` 为空或未实际调用 `playwright-cli` → 视为不可信，主进程拒绝并要求重做

## 步骤 6：跑 dirty spec

转入 `04-spec-run.md`，**限定范围 = Step 5 已更新的 spec 集合**：

- 不跑全量回归（避免污染本次 sync 的因果）
- healer 失败分诊照常走 04 的五类根因 + escalated 路由
- 04 完成后回到本流程 Step 7

## 步骤 7：finalize（LLM 直接做，不调脚本）

按顺序执行：

1. **推进 sync-state**：
   ```bash
   git rev-parse HEAD     # 拿 newCommit
   ```
   用 Edit 改 `.auto-test/sync-state.json`：
   ```json
   {
     "lastSyncedCommit": "<newCommit>",
     "lastSyncAt": "<ISO 时间戳>",
     "lastSyncBy": "<git config user.name>"
   }
   ```

2. **truncate sync-log**：
   ```bash
   : > .auto-test/sync-log.jsonl
   ```
   `sync-log.jsonl` 是团队共享文件（已进 git），truncate 后留空文件而不是删除；finalize 完成后会和 `sync-state.json` 一起被用户 commit & push，团队其它成员 pull 后即可获得"已消费"信号。

3. **摘除 dirtySince**：用 Edit 工具遍历 Step 3/5 加过 `dirtySince` 的 nl/spec frontmatter，删除该字段

4. **清理临时文件**：
   ```bash
   rm -rf .auto-test/.tmp/sync/
   ```

5. **报告用户**：
   ```text
   增量同步完成：
   - 处理 commit: N 个 (git-ai X / plain Y)
   - 更新 doc: A 个
   - 重生成 nl: B 个 / 跳过 manualPin: C 个
   - 重生成 spec: D 个
   - 04-spec-run 结果: passed=P / fixed=Q / fixmed=R / escalated=S

   请 review 后手动 git commit & push（skill 不替你 commit）。
   注意：本次 commit 必须包含 .auto-test/sync-state.json 与 .auto-test/sync-log.jsonl，
   团队其它成员 pull 后才能拿到推进过的同步水位线和已消费的攒料记录。
   ```

## 步骤 8：完成判定

唯一判定条件：

- `sync-state.json.lastSyncedCommit` 已推进到新 HEAD
- 所有 dirty nl/spec 都被处理（重生成 / manualPin 跳过）二选一，无悬空
- 04-spec-run 已跑完且无悬空 escalated（escalated 已走 04 步骤 6 路由报告用户）

任一不满足停止并报告卡在哪一步。

## 中断恢复

任何 Step 中断（崩溃、用户取消）后再进 skill：

- 入口自检仍会算出 pending > 0（因为 sync-state 没推进）
- 重跑本流程：doc-update agent 的幂等机制会跳过已 append 的变更段
- nl/spec 重生成是覆盖式，重跑不会损坏

唯一例外：Step 7.3「摘除 dirtySince」如果只摘到一半，下次重跑会少标记一些 nl，可能漏更新。**所以 Step 7 的 4 个子步骤必须当作一个原子组完成**，不能中途让用户做其它事。

## 多人协同

```text
A 跑完 sync ──push──► sync-state(lastSyncedCommit=A_HEAD)
                          │
                          ▼
                    B git pull
                          │
                          ▼
              B 进 skill, 入口自检
              git log A_HEAD..HEAD
              A 处理过的 commit 因 lastSyncedCommit 推进自动跳过
              只剩 B 自己的 commit 进 pending
```

冲突处理：

- `sync-state.json` 多人 push 撞车 → 取较晚 commit 作为 `lastSyncedCommit`，手工 git merge
- `sync-log.jsonl` 多人 push 撞车 → 该文件是仅追加的 jsonl，按"行级 union"合并（保留双方所有行，按 `commit` 字段去重），不发明业务合并算法
- `docs/nl/specs` 多人 push 撞车 → 走标准 git merge，本 skill 不发明合并算法
- 跑本流程的人**默认要求 git 干净 + 已是最新**，Step 0 强制校验

### sync-log 共享后的审计作用

`sync-log.jsonl` 进 git 后，v0.3 起仅记录 `{date, commit}`，作为审计日志：

- A commit 完触发 hook 写一行到 sync-log → A 直接 push
- B pull 拿到 A 的 commit
- B 跑 sync 时，sync_check 用 `git log L..HEAD` 找 pending（不依赖 sync-log），步骤 1.2 按需查 git-ai + git diff 获取上下文
- git-ai 的对话记录存储在 git notes 中，任何有 git-ai 的团队成员都能查到任意 commit 的对话

> v0.2 → v0.3 的变化：sync-log 不再承载 prompts/mode 数据，团队语义不再依赖 sync-log 传递。只要团队成员装了 git-ai，`git-ai search --commit` 即可直接拿到任何 commit 的对话。

## 与其它子流程的边界

- 02-doc-plan-nl：从无到有创建 doc/plan/nl。本流程**不**走 02，只在已有链路上做增量
- 03-nl-spec：从 nl 生成 spec。本流程 Step 5 复用 generator agent，但不走 03 的全套首跑 smoke
- 04-spec-run：批量回归 + 失败分诊。本流程 Step 6 限定范围调用 04，结果回流本流程
- 05-dirty-sync：未提交代码的增量同步。dirty-sync 是"提前开始"，本流程是"最终对齐"。当本流程 doc-update agent 遇到 `<!-- dirtyUpdate: true -->` 标记段时，整段替换为正式变更段（去掉 dirtyUpdate 标记）。dirty-sync 产生的 `dirtySince` 字段在本流程 Step 7 统一摘除

## 不能跳过的理由

- 跳过 Step 0 → 在脏工作区跑同步，doc/nl/spec 的改动和用户未提交改动混在一起，无法回滚
- 跳过 Step 1.2 上下文获取 → 后续步骤无 diff 信息、无用户意图，LLM 判定纯靠 commit SHA 猜测，必然误判
- 跳过 Step 1.5 LLM 判定与用户确认 → 要么漏判（横切文件不命中任何 doc）、要么误判广播（一刀切影响所有 doc），都会导致 doc 无意义增量段或测试覆盖缺失
- 跳过 Step 2 双路径判定 → 全走方案 B，丢失 git-ai 的用户意图信息，doc 增量段措辞保守失真
- 跳过 Step 3 manualPin 检查 → 用户手动维护的 nl 被覆盖
- 跳过 Step 6 → 改完 nl/spec 不跑回归，等于没验证增量是否破坏既有用例
- 跳过 Step 7 → sync-state 不推进，下次进 skill 又被算成 pending，团队其他人也跟着重复处理
