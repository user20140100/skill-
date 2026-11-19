# 05-dirty-sync. 未提交代码增量同步子流程

## 目标

在用户尚未 commit 的情况下，基于工作区变更（staged + unstaged + untracked 源码文件）增量更新测试资产（doc → nl → spec）。允许用户在开发过程中提前同步测试用例，不必等到 commit 后才更新。

**不写 sync-state.json**（无 commit sha 可锚定），**不写 sync-log.jsonl**。dirty sync 产物在后续正式 commit + 05-sync 时会被覆盖——dirty sync 是"提前开始"，正式 sync 是"最终对齐"。

## 前置条件

- `01-init.md` 已完成（`.auto-test/` 目录存在）
- `dirty_check.mjs` 输出 `hasDirtyChanges: true`
- 用户确认"基于未提交变更更新测试资产"

## 事故级硬约束

- 禁止重写 doc 主体（只能 append 变更段）
- 禁止写 sync-state.json（没有 commit 可锚定，写了会破坏正式 sync 逻辑）
- 禁止写 sync-log.jsonl（这是 post-commit hook 的职责）
- 禁止覆盖 `manualPin=true` 的 nl/spec
- 禁止主对话替用户 commit/push
- 禁止改源码

## 与 05-sync.md（commit sync）的区别

| 维度 | 05-sync（commit sync） | 05-dirty-sync（本流程） |
|---|---|---|
| 触发源 | git commit（sync-log.jsonl） | 工作区 dirty files |
| 追踪记录 | 写 sync-state.json | 不写 |
| diff 来源 | git log L..HEAD 的 commit diff | git diff HEAD + untracked |
| finalize | 推进 lastSyncedCommit、清空 sync-log | 仅报告更新了哪些资产 |
| 幂等性 | 按 commit sha 幂等 | 弱幂等（doc 层通过 dirtyUpdate 标记段替换实现去重，但 nl/spec 的 incremental 决策基于当前文件内容，工作区变化会产生不同结果） |
| doc 标记 | 无特殊标记 | 变更段标 `dirtyUpdate: true` |

## Agent 启动协议

复用 05-sync 的 agent 模板，仅 mode 参数不同：

| 场景 | 模板 | mode 参数 |
|---|---|---|
| doc 增量更新 | `doc-update.agent.md` | `mode=dirty-diff` |
| 重扫源码（兜底） | `code-fact.agent.md` | `mode=inventory-diff` |
| 重生成 dirty nl | `nl-author.agent.md` | `mode=incremental` |
| 重生成 dirty spec | `generator.agent.md` | `mode=incremental` |

## 步骤

### Step 1: 环境检查

运行 `dirty_check.mjs --root <项目根>`，读取 stdout JSON。

- `hasDirtyChanges: false` → 告知用户"工作区无源码变更"，退出本流程
- `hasDirtyChanges: true` → 继续

回显变更摘要给用户：

```text
检测到 N 个未提交的源码文件变更：
  - staged：X 个
  - unstaged：Y 个
  - untracked：Z 个
开始基于这些变更增量更新测试资产。
```

### Step 2: LLM 判定 dirty diff → 受影响 doc

与 05-sync Step 1.5 目标相同（判定变更命中哪些 doc），但输入不同：

- **05-sync 输入**：commit message + commit diff 文件列表 + prompts（来自 sync-log.jsonl）
- **本流程输入**：仅有 dirty_check 输出的 `diff` 字段（合并 diff 文本）和 `staged`/`unstaged`/`untracked` 文件列表。没有 commit message，没有 prompts（未走 sync_collect）

LLM 需要基于 diff 内容语义判定影响范围，而非依赖 commit message 提供的意图说明。

**confidence 判定策略**（缺少 commit message 辅助时的 fallback）：

- `high`：diff 修改的文件/函数/组件能在某个 doc 的 `linkedSrcHint` 或正文中直接找到对应关系
- `medium`：diff 涉及多个不相关模块，或修改的是横切文件（utils、i18n、shared hooks 等），无法确定唯一 doc
- `medium` 处理策略：**保守全选**——将所有可能相关的 doc 都纳入 hitDocs，由用户在确认环节 edit/skip 收窄范围。宁可多判不漏判

步骤：

1. 扫描 `.auto-test/docs/**/*.md`，提取 docKey/title/首段/linkedSrcHint/linkedNl，汇总到 `.auto-test/.tmp/dirty-sync/doc-catalog.json`
2. LLM 读 dirty_check 输出的 `diff` 字段 + 文件列表，判断命中哪些 doc
3. 输出到 `.auto-test/.tmp/dirty-sync/dirty-doc-mapping.json`：
   ```json
   [
     { "source": "dirty-working-tree", "hitDocs": ["route-key-1", ...], "reason": "...", "confidence": "high|medium" }
   ]
   ```
4. 打印 mapping 给用户确认（yes/edit/skip）；全 skip 直接跳 Step 7

### Step 3: 更新 doc

按 hitDocs 列表，逐 doc 委托 `doc-update.agent.md`（mode=dirty-diff）：

- 输入：dirty diff 文本（来自 dirty_check 输出）+ 当前 doc 内容
- agent append 变更段，变更段头部标记 `<!-- dirtyUpdate: true, ts: ISO时间 -->`
- **幂等机制**：agent 在 append 前必须检查 doc 中是否已有 `<!-- dirtyUpdate: true` 标记段。若存在，**整段替换**（而非再次 append），避免中断重跑后出现重复变更段。判定依据是标记本身，不依赖时间戳或 commit sha
- `mode=dirty-diff` 下 agent 按内容语义去重，而非按 commit sha 幂等
- 正式 05-sync 跑完后这些段会被正式变更段覆盖（05-sync doc-update agent 遇到 dirtyUpdate 标记段时整段替换）

### Step 4: 标 dirty nl + 增量更新

同 05-sync Step 3-4：

1. 读受影响 doc 的 frontmatter `linkedNl`，跳过 `manualPin=true` / `deprecated=true`
2. 给相关 nl 添加 `dirtySince: <ISO时间>` frontmatter 字段
3. 委托 `nl-author.agent.md`（mode=incremental），决策从 {unchanged | patch | new | delete} 四选一
4. 应用结果

### Step 5: 增量更新 dirty spec

同 05-sync Step 5：

1. 委托 `generator.agent.md`（mode=incremental），决策从 {unchanged | patch-static | patch-dynamic | delete} 四选一
2. patch-dynamic 必须用 `playwright-cli` 重新探查，并在 `exploredEvidence` 中记录 session、URL、snapshot 文件或关键输出、页面事实
3. patch 完后必须跑一次 smoke；失败则进 healer 五类根因分诊

### Step 6: 跑 dirty spec（可选）

与 05-sync Step 6 不同，本步骤是可选的而非强制。原因：用户代码尚未提交，可能还在迭代中，强制跑回归的 ROI 不高。但如果用户想验证当前状态的测试覆盖，可以选择执行。

询问用户是否执行更新后的 spec：

```text
已更新 N 个 spec，是否现在执行回归验证？(yes/later)
```

- yes → 转入 `04-spec-run.md`，限定范围 = Step 5 中 action 为 patch-static / patch-dynamic / new 的 spec 集合（排除 action=delete 和 action=unchanged 的）
- later → 跳到 Step 7

### Step 7: 报告 + 清理

**前置条件**：Step 5 的 smoke/healer 已全部完成（无论成功或 escalated）。若 Step 5 的 healer 仍在异步分诊中，等待其完成后再进入本步骤——临时文件可能被 healer 引用。

1. 清理临时文件：`rm -rf .auto-test/.tmp/dirty-sync/`
2. 报告用户：
   ```text
   dirty sync 完成：
     - 更新 doc：A 个
     - 更新 nl：B 个
     - 更新 spec：C 个
     - 执行结果：[已跑/未跑]
   
   注意：这些更新基于未提交代码。commit 后建议跑一次正式 sync（05-sync）对齐最终状态。
   ```

## 中断恢复

dirty sync 无状态锚点（不写 sync-state），中断后重跑即可。doc 层通过 dirtyUpdate 标记段替换实现去重（弱幂等），nl/spec 的 incremental 决策基于当前文件内容，重跑结果与当时工作区状态一致。

## 与正式 sync 的衔接

用户 commit 后触发 post-commit hook → sync_collect.mjs 正常写 sync-log.jsonl → 下次进 skill 自检检测到 pending > 0 → 用户跑 05-sync → 05-sync 的 doc-update agent 遇到 `dirtyUpdate: true` 标记段时**整段替换为正式变更段**（去掉 dirtyUpdate 标记）→ dirtySince 在 05-sync finalize 时统一摘除。

如果 dirty sync 更新的内容和最终 commit 完全一致，正式 sync 仅做验证确认无新增变更，快速通过。
