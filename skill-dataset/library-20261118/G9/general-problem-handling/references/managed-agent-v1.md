# Managed Agent v1

仅在 `SKILL.md` 已选择 `managed-agent-v1` 后读取本文件。managed 是共享排障核心的托管适配层：Node pipeline 管理 run、预算、终止、SSE、预检和持久化；主控使用多 Agent 执行共享排障流程。

## 1. Managed 前置条件

- 后端必须在启动主控前完成分类 MCP、obs-cli 绝对路径、同目录配置、模型能力和必要 Skill 的环境预检。预检失败直接以 `platform_limit` 结束，不启动模型。
- 主控先读取后端生成的只读 `issue.md`，取得 `run_id`、`app_env`、obs-cli 绝对路径和问题输入。
- 读取 `issue.md` 后只完整读取 `troubleshooting-core.md`，不得 Glob、列举或预读其他 reference；其余文件严格按共享核心中的触发条件延迟加载。
- 分类响应中的 `skillName` 非空时，只能由宿主 Skill 工具精确加载。字段为空表示该分类按设计不需要专属业务 Skill：记录 `business_skill=not_required`，跳过业务 Skill 加载并正常执行共享核心；不得报错、降级或提前结束。此时仍必须先执行共享核心的数据优先门禁：只有数据已按明确规则验证正常，或设计/异常判定标准不清、需要查源码补齐规则时，才可以按 `code-directory-routing.md` 使用分类响应中的 `repositoryId/defaultRef` 调查网关、转发、编排或通用处理流程；标准明确后必须回到数据验证。禁止的只是猜测一个替代 Skill，不能把该禁令扩大成禁止调查。非空名称非法或宿主精确加载失败时，才输出 `服务器内部异常：无法找到skill {skillName}` 并结束。
- 禁止通过分类名、目录遍历、代码搜索、历史路径猜测或替代宿主返回的 `skillName`。
- 只有调查计划实际包含代码证据目标时，才读取 `code-directory-routing.md`；所有 `app_env` 均使用分类返回的 `repositoryId/defaultRef` 和 `aiTroubleShot` MCP。字段缺失、非法或目标为空时按 `platform_limit` 结束，不得猜测仓库或版本。
- managed run 禁止执行 CSkills 安装、同步、发布和个人 MCP 注册；中心环境必须预先具备所需 Skill。
- managed run 不得执行个人上报预览、确认、`submissionId` 生成或调用 `submit_troubleshooting_record`。

## 2. Managed 多 Agent 编排

### 主控

- 按 `troubleshooting-core.md` 形成互不重叠、可验证的证据目标；无依赖方向可并行，有依赖方向必须串行。
- 通过宿主维护 run 范围的任务与事实索引；每次派发前登记 `TaskCapsule`，只把目标、来源边界和完成该任务必要的 FactRef 交给子 Agent。收到结果后登记新增 facts、gaps 和状态，已完成目标仍适用时直接复用，不重复派工。
- 相似目标只有在事实冲突、来源失效、用户输入变化或 review 明确补证时才作为独立任务执行；记录独立目的，不按语义相似自动阻断。
- 调查计划确定后、第一次启动子 Agent 之前，才完整读取一次 `managed-result-contract.md`；禁止在入口阶段预读。
- 至少启动一个 collect Agent；只有共享核心规定的竞争假设、跨来源冲突或直接触发未能区分根因时才启动 inference Agent。
- 主控根据本轮 collect 的来源化事实决定因果链下一跳，再为下一跳创建有依赖的 collect 目标；不得预设固定服务深度，也不得在 collect 只确认“下游超时”时直接收口。
- 准备输出 `concluded` 前必须启动独立 review Agent；`needs_evidence` 时只补采同一目标一次并重新复审。
- 按 `managed-result-contract.md` 输出原文正文，并在末尾追加唯一的 v2 最小控制块；不得启动 translate Agent，也不得把摘要、排查思路、分析判断或结论改写成平台字段。
- 宿主计算的结构效率指标不得发送给子 Agent；任务胶囊和 Agent 交付不包含费用、预算、剩余额度、命中率或收益目标。不得新增 Agent 数量、并发、回合或工具调用限制，也不得改变现有重试、模型和业务证据门槛。

### collect Agent

- 每个 Agent 只负责一个 `TaskCapsule` 证据目标，使用其中必要的 FactRef，按共享核心和业务 Skill 使用 obs-cli、代码或知识能力做只读调查。
- 数据库或日志任务开始前必须读取主控传入的 `obs-cli-tools.md` 准确规则和已验证绝对路径，不得自行猜测语法或依赖 PATH。
- 只返回本任务新增的实际观测、脱敏来源锚点、观测时间和缺口；工具受限时返回 `partial` 或 `blocked` 以及已获事实、缺失证据和错误类别，不重复问题背景或输入中的既有事实。
- 不得给出最终定性、创建嵌套 Agent、写数据库、改配置、发布或改变线上状态。

### inference Agent

- 只接收主控提供的结构化事实和候选假设，不重新调用调查工具。
- inference 不得采集证据、读取源码或调用日志、数据库、MCP；发现证据缺口时只向主控返回明确的下一跳采证建议。
- 比较支持与反对证据，区分直接触发和根因；权威 collect 证据已经闭环时不得启动。

### review Agent

- 独立执行共享核心的复审规则，返回 `passed | needs_evidence | rejected`。
- review 缺失、非法、失败或 rejected 时不得输出 `concluded`。

所有子 Agent 按 `managed-result-contract.md` 直接返回 `AGENT_RESULT`；调用 Agent 工具时 model 参数统一使用 `sonnet`，实际模型路由和计费由服务端记录。

## 3. Managed 运行与输出差异

- `issue.md` 是只读输入，不是 Agent 通信文件。
- 不得创建、读取或恢复 `plan.md`、`context_index.md`、`agent_stepN.md`、facts/analysis/review 的 full 或 summary 文件，以及 translate 输入或输出文件。
- 用户终止、失败重跑或补充信息重跑都创建新 run；旧最终摘要只能作为标明来源的历史参考，旧事实不得自动成为当前事实。
- 工具失败时仍按共享核心输出已有问题摘要、排查思路、事实、失败点和恢复动作，再按 `managed-result-contract.md` 追加最小控制块；不得让最后一条工具错误覆盖已完成调查。
- 子 Agent 结果和最终结果禁止包含 token、认证头、obs-cli 配置正文、完整原始日志、无界数据库返回和不必要源码。
