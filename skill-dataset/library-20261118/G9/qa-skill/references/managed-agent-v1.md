# Managed Agent v1

本文件只用于平台托管知识问答。managed 是 `qa-core.md` 的受控运行适配层，不重新定义意图、知识层级、RAG 或回答规则。

## 1. 托管硬门禁

开始问答前确认可信宿主已经提供：

- `execution_profile: managed-agent-v1`、固定 `requestId`、channel 和可见会话输入；
- 宿主从当前已验证 `qa-skill` 制品读取 `intent-routing.md`，并通过隔离意图模型基于当前路由目录产出可信 `IntentResult`，其中项目归属与 `questionType` 已同时完成校验；宿主不得维护第二套类别定义；
- 兼容版本的 `qa-skill`；
- `get_project_route_catalog`、`resolve_knowledge_scope`、`load_scoped_markdown`、`search_project_knowledge` 四个只读工具；
- `read_managed_skill_file` 受控 Skill 正文读取能力、模型、超时/终止和结果接收能力。

任一必需项缺失时返回平台能力失败，不进入 `qa-core.md`。managed 禁止安装、同步或发布 `qa-skill`/业务 Skill，禁止运行 CSkills mutation，禁止配置个人 MCP，禁止读取 `personal-local-v1.md`、`cskills-loading.md` 或 `mcp-setup.md`。

## 2. 执行共享核心

硬门禁通过后，完整读取并执行 `qa-core.md`。所有工具调用必须使用宿主固定 `requestId`；模型必须原样提交宿主提供的可信 `IntentResult`，不得重新分类或替换 `questionType`、actorRef、项目、Scope、Skill 路径或认证身份。

managed 禁止原生 Read、Skill、Glob、Grep，不接收任何文件路径。入口先调用 `read_managed_skill_file(fileId=qa:entry)`，随后只按入口导航读取 `qa:managed-profile`、`qa:core`；Scope 与操作意图校验完成后，只读取已验证 `questionType` 对应的一个 `qa:operation:*` fileId；结束前读取 `qa:result-contract`。宿主必须拒绝另外三个操作提示词，以及 `qa:personal-profile`、CSkills 和 MCP setup 等未选内容。

managed 使用平台预安装的 exact 业务 Skill，但模型不得直接访问共享 Skill 目录。`resolve_knowledge_scope` 成功后仍不读取业务 Skill；匹配的操作提示词加载成功时，宿主只返回 Scope 中各 exact Skill 的惰性 `entryFileId`。模型明确读取某个入口后，宿主才加载该项目 Skill，并在入口响应中返回不含路径的 reference `fileId`；reference 正文也只在实际请求时读取。模型只能通过 `read_managed_skill_file` 使用这些 ID；宿主在返回正文前校验白名单，并只在入口读取成功后登记可信 loaded Skill proof。

Scope 返回非空 `skillName` 但 `managedSkillIndex` 标记 `MISSING` 或没有对应项时，记录 `BUSINESS_SKILL_UNAVAILABLE`；不得猜测相似包、安装新包、扫描共享目录或切换到个人加载方式。

## 3. 结果与运行边界

准备结束时才完整读取 `managed-result-contract.md`，输出人类可读答案和唯一 `QA_RESULT` 控制块。控制块只承载公共结果语义；Scope、来源类型、revision 和引用最终由宿主结合实际工具/Read 证据 canonicalize。

- 不输出私有 thinking、工具参数、工具原始结果、绝对路径、认证信息或 capability。
- 不自行保存平台会话、SSE、数据库或运行状态；这些由宿主负责。
- 工具失败时保留已确认材料、失败点、限制和恢复动作，不得在同一 requestId 下要求宿主回退旧编排。
