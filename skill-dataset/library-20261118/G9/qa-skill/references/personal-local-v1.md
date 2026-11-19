# Personal Local v1

本文件只用于用户显式调用的个人 Claude Code/Codex。personal 是 `qa-core.md` 的本机适配层，不重新定义公共问答步骤。

## 0. 目标环境条件确认

对每个新的个人知识问答请求，在版本检查、工具探测、业务 Skill 或任何知识读取之前，先根据当前问题和紧接当前问题的澄清回复识别目标部署环境。只接受以下两种明确且不冲突的目标表达：

- `LOCALIZED`：问题明确指向“本地化”，例如“本地化课表”或“在本地化环境接入”；
- `CLOUD`：问题明确指向“云端”，例如“云端课表”或“在云端环境接入”。

问题已经明确指向其中一个环境时，直接固定 `targetEnvironment=LOCALIZED|CLOUD`，不得重复追问。以下情况均视为无法唯一识别目标环境：没有出现目标环境、同时出现“本地化”和“云端”、只是在比较两者，或环境表达与问题目标冲突。不得根据项目名称、仓库路径、当前代码、客户现场、私有化、线上/测试/生产、MCP 地址、历史问题或模型常识推断目标环境。

环境无法唯一识别或信息冲突时，只询问：“请问这个问题属于本地化还是云端环境？”随后停止本轮。此时禁止执行 `cskills info`、MCP 工具探测、业务 Skill 加载、GLOBAL/BUSINESS/PROJECT Markdown 或 RAG 读取，也不得直接给出项目事实答案。

环境确认是条件门禁：环境已唯一识别时继续执行后续版本、工具和知识流程；用户改变环境时必须以新的 `requestId` 重新开始，不得沿用原 Scope 或已加载知识。

执行 `qa-core.md` 第 2 步时，将当前问题中的明确环境表达作为可见输入证据。只有当前项目目录存在可回查的环境提示时，才可在现有 `matchedEvidence` 中记录原始 `inputSignal` 和 `routePath=routeHints.environments`；不得向严格 `IntentResult` 私自新增 `environment`、`deploymentEnvironment` 或其他字段。环境证据无法映射到当前目录时返回 `NEEDS_CONTEXT`，不得跨环境猜测业务 Skill 或项目。

## 1. qa-skill 版本检查

在远程工具、业务 Skill 或知识读取前，先从当前 canonical `SKILL.md` frontmatter 动态读取 `name`、`version`，再执行 `cskills info qa-skill`。必须同时确认 CSkills metadata 的 package name、canonicalPath 和 checksum/hash 指向当前这份 `qa-skill`；不得只比较硬编码版本号或信任同版本副本。然后比较本地与远端语义版本：

- 远端不高于本地时继续；
- 远端更高时停止，展示差异并建议用户明确确认后执行 `cskills sync qa-skill --pull-only`，更新后重新加载 Skill；
- CSkills 不可用或版本无法校验时停止，不得声称已是最新版或绕过。

不得自动同步、安装、发布或使用 `--force`。

## 2. 必需工具硬门禁

实际检查：

1. `cskills version` 可用；
2. `aiTroubleShot` MCP 工具列表精确包含 `get_project_route_catalog`、`resolve_knowledge_scope`、`load_scoped_markdown`、`search_project_knowledge`；当前项目目录必须返回 `contractVersion=knowledge-qa/v1`、`toolsetVersion=knowledge-qa-tools/v1` 和非空 `toolSchemaFingerprint`，否则在业务 Skill/知识加载前 fail closed。逐个核对 input schema 的 required、additionalProperties 和关键字段，不能只按同名工具判兼容；
3. 远程 MCP 使用环境变量 `AI_TROUBLE_SHOT_MCP_TOKEN`，只检查“已设置/未设置”，禁止读取、打印或要求用户发送值。

任一失败时输出 `PERSONAL_QA_PREFLIGHT_FAILED` 并停止。MCP 缺失时可以精确读取 `mcp-setup.md`，展示将修改的宿主、server name、URL 和认证环境变量；只有用户明确确认后才能使用 `sh <canonical-skill-root>/scripts/setup-qa-mcp.sh --yes --agent auto`。成功配置后返回 `MCP_SESSION_RESTART_REQUIRED`，新会话重新执行全部门禁。

## 3. 准备 personal 上下文

目标环境、版本和工具门禁全部通过后，完整读取并执行 `qa-core.md`。Scope 返回 exact `skillName` 且本机缺少兼容业务 Skill 时，才完整读取 `cskills-loading.md`；安装或同步必须取得用户明确确认。

## 4. personal 输出边界

- 直接按 `qa-core.md` 的公共答案语义回复用户，不得输出 `QA_RESULT`、`QA_RESULT_START` 或平台机器控制块。
- 状态只保留在当前会话；默认不创建平台 session/run、不写中间文件、不上传完整对话或 telemetry。
- 只有用户明确要求保存最终报告并给出路径时，才可以导出一份不含 Token、工具原文和秘密的报告。
- 工具失败时保留已确认知识、失败点、限制和恢复动作；不得用模型记忆补全项目事实。
