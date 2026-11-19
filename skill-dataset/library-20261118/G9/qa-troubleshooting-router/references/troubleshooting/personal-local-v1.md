# Personal Local v1

仅在 `SKILL.md` 已选择 `personal-local-v1` 后读取本文件。personal 是共享排障核心和 shared 基础内核的本机适配层：负责本机工具预检、用户确认和对话输出，不重新定义排障步骤。

## 前置 Token 门禁（优先于以下所有步骤）

先执行入口第 0 节及 `references/shared/mcp-setup.md` 的个人 Token 前置检查；未通过时只输出其中的固定最终答复并停止。本文件的 URL 快速路径、工具降级、保留已确认知识、受限收口和任务后反馈规则均不得覆盖该停止条件。

## 0. 入口与版本信息

确认当前入口 Skill 可读取，记录本地版本。按需使用 `references/shared/cskills-loading.md` 查询版本信息；TROUBLESHOOTING 中远端查询不可用只记录版本未核验，不自动安装、同步或中止已有本地能力。实际入口缺失时停止。

## 1. 工具能力报告

记录工具的 `tool/status/code/recovery`，按调查需要检查：项目目录 MCP、`search_project_knowledge`、`load_scoped_markdown`、ccloud-cli、业务 Skill 加载能力。目录 schema 支持 view 时，按共享 MCP 规则核对 `get_project_detail` 和 `resolve_project_candidates`，首次请求 `view:"routing"`；具体线索匹配及候选详情读取复用目录 requestId。ccloud-cli 使用已验证的绝对路径和 shared 工具契约；未验证或无权限的能力不可调用。

个人 Token 门禁已通过且未发生认证失败时，其他工具不可用可继续使用其他已授权渠道；项目目录无法取得且不能建立可信项目范围时，按共享核心保留输入和缺口后受限收口。不得猜测资源或切换未授权服务。安装、同步或 MCP 注册保留原有显式授权要求。用户需要注册 MCP 时读取 `references/shared/mcp-setup.md` 并按其步骤执行。

## 2. 准备 personal 上下文

能力报告就绪后，先完整读取并执行 `troubleshooting-core.md`；由 Core 完成项目选择，并在调查计划前进入 `references/shared/knowledge-loading.md`。本 Profile 不提前解析业务 Skill 或制定另一份计划。

只有共享知识流程到达第三层时，才按 `references/shared/cskills-loading.md` 第 2–4 节解析业务 Skill；安装或同步仍需展示信息并取得用户明确确认。业务 Skill 名称只使用完整项目记录的 `skillName`，不得猜测。数据优先、代码来源和因果追查全部交由 Core；禁止 Glob、列举或预读未触发的 reference。

## 3. personal 执行差异

- 计划、证据和中间状态只保留在当前会话；不得创建或恢复 `.trouble-shooter/`、run 或任何排障 Markdown。
- 主控在当前会话维护任务与事实索引；派发前形成 `TaskCapsule` 并检查 completed task 与 FactRef，只发送目标、来源边界和必要事实。已完成事实仍适用时直接引用，事实冲突、来源失效或 review 补证时允许独立交叉验证。
- 有子 Agent 时可把采集、推断或复审分配出去，子 Agent 只返回新增事实、来源锚点、缺口和角色结果；没有子 Agent 时由当前会话串行完成。不得重复传递完整问题历史、其他 Agent 原文或既有完整结果。
- 因果链存在前后依赖时必须按共享核心逐跳串行推进；不能因为 personal 没有子 Agent，就在定位到下游超时后提前结束。
- 不输出 `AGENT_RESULT`、`MANAGED_RESULT_META` 或 `BUSINESS_SUMMARY` 机器标记，直接按共享核心的公共结果语义回答用户。
- 只有用户明确要求保存最终报告并提供目标路径时才允许导出一份脱敏报告；不得生成中间文件。
- 默认只读，不修改数据库、配置、发布或线上状态；不保存认证信息、完整日志、无界查询结果或不必要源码。
- 不得新增 Agent 数量、并发、回合或工具调用限制；必要工作、现有重试和业务 Skill 证据门槛保持不变。

增强能力只使用宿主在调用前显式声明的 capability，不为探测能力额外启动 Agent、调用工具或安装组件：

- `sessionMemory=true`：可以在当前宿主进程内用结构化内存承载同一索引；退出即释放，不得落盘或跨会话恢复。
- `toolInterception=true`：可以在当前会话对可证明等价的只读请求做透明复用；能力未声明时只做主控级事实复用，不得声称底层请求已被透明缓存。
- `usageTelemetry=true`：只可使用宿主提供的当前会话真实 telemetry 做本地比较，不估算美元，也不默认上传。能力未声明时明确精确用量不可得。

无论 capability 是否可用，子 Agent 都不接收费用、预算、剩余额度、命中率、收益目标或基于成本决定是否继续的指令。personal 不创建 sidecar，不上传原始日志、SQL、源码、完整对话或 telemetry。

门禁通过后的失败仍按共享核心列出问题摘要、排查思路、事实、失败点、限制和恢复动作，不得退化为单行工具报错。

## 4. 可选上报到排查平台

本节只在原有最终答复之后执行，且不得改变已经给出的个人排查结论。本次已完成实际调查，并且最终状态为 `concluded`、`platform_limit`、`input_insufficient` 或 `skill_gap` 时，才可以询问用户是否需要把脱敏结论上报到平台。若流程以 `PERSONAL_TOOL_PREFLIGHT_FAILED` 结束，不得展示排查记录上报选项、不得生成 `submissionId`、不得调用 `submit_troubleshooting_record`。

### 4.1 预览与必填字段

用户表示想了解或提交平台记录时，先展示当前拟提交内容的人类可读完整预览。预览和工具载荷只允许包含：

- 业务元数据：`reporter`、`env`、`module`、`feature`、`orgCode`，五项全部必填；字段缺失时逐项请用户补齐，并重新展示完整预览，补字段本身不得视为提交确认。
- 问题摘要与结论状态：`problemSummary`、`conclusionStatus`，其中结论状态必须保留实际值，不得把 `platform_limit`、`input_insufficient` 或 `skill_gap` 伪装为 `concluded`。
- 最终结论五要素：`conclusion`、`keyEvidence`、`triggerAndRootCause`、`confidenceAndLimitations`、`recommendedActions`。`keyEvidence` 和 `confidenceAndLimitations.limitations` 可以是显式空数组，但字段必须存在。

预览和载荷必须排除原始日志、SQL 结果、源码、完整对话、Prompt、Token、附件、run/session 和模型用量；只可保留足以理解结论的脱敏证据摘要、来源锚点和观测时间。不得因为用户可能确认就放宽最小披露边界，也不得在本地落盘保存预览或载荷。

### 4.2 明确确认后才提交

只有用户对当前完整预览明确确认提交时，才为本次确认生成新的 UUID v4 `submissionId`，并调用一次 `submit_troubleshooting_record`。拒绝、沉默、含糊答复、仅表示了解或继续补充字段都不是确认，必须保持本地结论不变且没有远端副作用。

若用户修改预览中的任一字段，或因工具返回 `VALIDATION_ERROR` 需要修正载荷，旧确认立即失效；必须展示更新后的完整预览，等待新的明确确认，并在再次确认后生成新的 `submissionId`。不得用同一个 `submissionId` 携带修改后的载荷重试。

### 4.3 当前会话内重试与结果

若 `submit_troubleshooting_record` 返回 `retryable=true`，或客户端无法判断首次调用是否已经成功，当前会话可以复用原 `submissionId` 和完全相同载荷重试，并向用户说明这是幂等重试。若工具返回 `VALIDATION_ERROR` 或 `IDEMPOTENCY_CONFLICT`，展示安全错误摘要和恢复动作，不得用同一 `submissionId` 修改后重试。

上报成功后，向用户报告 `issueId`、`issueNo`、`status` 和 `conclusionStatus`，并说明记录已进入平台问题/排查列表。新会话缺少原确认上下文、原始完整载荷或原 `submissionId` 时，不得自动重放旧提交；必须重新执行 personal 门禁、排查或预览确认流程。

`managed-agent-v1` 不得执行本节的预览、确认、`submissionId` 生成或 `submit_troubleshooting_record` 调用。

## 5. 任务完成后的可选反馈

原有排障结论和平台记录上报处理完成后，读取并执行 `references/shared/feedback-collection.md`。反馈是独立的评分收尾，只在用户明确评分后提交上次成功采集后到本次最终答复的新增 user/assistant 问答段；不得把排障记录预览、工具结果或日志放入反馈对话，也不得用反馈工具替代 `submit_troubleshooting_record`。
