# 初始化工作流

## 成功标准

仅当以下条件全部满足时才算初始化成功：

- `.agents/skills/` 已安装 `project-prd-edit`、`project-prd-verify`、`project-prd-clear`、`project-prd-serve`。
- 入口、路由、公开接口、数据模型、业务分支和现有测试均已纳入全量分析。
- 每个用户可感知的细分功能都有一份完整版 PRD。
- 每份细分功能 PRD 由一个全新的独立子代理根据单功能任务包生成；主代理不撰写或汇总正文。
- 每份 PRD 先无损拆出 Feature Point，每个 FP 均完整包含 `prd-writer` 的功能描述、交互逻辑、跳转逻辑、跳转过程逻辑、正向限制、反向限制、异常/空态/错误提示。
- 每个一级分类都有共同 `category_domain`、`category_goal` 和结构化 `category_contract`；每个成员至少有两个 `category_fit` 源码证据，不存在按数量、源码目录或“工具/其他”兜底聚合的不相关成员。
- 每份 PRD 已完成复杂度评估、候选拆解、功能闭环、规则矩阵和行为覆盖；complex PRD 有覆盖全部 FP 的 Mermaid 流程图。
- 无证据的产品意图已标为“待产品确认”，不适用的页面/网络/权限类别已说明不适用证据。
- `.project-prd/INDEX.md` 能索引全部 PRD 及代码入口。
- `manifest.json` 状态为 `complete`，完整性门禁通过。
- `AGENTS.md` 包含且只包含一个 project-prd 受管规则块。

## Phase 0：确定项目根目录与状态

项目根目录必须是当前任务对应的单一版本库或构建项目。禁止使用主目录、`Documents` 或多个仓库的共同父目录。运行时必须支持创建子代理；能力不可用或没有任何可用槽位时返回 `BLOCKED`，不得由主代理代写 PRD 正文。

先执行 `status`：`clean` 可以初始化；`initialized` 立即停止；`partial` 且 `resumable=true` 时从 `.project-prd/.analysis/progress.json` 续跑；`partial` 且 `resumable=false` 时要求先使用 `project-prd-clear`。

## Phase 1：准备工作区

运行：

```bash
python3 <skill-dir>/scripts/bootstrap.py prepare --project-root <project-root>
```

该命令先安装四个项目级 skill，再创建工作区、空任务账本、完整性工具、AGENTS.md 规则和受管 GitHub workflow，并记录这些受管初始化资产的 SHA-256 指纹供续跑与 finalize 前复核。

## Phase 2：全量分析

阅读 `feature-analysis.md`。优先使用项目已配置的结构化代码索引；没有时使用文件清单与源码搜索。在 `.project-prd/.analysis/` 维护临时台账：

| 源码目录/模块 | 文件数 | 已分析 | 功能归属 | 备注 |
|---|---:|---:|---|---|

未归类源码必须在完成报告中列出，不得静默忽略。

同时在 `.project-prd/.analysis/` 建立分类契约表。分类没有成员数量下限；只有一个功能时保留单成员目录。为每个成员验证至少两个共享维度并记录源码证据；不能满足时先拆分类再继续。

`.analysis/` 是初始化临时区：通过 `.gitignore` 排除，也不进入 PRD 索引、manifest 或哈希。初始化中断或门禁失败时保留它用于续跑；成功后可留作本地诊断，但不得提交为 PRD 基线。

## Phase 3：建立 PRD 输入模型

在 `.project-prd/.analysis/` 为每个细分功能建立：

1. 完整行为闭包与源码证据。
2. `complexity` 与 `complexity_reasons`。
3. Feature Point 候选表：先将每个独立触发、阶段、策略/拦截、交互矩阵、外部协作和恢复/清理闭环登记为 `decomposition_candidates`，再一一映射 FP 和 `decomposition_basis`。
4. 每个 FP 的主路径、独立分支、状态转换与外部协作。
5. 每个 FP 的正向限制、反向限制、空态、失败、网络、权限与边界。
6. FP 之间的入口、跳转、回调、恢复和终止闭环，以及 complex 流程的 Mermaid 流程图。
7. 枚举、状态、优先级、文案、策略和权限的代码项/PRD 项对照矩阵。

行为没有分配到 FP 与 PRD 章节时不得开始写作。`decomposition_basis` 数量与 FP 数量不一致时不得开始写作。

## Phase 4：委派生成逐功能 PRD

严格执行“一份 PRD = 一个全新子代理”。这里的一份 PRD 指一个细分功能对应的一个 Markdown 文件，不是单个 FP 章节。同一子代理不得处理第二份 PRD；重试也使用新子代理，防止多个功能正文累积在同一上下文。

### 4.1 主代理职责

主代理只负责：

1. 在 `.project-prd/.analysis/tasks/<task-id>.md` 为每个目标文件写独立任务包。
2. 在 `.project-prd/.analysis/progress.json` 维护 `pending/running/completed/failed`；每项固定记录 `task_id/target_path/agent_id/status/attempt/error` 和 `attempts[]`。`attempts[]` 逐次保留 attempt、唯一 agent_id、状态和精简错误，禁止覆盖历史；只有主代理可写进度文件。
3. 并发上限固定为 `min(4, 可用子代理槽位, 未完成任务数)`；无法确认可用槽位时串行委派。每个子代理只拥有一个任务包和一个唯一目标文件，不得因并发而让两个子代理写同一路径。
4. 要求子代理完成后只返回 `task_id`、目标路径、状态、门禁摘要和缺失字段，不粘贴 PRD 正文。
5. 全部任务完成后执行跨文件校验、生成 INDEX、运行 `finalize` 和完整性门禁。主代理不得亲自撰写 PRD 正文。

### 4.2 任务包字段

每个任务包必须以可解析的 YAML frontmatter 承载固定“任务包字段”，正文可补充说明。以下字段均必填且不得为空：

- `task_id`、唯一 `target_path`、产品/版本/日期/作者和唯一 `prd_id`；
- `category`、`feature`、共享 `category_domain`、`category_goal`、`category_contract`、当前功能 `category_fit`；
- `source_scope`：允许按需补读的当前功能源码范围；`behavior_inventory`：完整 Behavior 清单和 `source_entries`，以及必要的上游/下游关联；
- `complexity`、`complexity_reasons`、连续 `decomposition_candidates`、`feature_points` 和一一对应的 `decomposition_basis`；
- `feature_points` 中每个 FP 的角色、触发、前置、动作、响应、跳转、正反向限制、异常、外部协作、恢复与清理；
- 枚举/状态/优先级/文案/策略/权限规则矩阵；
- `verification_evidence`：现有测试、自动化验证缺口、待确认项；
- `writer_path`、`template_path`、唯一目标文件、禁止触碰的文件列表和 `acceptance_criteria`。

任务包必须自足。`source_scope` 只列真实存在、位于项目内且不经过符号链接的精确相对文件/目录，不接受绝对路径、`..` 或 glob。`writer_path` 固定为 `.project-prd/tools/project-prd-writer/SKILL.md`，`template_path` 固定为 `.project-prd/tools/project-prd-writer/references/prd-template.md`。若某个字段无法从证据确认，先在分析阶段补齐或标记待确认，不得让写作子代理重新做全项目分类。任务包可引用当前功能的精确源码证据；不要附带其他 PRD 正文。

### 4.3 子代理职责与写入隔离

子代理必须完整读取任务包、已安装的 `tools/project-prd-writer/SKILL.md` 及其直接要求的模板契约，只按需读取 `source_scope` 授权的当前功能源码证据。它只写入任务包指定的唯一目标文件，不得写 `.project-prd/INDEX.md`、`manifest.json`、`.history/`、`.analysis/progress.json`、其他任务包或其他 PRD，也不得运行 `finalize` 或 `integrity`。

子代理采用 `prd-writer` 的模块/功能点结构：文档级说明之后，逐 FP 完整重复七章节，再写整体闭环、Behavior 追溯、验证依据和已知缺口。子代理只执行单文件自审，检查任务包字段是否全部映射，并只返回精简结果。

### 4.4 失败、续跑与重试

- 子代理缺输入时返回 `failed` 和缺失字段，不得猜测；主代理补齐任务包后委派新子代理。
- 写作或单文件自审失败时保留目标文件与错误摘要，将进度记为 `failed`；续跑只重派 `pending/failed`，且必须使用新的子代理，不得重写 `completed` 任务。
- 续跑遇到 `running` 时先检查对应子代理是否仍存活；已失联则把最后一次 attempt 标记为 `interrupted`，把当前状态转成 `failed` 后再用新子代理重试，不得永久占用槽位。
- 全局门禁能定位到单文件时，把精简错误交给该文件的新子代理修复；不得由主代理直接改正文。
- 分类契约或跨文件错误说明任务包本身不一致。主代理先统一修正相关任务包，把受影响任务按 `completed → failed → running → completed` 进入返修，并为每个 PRD 分别委派新的子代理，仍保持唯一写入路径且保留全部 `attempts[]`。
- 只在所有任务均为 `completed` 后运行 `finalize`。任何 `failed/running/pending` 项都必须阻止完成锁定。

初始化是主 skill 唯一可以直接创建 PRD 文件的阶段，但正文写入权属于对应的单文件子代理。只提炼可观察的产品行为，不复制实现代码。

## Phase 5：交叉校验

逐项检查：

只有主代理可以生成 INDEX，并执行跨 PRD 分类契约、引用关系和完整覆盖校验；不得以单个子代理成功代替全局校验。

- 每个入口、路由、公开业务接口和业务模型是否有归属。
- 一级分类的成员是否确实共享 domain、goal、contract 与至少两个有证据的 fit 维度，是否存在因“少于 3 个”而错误合并的单成员业务域。
- 每个独立触发、阶段、策略、拦截链、文案矩阵、外部协作和清理是否先形成候选并映射独立 FP；是否达到最低数量后过早停止拆解。
- complex 流程图是否覆盖所有 FP、标明关键分支和失败/恢复出口，且与文字闭环一致。
- 规则矩阵是否逐项覆盖代码枚举、状态、优先级、文案和策略，没有漏项或臆造项。
- 每个 FP 是否按固定顺序恰好一次包含 `prd-writer` 完整七章节。
- 交互逻辑是否从用户/调用方视角完整描述动作与响应。
- 跳转是否闭环；无页面跳转时是否明确标注。
- 数量、格式、角色、状态、生效时机和不支持组合是否准确。
- 异常表是否覆盖空态、操作失败、网络异常、权限不足、边界超限，且展示方式具体。
- 每个行为是否进入“行为覆盖与代码追溯”并归属一个 FP；`source_entries` 是否与源码证据集合精确一致。
- 现有测试是否支持 PRD；没有测试时是否如实记录缺口。
- 代码无法支持的产品原因、价值或文案是否被错写成确定事实。
- 每个目标文件是否有独立任务包和独立子代理完成记录，是否存在一个子代理处理多份 PRD、越权修改其他 PRD 或把完整正文回传主代理。

业务边界或现有行为无法确定时，询问用户；不得臆造。

## Phase 6：完成锁定

确认进度中没有 `pending/running/failed` 后，先由主代理创建 `INDEX.md` 草稿，再由主代理执行 `finalize` 和 `integrity`。`finalize` 会校验全部 PRD、重建索引、生成初始审计记录和 SHA-256 清单。失败时按 Phase 4.4 将错误重新委派到对应单文件子代理；禁止主代理直接修正文，也禁止手写 `manifest.json`。

### 完成结论报告

初始化成功后，主代理必须读取 `finalize` JSON 中的 `feature_coverage` 并在结论报告单列：

- `功能覆盖率`：使用 `covered / total × 100%`，按两位小数展示；
- `已覆盖细分功能数`：已生成 PRD、子代理任务完成且通过全局门禁的目标数；
- `已识别细分功能总数`：全量分析后进入 `.project-prd/.analysis/progress.json` 的任务总数；
- `未覆盖功能清单`：逐项列出 `uncovered`；为空时明确写“无”。

不得根据 PRD 文件数自行估算分母，也不得只写百分比。成功初始化的覆盖率必须为 `100.00%` 且未覆盖功能清单为空；否则结论只能是 `BLOCKED`，不得宣告完成。其余结论项继续报告功能分类数、PRD 数、Feature Point 数、交互步骤、正反向限制、异常项、行为覆盖数、复杂度分布、失败重试数、未归类文件和安装的门禁。
