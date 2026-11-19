# Personal Local v1

本文件只用于用户显式调用的个人 Claude Code/Codex。personal 是 `qa-core.md` 的本机适配层，不重新定义公共问答步骤。

## 前置 Token 门禁（优先于以下所有步骤）

先执行入口第 0 节及 `references/shared/mcp-setup.md` 的个人 Token 前置检查；未通过时只输出其中的固定最终答复并停止。本文件的 URL 快速路径、工具降级、保留已确认知识、受限收口和任务后反馈规则均不得覆盖该停止条件。

## URL 直读快速路径

如果用户给出了 HTTP(S) URL，或明确要求“访问这个 URL 并返回响应”，先按入口 Skill 的 URL 直读快速路径执行。该路径必须先通过个人 Token 门禁；随后不要求先判断 `LOCALIZED|CLOUD`，也不要求执行 CSkills、MCP 工具兼容性、项目路由或业务 Skill 门禁；直接使用 `curl`、`fetch` 或浏览器发送一次只读 `GET`，校验状态并返回响应内容，输出前脱敏明显凭据。

如果用户没有给出可用 URL，或还要求解释项目归属、能力或业务规则，再继续执行下面的 personal QA 流程。

## 0. 项目优先、按需确认目标环境

对每个未命中 URL 直读快速路径的个人知识问答请求，不得把 `LOCALIZED|CLOUD` 作为统一前置门禁。先按第 1、2 节完成本地版本和必需工具硬门禁；这些步骤不要求先得到部署环境，也不读取业务知识。门禁通过后读取并执行 `qa-core.md`，由其调用当前 `get_project_route_catalog` 完成项目归属。

项目路由和受支持的操作类型门禁完成后按以下顺序处理：

1. 已形成可回查的 `UNIQUE_PROJECT` 时，直接继续，不因用户没有写环境而追问。当前项目 `routeHints.environments` 只有一个可信值时，可在 personal 上下文中固定对应的 `targetEnvironment=LOCALIZED|CLOUD`；没有唯一环境提示也不阻断项目级问答。例如当前目录中开放平台只有云端项目时，直接按该项目继续。
2. 仍有多个项目候选时，先使用用户明确的“本地化”/“云端”表达缩小候选；只有候选环境提示明确不同且环境答案能唯一选出一个项目时，才询问：“请问这个问题属于本地化还是云端环境？”。
3. 环境不能把候选唯一收敛时，不要为了补齐环境字段反复追问；改问一个最小的项目/功能区分问题，或在 `GLOBAL_ONLY`/业务级答案已足够时继续。用户同时提到两种环境或表达冲突时，也只在该冲突会改变项目选择或当前答案时询问。
4. 如果后续操作确实需要环境专属资料，才在对应分支询问精确环境。Apollo 的 `fat|pro` 与 personal 的 `LOCALIZED|CLOUD` 是独立维度，必须按 Apollo 规则单独确认。

环境上下文只能来自按 `SKILL.md` 环境归一化表识别的用户明确部署环境表达，或当前项目目录可信的 `routeHints.environments`，不得从项目名称本身、仓库路径、当前代码、客户现场、线上/测试/生产、MCP 地址、历史问题或模型常识推断。环境是路由辅助信息，不是项目证据；不得向严格 `IntentResult` 私自新增 `environment`、`deploymentEnvironment` 或其他字段。用户改变环境或项目选择时，必须以新的 `requestId` 重新开始，不得沿用已加载知识。

## 1. 统一 CSkills 门禁

先完整读取 `references/shared/cskills-loading.md`，按其第 1 节读取当前实际使用的本地 `SKILL.md` 版本并执行 `cskills info qa-troubleshooting-router`。共享文件统一处理本地与远端版本号相等检查、用户确认、同步后版本复核和失败收口；不得在 QA Profile 中复制另一套版本或安装规则。未通过时停止，不得自动同步、安装、发布或使用 `--force`。该门禁不依赖 `LOCALIZED|CLOUD` 是否已确认。

## 2. 必需工具硬门禁

实际检查：

1. `cskills version` 可用；
2. `aiTroubleShot` MCP 工具列表精确包含 `get_project_route_catalog`、`load_scoped_markdown`、`search_project_knowledge`；当前项目目录必须返回 `contractVersion=knowledge-qa/v1`、`toolsetVersion=knowledge-qa-tools/v1` 和非空 `toolSchemaFingerprint`，否则在业务 Skill/知识加载前 fail closed。逐个核对 input schema 的 required、additionalProperties 和关键字段，不能只按同名工具判兼容。调用时遵守 `references/shared/mcp-usage.md`，同一请求只使用这一份 `aiTroubleShot` MCP，不切换身份、地址或旧结果；
   轻量路由能力单独核对：若目录 schema 声明 `view`，确认其支持 `routing`，并检查 `get_project_detail`（requestId、projectUid）与 `resolve_project_candidates`（requestId、text）的 schema。按共享 MCP 规则首次请求轻量目录、复用 requestId 进行匹配和详情读取；旧服务未声明 view 时保持原完整目录兼容调用，不凭工具同名假定新版能力。
3. 远程 MCP 使用平台个人 API Key，并通过环境变量 `AI_TROUBLE_SHOT_MCP_TOKEN` 提供；只检查“已设置/未设置”，禁止读取、打印或要求用户发送值。

Token 状态或认证失败优先按前置门禁的固定最终答复结束；其他检查失败时输出 `PERSONAL_QA_PREFLIGHT_FAILED` 并停止。Token 已通过但 MCP 缺失时可以精确读取 `references/shared/mcp-setup.md`，展示平台登录地址、用户名菜单 → API Key 管理、将修改的宿主、server name、URL 和认证环境变量；只有用户明确确认后才能使用 `sh <canonical-skill-root>/scripts/setup-mcp.sh --yes --agent auto`。成功配置后返回 `MCP_SESSION_RESTART_REQUIRED`，新会话重新执行全部门禁。

## 3. 准备 personal 上下文

版本和工具门禁通过后，完整读取并执行 `qa-core.md`；项目选择和环境确认按第 0 节的条件执行。仅在共享知识流程到达第三层、当前项目完整记录返回 exact `skillName` 且本机缺少兼容业务 Skill 时，才按 `references/shared/cskills-loading.md` 第 2-4 节解析/安装；安装或同步必须取得用户明确确认。QA Core 处理能力发现的配置查询分支或其他问题需要 Apollo 配置证据时，再按 `references/shared/apollo-config.md` 的触发条件读取，不把 personal 的 `LOCALIZED|CLOUD` 环境标签当成 Apollo `fat|pro` 环境。

源码核验按需检查当前 `aiTroubleShot` 的四个只读代码工具及其 schema，遵守 `references/shared/code-mcp.md`；个人使用不额外要求 requestId，参数以当前工具 schema 为准，不能改用 shared Token 绕过权限。缺失代码能力时保留已加载知识和缺口，不增加所有 QA 请求的源码工具硬门禁。

## 4. personal 输出边界

- 直接按 `qa-core.md` 的公共答案语义回复用户，不得输出 `QA_RESULT`、`QA_RESULT_START` 或平台机器控制块。
- 状态只保留在当前会话；默认不创建平台 session/run、不写中间文件、不上传完整对话或 telemetry。
- 只有用户明确要求保存最终报告并给出路径时，才可以导出一份不含 Token、工具原文和秘密的报告。
- 工具失败时保留已确认知识、失败点、限制和恢复动作；不得用模型记忆补全项目事实。

## 5. 任务完成后的可选反馈

最终答复完成后读取并执行 `references/shared/feedback-collection.md`。反馈只在用户明确评分后提交上次成功采集后到本次最终答复的新增 user/assistant 问答段；跳过或未评分不上传。该规则不创建平台 session，不改变 QA 答案语义。
