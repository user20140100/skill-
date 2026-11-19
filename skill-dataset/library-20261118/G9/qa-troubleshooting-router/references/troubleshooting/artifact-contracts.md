# Artifact Contracts

## 共享规则

- `facts_stepN.md`、`analysis.md`、`review.md` 是权威 full artifacts
- `facts_stepN.summary.md`、`analysis.summary.md`、`review.summary.md` 是派生 summary
- summary 不能引入 full 中不存在的新事实
- 若读取了 full artifact，必须在本阶段 summary 中记录：
  - `full_reads_used`
  - `full_read_reasons`

如果 shell 可用，写完 full artifact 后优先用 `shasum` 计算 `source_hash`。

## plan.md

必须包含以下块：

- `# 排查计划`
- `## 问题描述`
- `## 业务知识`
- `## 已知输入摘要`
- `## 目标记录锁定`
- `## 候选假设`
- `## 决策树总览`
- `## 本案默认路径`
- `## 节点卡片`

### 可读性优先规则

- `plan.md` 的主视图必须面向人读；优先输出 ASCII 决策树 + 默认路径 + 节点卡片
- 不要把 YAML / JSON / Mermaid / 邻接表作为主视图；如需机器可读补充，可放在附录，但不是默认要求
- 不要输出平级 Step 清单然后把分支藏在自然语言里
- 默认路径必须清晰标出：当前已知信息下最便宜、最可能直接闭环的执行路径
- 旁证 / 兜底 / 升级人工节点只能作为可选分支出现，不应默认混入默认路径
- 节点数保持最小；通常 3-6 个节点足够，不要为了“完整”预写大量高概率不会执行的分支

### 目标记录锁定最少字段

- `needs_record_lock: yes | no | conditional`
- `lock_scope`
- `target_record_fingerprint`
- `current_match_status: pending | confirmed | not_applicable`
- `lock_rule: 未确认前禁止输出具体 UID / 记录号级结论`

### 每个假设最少字段

- 标题（如 `H1`）
- 优先级
- 为什么怀疑
- 需要验证
- 支持证据
- 反证
- 最小证据闭环

### 每个节点卡片最少字段

- 节点 ID / 标题
- 关联假设
- 目标
- 进入条件
- 支持信号
- 反证信号
- 达成后动作

### 决策树总览最少要求

- 至少有一个起始节点
- 至少有一个终局节点
- 每个非终局节点都要能看出“支持 / 反证 / 不足”时如何流转
- 默认路径必须能从起始节点一路读到一个终局，不要求覆盖所有节点

## context_index.md

必须包含以下块：

- `# 当前运行索引`
- `## 运行元信息`
- `## 当前阶段状态`
- `## 当前可用产物`
- `## 关键事实速查`
- `## 当前开放问题`
- `## 当前阻塞 / 冲突`
- `## Full 回源记录`

### 当前阶段状态最少字段

- `last_executed_step`
- `latest_collect_outcome`
- `latest_closure_level`
- `closure_attribution: concluded | skill_gap | platform_limit | input_insufficient`
- `target_record_match_status: pending | confirmed | not_applicable`
- `matched_record_uid`
- `current_plan_node`
- `executed_path`

## agent_stepN.md

必须包含以下块：

- `# 子 Agent 指令 - StepN: <标题>`
- `## 对应决策节点`
- `## 角色`
- `## 任务目标`
- `## 执行元信息`
- `## 关联假设`
- `## 本步验证规则`
- `## 必须读取`
- `## 执行动作`
- `## 输出文件`
- `## 约束`

### 执行元信息最少字段

- `run_id`
- `current_step`
- `execution_mode: step_collect`
- `next_step_file`
- `plan_node_id`

### 本步验证规则最少字段

- `支持信号`
- `反证信号`
- `最小证据闭环`
- `未达闭环时动作`

### 约束必须覆盖

- 只采集，不输出根因
- 每条事实标注来源锚点
- SQL 先确认表结构
- 禁止写操作
- 禁止编造结果
- 当前步骤必须先写完 `facts_stepN.md` 和 `facts_stepN.summary.md`
- 只执行当前节点，不主动扩展兄弟分支或旁证分支

## facts_stepN.md

**必需块**（缺少任一视为 invalid）：

- `# 采集产物 - StepN: <标题>`
- `## 事实表`
- `## 目标记录锁定`
- `## 采集备注`

**完成判据**：

- 必需块全部存在 → valid
- 缺少任一必需块 → invalid，主控必须让 Collect Agent 重新写入

### 事实表建议列

- 编号
- 事实描述
- 来源锚点
- 原始数据摘要
- 异常标记

### 目标记录锁定最少字段

- `record_match_status: pending | confirmed | not_applicable`
- `matched_record_uid`
- `candidate_records`
- `record_match_evidence`

## facts_stepN.summary.md

必须包含以下块：

- `# Facts StepN Summary: <标题>` 或语义等价标题
- `## Metadata`
- `## 关键事实摘要`
- `## 未解决项`
- `## critical_fact_ids`

### Metadata 必填字段

- `run_id`
- `source_file`
- `source_hash`
- `source_updated_at`
- `closure_level`
- `collect_outcome`
- `record_match_status`
- `covers_fact_ids`
- `critical_fact_ids`
- `omitted_fact_ids`
- `unresolved_items`
- `full_reads_used`
- `full_read_reasons`

### Metadata 建议附加字段

- `plan_node_id`
- `node_result`
- `next_node_candidates`

若缺少 `## Metadata`、缺少任一必填字段、或以下枚举值不在允许集合内，则该 summary 视为 schema invalid，主控不得据此收口：

- `closure_level`
- `collect_outcome`
- `record_match_status`

### closure_level 可用值

- `unresolved`
- `direct_trigger_only`
- `root_cause_closed`

### collect_outcome 可用值

- `continue`
- `stop_to_inference`
- `plan_exhausted`

### record_match_status 可用值

- `pending`
- `confirmed`
- `not_applicable`

### closure_attribution 可用值（运行级归因标签）

- `concluded` — 根因已闭环：`closure_level: root_cause_closed`，证据链完整
- `skill_gap` — 技能覆盖不足：collect 已穷尽计划路径但证据不足以闭环，缺口落在业务 skill 未覆盖的故障路径、未定义的表 / 接口 / 业务规则
- `platform_limit` — 平台限制：预算耗尽（`budget_exhausted`）、工具不可达（ccloud-cli / MCP 报错）、编排异常导致关键步骤跳过
- `input_insufficient` — 用户输入不足：原始 issue 缺少关键上下文（时间窗口、模块名、机构码、具体现象描述），无法继续定向排查

### closure_attribution 判定规则（优先级从高到低）

1. `closure_level: root_cause_closed` → `concluded`
2. `collect_outcome: budget_exhausted` 或 `plan_exhausted` 且预算已达上限 → `platform_limit`
3. collect 已闭环但 `closure_level: direct_trigger_only` 或 `unresolved`，且遗留缺口落在 skill 未覆盖领域 → `skill_gap`
4. 原始 issue 缺少排查入口所需的关键信息 → `input_insufficient`

## agent_inference.md

必须包含以下块：

- `# 子 Agent 指令 - 推断分析`
- `## 角色`
- `## 任务目标`
- `## 必须读取`
- `## 输出文件`
- `## 约束`

### 约束必须覆盖

- 不调用 MCP
- 每条判断引用事实编号
- 区分 `direct_trigger` 与 `defect_classification`
- 证据不足时显式写出

## analysis.md

**必需块**（缺少任一视为 invalid）：

- `# 推断分析`
- `## 问题陈述`
- `## 已确认事实`
- `## 直接触发原因`
- `## 缺陷定性`
- `## 假设验证结论`
- `## 遗留缺口`

**完成判据**：

- 必需块全部存在 → valid
- 缺少任一必需块 → invalid，主控必须让 Inference Agent 重新写入

## analysis.summary.md

必须包含以下块：

- `# Analysis Summary: <标题>` 或语义等价标题
- `## Metadata`
- `## 直接触发原因（direct_trigger）`
- `## 缺陷定性（defect_classification）`
- `## 遗留缺口`
- `## critical_fact_ids`
- `## unresolved_items`

### Metadata 必填字段

- `run_id`
- `phase: inference`
- `source_file`
- `source_hash`
- `source_updated_at`
- `record_match_status`
- `covers_fact_ids`
- `critical_fact_ids`
- `omitted_fact_ids`
- `unresolved_items`
- `full_reads_used`
- `full_read_reasons`

## agent_review.md

必须包含以下块：

- `# 子 Agent 指令 - 独立复审`
- `## 角色`
- `## 任务目标`
- `## 必须读取`
- `## 输出文件`
- `## 约束`

### 约束必须覆盖

- 必读 `analysis.md`
- 定向核验关键 full facts
- 默认采取对抗立场

## review.md

**必需块**（缺少任一视为 invalid）：

- `# 独立复审报告`
- `## 复审立场`
- `## 逐项审查`
- `## 复审结论`

**完成判据**：

- 必需块全部存在 → valid
- 缺少任一必需块 → invalid，主控必须让 Review Agent 重新写入

## review.summary.md

必须包含以下块：

- `# Review Summary` 或语义等价标题
- `## Metadata`
- `## 判定`
- `## 关键核验结果`
- `## 遗留风险`

### Metadata 必填字段

- `run_id`
- `phase: review`
- `source_file`
- `source_hash`
- `source_updated_at`
- `covers_fact_ids`
- `critical_fact_ids`
- `omitted_fact_ids`
- `unresolved_items`
- `full_reads_used`
- `full_read_reasons`

## translate_input.md

由主控写入，内容为技术结论全文（即最终输出的 7 章节 Markdown）。translate Agent 只读此文件。

## agent_translate.md

必须包含以下块：

- `# 子 Agent 指令 - 结论翻译`
- `## 角色`
- `## 任务目标`
- `## 必须读取`
- `## 输出文件`
- `## 输出格式`
- `## 约束`

### 约束必须覆盖

- 不调用 MCP
- 不做代码检索
- 不做额外分析或推断
- 禁止使用技术术语（SQL、API、字段名、表名、状态码、堆栈、日志、配置项等）
- 目标读者为 FAE、售前、400 客服等非技术人员
- 不确定性如实传达

## translate_output.md

必须包含以下四个章节：

- `## 现象` — 用户看到了什么异常表现（日常用语描述）
- `## 原因` — 为什么会出现这个问题（不涉及技术细节）
- `## 影响` — 这个问题对用户 / 业务造成什么影响
- `## 建议动作` — 用户或支持人员应该做什么

每个章节不超过 3 句话。
