# Personal Local v1

仅在 `SKILL.md` 已选择 `personal-local-v1` 后读取本文件。personal 是共享排障核心的本机适配层：负责本机工具预检、CSkills 安装授权和对话输出，不重新定义排障步骤。

## 0. 排查前检查 CSkills 远端版本

本节只用于 personal，必须在必需工具硬门禁、业务语境询问、证据采集、排查工具调用或文件操作之前完成。managed 不得执行本节，也不得因本机 CSkills 状态或远端版本查询失败而阻断。

1. 读取当前已加载 `SKILL.md` frontmatter 中的 `version`，作为本地版本。
2. 执行只读命令 `cskills info general-problem-handling`，从输出的 `Version:` 字段获取远端版本。
3. 按语义化版本比较远端版本与本地版本，不得用字符串字典序比较，也不得仅依赖缓存的同步时间或安装索引推断。
4. 远端版本不高于本地版本时，记录版本检查已通过并继续 personal 工具门禁。
5. 远端版本高于本地版本时，立即停止后续排查并引导用户执行：

   `cskills sync general-problem-handling --pull-only`

   告知用户更新完成后重新加载 Skill 或新开会话，再重新执行本节检查。用户明确拒绝更新时，不得继续使用当前旧版本执行排查。
6. `cskills` 不可用、远端查询失败或版本无法解析时，明确告知用户“未能完成远端版本校验”及实际错误；不得声称当前已是最新版，也不得绕过门禁继续排查。

不得自动执行同步、安装或发布命令；更新操作必须由用户确认并执行。

## 1. 必需工具硬门禁

在询问业务语境、读取 `troubleshooting-core.md`、加载业务 Skill 或开始排查前，独立检查全部三项，最后一次性汇总：

1. **CSkills**：执行 `cskills version`，要求命令存在且版本不低于 `5.5.0`。缺失记为 `CSKILLS_NOT_FOUND`，版本过低记为 `CSKILLS_VERSION_UNSUPPORTED`；只提供安装或升级指引。
2. **分类 MCP**：实际调用 `get_trouble_categories`，要求响应可用于分类。失败记为 `CLASSIFICATION_MCP_NOT_AVAILABLE`；成功时保留完整响应，后续不得重复调用。
3. **obs-cli**：完整读取 `obs-cli-tools.md`，按 personal 路径解析规则检查用户显式路径或 `command -v obs-cli`。候选必须是存在且可执行的绝对路径，`--help` 成功且同目录存在 `obs-cli.json`；只检查配置存在性。

输出包含 `tool`、`status`、`code`、`recovery` 的预检矩阵。只有三项均为 `passed` 才继续。任一失败时输出 `PERSONAL_TOOL_PREFLIGHT_FAILED` 并结束：

- 禁止询问业务语境、读取 `troubleshooting-core.md`、加载业务 Skill、开始调查或生成任何文件。
- 分类 MCP 缺失时可以完整读取 `mcp-setup.md` 并展示一键注册选项；只有用户明确确认后才能使用 `sh` 运行 canonical Skill 内的脚本。
- 注册后返回 `MCP_SESSION_RESTART_REQUIRED`；新会话重新执行全部门禁。

## 2. 准备 personal 上下文

门禁通过后：

1. 执行入口 `SKILL.md` 的共享业务语境路由。
2. 选定分类后才完整读取 `cskills-loading.md`；业务 Skill 名称只使用分类响应中的 `skillName`，不得猜测。`skillName` 为空是预期配置，按该 reference 跳过业务 Skill 加载并继续通用排障；仍必须遵守共享核心的数据优先门禁，不得直接跳到代码调查。
3. 根据可用业务 Skill（若有）和问题输入形成调查计划；先建立数据证据目标，只有数据已按明确规则验证正常，或设计/异常判定标准不清需要查源码补齐规则时，才允许建立代码证据目标并读取 `code-directory-routing.md`。使用分类返回的 `repositoryId/defaultRef` 建立 MCP 代码来源，查清规则后必须回到数据验证。
4. 业务 Skill 未安装或版本落后时，按 `cskills-loading.md` 展示信息并取得用户明确确认后，才可安装或同步。
5. 完整读取并执行 `troubleshooting-core.md`。

除工具门禁固定需要的 `obs-cli-tools.md` 外，禁止 Glob、列举或预读其他 reference；全部按 `troubleshooting-core.md` 的触发条件渐进加载。

## 3. personal 执行差异

- 计划、证据和中间状态只保留在当前会话；不得创建或恢复 `.trouble-shooter/`、run 或任何排障 Markdown。
- 主控在当前会话维护任务与事实索引；派发前形成 `TaskCapsule` 并检查 completed task 与 FactRef，只发送目标、来源边界和必要事实。已完成事实仍适用时直接引用，事实冲突、来源失效或 review 补证时允许独立交叉验证。
- 有子 Agent 时可把采集、推断或复审分配出去，子 Agent 只返回新增事实、来源锚点、缺口和角色结果；没有子 Agent 时由当前会话串行完成。不得重复传递完整问题历史、其他 Agent 原文或既有完整结果。
- 因果链存在前后依赖时必须按共享核心逐跳串行推进；不能因为 personal 没有子 Agent，就在定位到下游超时后提前结束。
- 不输出 `AGENT_RESULT`、`MANAGED_RESULT_META` 或 `BUSINESS_SUMMARY` 机器标记，直接按共享核心的公共结果语义回答用户。
- 只有用户明确要求保存最终报告并提供目标路径时才允许导出一份脱敏报告；不得生成中间文件。
- 默认只读，不修改数据库、配置、发布或线上状态；不读取 `obs-cli.json` 正文，不保存 token、完整日志、无界查询结果或不必要源码。
- 不得新增 Agent 数量、并发、回合或工具调用限制；必要工作、现有重试和业务 Skill 证据门槛保持不变。

增强能力只使用宿主在调用前显式声明的 capability，不为探测能力额外启动 Agent、调用工具或安装组件：

- `sessionMemory=true`：可以在当前宿主进程内用结构化内存承载同一索引；退出即释放，不得落盘或跨会话恢复。
- `toolInterception=true`：可以在当前会话对可证明等价的只读请求做透明复用；能力未声明时只做主控级事实复用，不得声称底层请求已被透明缓存。
- `usageTelemetry=true`：只可使用宿主提供的当前会话真实 telemetry 做本地比较，不估算美元，也不默认上传。能力未声明时明确精确用量不可得。

无论 capability 是否可用，子 Agent 都不接收费用、预算、剩余额度、命中率、收益目标或基于成本决定是否继续的指令。personal 不创建 sidecar，不上传原始日志、SQL、源码、完整对话或 telemetry。

门禁通过后的失败仍按共享核心列出问题摘要、排查思路、事实、失败点、限制和恢复动作，不得退化为单行工具报错。

## 4. 可选上报到排查平台

本节只在原有最终答复之后执行，且不得改变已经给出的个人排查结论。只有必需工具硬门禁全部通过，并且本次最终状态为 `concluded`、`platform_limit`、`input_insufficient` 或 `skill_gap` 时，才可以询问用户是否需要把脱敏结论上报到平台。若流程以 `PERSONAL_TOOL_PREFLIGHT_FAILED` 结束，不得展示排查记录上报选项、不得生成 `submissionId`、不得调用 `submit_troubleshooting_record`。

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
