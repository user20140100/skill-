# Decision Rules

## 0. summary 验收前置规则

- 主控只能依据**合法 summary**做 closure 判断
- 若 summary 缺少 `## Metadata`、缺少必填字段、或 `closure_level` / `collect_outcome` / `record_match_status` 取值不在契约允许集合内，则该 summary 视为 **invalid**
- invalid summary 默认按 `continue` 处理：不得进入 inference，不得 direct output，不得提升为 `root_cause_closed`
- 对截图表格行 / 列表项 / 卡片类问题，若 `record_match_status = pending`，也不得 final close

## 1. closure_level 含义

- `unresolved`
  当前步骤只拿到局部事实，距离直接触发原因都还没闭合
- `direct_trigger_only`
  已定位“为什么会触发这个现象”，但还没完成“这是不是缺陷 / 是否与权威层一致”的验证
- `root_cause_closed`
  直接触发原因和缺陷定性都已经闭环，且不存在会改变结论口径的未决项

## 2. collect_outcome 含义

- `continue`
  下一步 collect 仍然必需
- `stop_to_inference`
  collect 可以停止；若当前路径已闭环可 direct output，否则再决定 inference
- `plan_exhausted`
  静态计划已跑完，但结论仍未完全闭环

## 3. 哪些 collect 步骤不能省

以下步骤属于“会改变 defect_classification 的必需步骤”，不能因预算或时间压力直接跳过：

- 目标记录锁定 / `not_applicable` 判定
- 多层链路中的跨层一致性验证
- 会把“bug”改写成“系统设计行为 / 非缺陷”的权威规则核验
- 会把“局部层根因”改写成“下游层根因 / 共享契约问题”的验证
- 因 summary schema invalid 而必须进行的同目标补采 / 修复

## 3.1 记录锁定何时可以写 `not_applicable`

以下条件**全部成立**时，最终 `record_match_status` 可以写 `not_applicable`，不强制继续查 UID / DB：

- 结论依赖的是代码级 / 契约级不变式，而不是某条记录的私有字段
- 输入里的可见指纹已足够证明“当前讨论对象就是这一类目标记录”
- 是否锁到具体 UID，不会改变 `direct_trigger` 或 `defect_classification`
- 后续步骤也不需要依赖该记录的数据库字段继续验证

如果任一条件不成立，仍必须完成记录锁定并写 `confirmed`。

## 4. 默认路径与分支展开规则

### 4.1 主控的第一原则

- 主控先沿 `plan.md` 的 `## 本案默认路径` 执行，不默认展开整棵树
- 默认路径必须是当前已知信息下最短、最便宜、最可能改写结论、最可能直接闭环的路径
- `agent_stepN.md` 的 `N` 只是运行时执行序号；它对应“当前正在执行的决策节点”，不是逻辑上的固定 Step 编号
- 每次 collect 完成后，主控都要在 `context_index.md` 中更新 `current_plan_node` 和 `executed_path`
- 旁证、背景补充、兜底节点默认都不是必跑项；只要当前节点已足以闭环，就停止展开未执行分支

### 4.2 何时允许展开兄弟 / 可选分支

仅在以下场景之一成立时，才允许展开兄弟分支或可选分支：

- 当前节点结果否定了默认路径的前提，需要改走另一条路
- 当前节点仍是 `unresolved` / `direct_trigger_only`，且下一结论必须依赖兄弟分支或下游分支
- 该分支属于会改变 `defect_classification` 的必需校验
- 当前节点 summary invalid，且同目标补采后仍必须改走同层备用分支

以下场景不应展开分支：

- 只是“可能还能补更多背景”
- 只是为了补充旁证、增强叙述完整度
- 当前节点已经 `root_cause_closed`
- 只是因为计划里画出了该分支，就机械并行或串行全部跑完

### 4.3 latest summary = invalid

动作：

- 视为当前节点未闭环
- 优先做同一决策目标的补采 / 修复
- 若当前节点已经无法继续支撑该决策目标，再切到同层备用分支

禁止：

- 用主控自行脑补把 invalid summary 提升成 `root_cause_closed`
- 带着 invalid summary 进入 inference
- 直接输出最终结论

### 4.4 latest summary = `collect_outcome: continue`

动作：

- 只写当前真正需要的下一个 `agent_stepN.md`
- 默认优先选择默认路径上的下一个节点
- 若默认路径被当前节点证伪，再切换到必要的兄弟分支

禁止：

- 进入 inference
- 直接输出最终结论
- 为未来可能用到的分支预写一整串 `agent_stepN.md`

### 4.5 latest summary = `closure_level: direct_trigger_only`

如果还存在会改变定性的未决步骤：

- 必须继续 collect
- 优先补当前路径上的下一个必需节点；只有当前路径不再成立时才切兄弟分支

如果静态计划已耗尽：

- 可以进入 inference
- 但最终结论必须明确“缺陷定性待验证”

如果预算不足以完成剩余必需步骤：

- 可以停止 collect
- 但只能输出“不完整结论 / 待验证 / 升级人工”，不能假装已闭环

### 4.6 latest summary = `closure_level: root_cause_closed`

如果同时满足以下条件：

- `collect_outcome = stop_to_inference`
- 当前节点或当前已执行路径已经闭合本案，不再依赖未执行兄弟分支
- `unresolved_items` 不会改变结论口径
- `record_match_status` 已满足当前问题需要
- 计划中的跨层一致性 / 权威校验已完成，或问题天然不需要该步骤

则：

- 应停止展开未执行的兄弟分支 / 可选旁证分支
- **但仍必须执行 inference 和 review 阶段**（可以采用"快速收口"策略简化产物内容，参见 SKILL.md）
- 不允许跳过 inference 或 review 阶段

如果仍有争议性缺口：

- 先 inference 或 review，再决定最终输出

## 5. 预算规则

预算优先级：

1. 目标记录锁定 / `not_applicable` 判定
2. 默认路径上会改变 `defect_classification` 的必需 collect 步骤
3. 因 summary invalid 而必需的同目标补采 / 修复
4. inference
5. review
6. 可选旁证 / 额外背景补充

### 预算不足时允许省的内容

- 非关键背景补充
- 重复性确认
- 可选兄弟分支 / 旁证分支
- inference 和 review 的详细内容（可以采用"快速收口"策略简化产物，但不能跳过这两个阶段）

### 预算不足时不允许省的内容

- 当前路径上仍会改变 `defect_classification` 的 collect 步骤
- 目标记录锁定 / `not_applicable` 判定
- 会阻塞收口的 invalid summary 修复

### 正确动作

如果剩余预算不足以完成必需 collect 步骤：

- 停止继续下游分析
- 输出不完整结论或升级人工
- 明确说明缺的是哪个决策节点，以及为什么这一步不能省

### 错误动作

- “默认路径上的关键节点还没做完，但先去跑旁证分支”
- “Step3 很关键，但预算不够，先跳过，直接 inference”
- “review 很关键，但预算不够，先输出高置信度最终根因”

## 6. inference / review 规则

### inference

仅在以下条件下执行：

- collect 已停止
- 当前已执行路径尚未 `root_cause_closed`

### review

默认规则：

- 如果执行了 inference，通常还要执行 1 轮 review

可跳过 review 的条件：

- collect 已 `root_cause_closed` 且主控 direct output
- 用户明确接受当前最佳结论，无需复审

若 collect 已 `root_cause_closed`，不要为了“把决策树所有分支都走完”再补跑 inference / review。

如果 review 本应执行但预算不够：

- 不得输出“高置信度最终根因”
- 必须把结论降级为待验证或升级人工

## 7. 多层链路定性规则

在以下场景里，`direct_trigger_only` 不能直接等价成“非缺陷”：

- 上层和下层都在做历史判定
- 多层都在做日期 / 时间比较
- 多层都在做状态归一或语义映射
- 本地化封装层与下游服务都可能决定按钮可用性

这类问题必须补齐跨层一致性验证，才能输出：

- `系统设计行为`
- `非缺陷`
- `用户认知偏差`

## 8. 低成本 / 低耗时执行习惯

- 只写当前必需的 `agent_stepN.md`，不要预写一整串不用的步骤文件
- 默认先跑 `plan.md` 中的默认路径，不要把旁证分支和默认路径一起跑完
- `agent_stepN.md` 只对应当前节点；不要把多个兄弟节点塞进同一个采集 Agent
- 当前节点已闭环时，停止展开未执行的兄弟分支 / 旁证分支
- collect Agent 默认只读最新相关 summary，不要全量回读所有历史 summary
- 静态计划优先跑“最便宜且最能改写结论”的步骤；若 DB 锁定 / 背景查询不会改变定性，先做代码 / 契约验证
- 代码检索先看最近的 README / docs，再做 1-3 次定向搜索
- 已拿到最小证据闭环后，不要为了“更完整的背景”继续扩搜
- 不要把“需要处理 record_match_status”机械等价成“必须先查库锁 UID”；能合法写 `not_applicable` 时，要把理由写清楚
- collect 已 `root_cause_closed` 时，不要再形式化跑 inference / review
- 对话里少解释，把证据和判断写进文件

## 9. 阶段进入条件

### 9.1 进入 inference 阶段的前提

- `facts_stepN.md` 和 `facts_stepN.summary.md` 存在（对所有已执行的 stepN）
- 所有 `facts_stepN.md` 包含必需块（参见 `references/artifact-contracts.md`）
- 所有 `facts_stepN.summary.md` 的 Metadata schema valid
- `context_index.md` 的 `latest_collect_outcome` 为 `stop_to_inference` 或 `plan_exhausted`

### 9.2 进入 review 阶段的前提

- `analysis.md` 和 `analysis.summary.md` 存在
- `analysis.md` 包含所有必需块（参见 `references/artifact-contracts.md`）
- `analysis.summary.md` 的 Metadata schema valid

### 9.3 进入 translate 阶段的前提

- `review.md` 和 `review.summary.md` 存在
- `review.md` 包含所有必需块（参见 `references/artifact-contracts.md`）
- `review.summary.md` 的 Metadata schema valid

## 10. 阶段产物校验失败的处理

如果主控在进入下一阶段前发现上一阶段的产物缺失或不合格：

### 10.1 步骤 1：记录告警

在 `context_index.md` 的"当前阻塞/冲突"中写入：

```markdown
- ⚠️ 阶段产物校验失败：{阶段名} 的 {文件名} 缺失或不合格
- 失败原因：{必需块缺失 / schema invalid}
- 缺失的必需块：{列出缺失的块名称}
```

### 10.2 步骤 2：重试

让子 Agent 重新写入产物（最多重试 1 次）：

- 重试时，在 `agent_*.md` 中明确指出缺失的必需块或不满足的约束
- 示例：`"上一次写入的 analysis.md 缺少 ## 缺陷定性 块，请补充"`
- 重试后重新校验

### 10.3 步骤 3：重试失败处理

如果重试后仍然不合格，在最终输出中包含"流程异常告警"块：

```markdown
## 流程异常告警

- 异常阶段：{阶段名}
- 异常文件：{文件名}
- 异常原因：{必需块缺失 / schema invalid}
- 缺失的必需块：{列出缺失的块名称}
- 已尝试重试：是
- 建议动作：请人工检查 {文件名} 并手动补充缺失内容，或重新发起排查
```

### 10.4 注意事项

- 重试不计入预算（因为是子 Agent 的写入失败，不是新的采集任务）
- 如果重试后仍然失败，不要继续重试，直接输出告警并收口
- 告警块必须出现在最终输出的显著位置（建议在结论之前）
