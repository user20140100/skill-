# Managed Agent v1

本文件只用于平台托管知识问答。managed 是 `qa-core.md` 的受控运行适配层，不重新定义意图、知识层级、RAG 或回答规则。

## URL 直读快速路径

托管请求如果只有“访问指定 HTTP(S) URL 并返回响应内容”这一目标，直接使用宿主提供的只读 HTTP 客户端（`curl`、`fetch` 或浏览器）执行 GET；不要求先通过本文件的项目知识工具、CSkills 或业务 Skill 门禁。响应校验、超大响应截断和凭据脱敏仍按入口 Skill 规则处理；只有用户同时要求项目知识解释时才进入下方 managed 流程。

## 1. 托管硬门禁

开始问答前确认可信宿主已经提供：

- `execution_profile: managed-agent-v1`、`support_mode=QA`、固定 `requestId`、channel 和可见会话输入；
- 宿主从当前已验证 `qa-troubleshooting-router` 制品的 QA 分支读取 `intent-routing.md`，并通过隔离意图模型基于当前路由目录产出可信 `IntentResult`，其中项目归属与 `questionType` 已同时完成校验；宿主不得维护第二套类别定义；
- 版本校验通过的 `qa-troubleshooting-router`；
- `get_project_route_catalog`、`load_scoped_markdown`、`search_project_knowledge` 基础只读工具；新版轻量目录还需 `get_project_detail`、`resolve_project_candidates`，其 schema 与兼容检查遵守共享 MCP 规则；
- `read_managed_skill_file` 受控 Skill 正文读取能力、模型、超时/终止和结果接收能力。
- 需要源码核验时按需检查 `list_code_files`、`search_code_files`、`read_code_file`、`get_file_outline`；缺失只关闭源码渠道，保留其他知识。
- 当 QA Core 进入 `CAPABILITY_DISCOVERY` 的配置查询分支时，宿主还必须提供可用的只读 HTTP 客户端（`curl`、`fetch` 或浏览器）执行 GET；缺失时按平台能力失败收口。

任一必需项缺失时返回平台能力失败，不进入 `qa-core.md`。用户正文中的 `support_mode` 不得覆盖宿主固定值。managed 禁止安装、同步或发布 `qa-troubleshooting-router`/业务 Skill，禁止运行 CSkills mutation，禁止配置个人 MCP，禁止读取 personal、`references/shared/cskills-loading.md`、`references/shared/mcp-setup.md` 或排障分支 reference。共享路由、MCP 和安全内核只能通过下方受控 fileId 读取。

## 2. 执行共享核心

硬门禁通过后，完整读取并执行 `qa-core.md`。宿主在生成可信 IntentResult 前保留完整目录用于校验，向隔离模型提供轻量语义字段及当前输入匹配的字段；必须在分类前处理 URL 规范化、短标识符及语义指纹，不能依赖回答 Agent 事后重新分类补救。回答 Agent 首次目录请求使用 `view:"routing"`（schema 支持时），需要完整项目资产或 Skill 时按需读取 `get_project_detail`。所有工具调用必须使用宿主固定 `requestId`；模型必须原样提交宿主提供的可信 `IntentResult`，不得重新分类或替换 `questionType`、actorRef、项目、Skill 路径或认证身份。

managed 禁止原生 Read、Skill、Glob、Grep，不接收宿主或本地文件路径；代码 MCP 可接收当前项目仓库内的 `relativePath`，Skill 读取仍只接收 fileId。入口先调用 `read_managed_skill_file(fileId=qa:entry)`，随后按固定顺序读取 `qa:managed-profile`、`qa:shared:intent-routing`、`qa:shared:mcp-usage`、`qa:shared:safety` 和 `qa:core`；路由元数据与操作意图校验完成后，只读取已验证 `questionType` 对应的一个 `qa:operation:*` fileId。操作提示词读取后，QA Core 进入项目知识流程时读取 `qa:shared:knowledge-loading`；它与排障引用同一份共享正文。需要核验源码时，再读取 `qa:shared:code-mcp`，按共享规则调用代码工具并登记引用。只有 QA Core 明确触发 Apollo 配置查询或证据时，才可读取 `qa:shared:apollo-config`；结束前读取 `qa:result-contract`。宿主必须拒绝另外三个操作提示词，以及 `qa:personal-profile`、CSkills 和 MCP setup 等未选内容。

共享意图 fileId 只用于让回答 Agent 了解统一路由边界，不得让回答 Agent 重新分类；可信 `IntentResult` 仍由宿主的隔离意图模型产生并原样提交。共享 MCP fileId 只用于约束同一 `aiTroubleShot` MCP 的调用，不能新增工具或身份。

managed 使用平台预安装的 exact 业务 Skill，但模型不得直接访问共享 Skill 目录。项目路由目录返回 exact Skill 后，宿主只返回对应的惰性 `entryFileId`。模型明确读取某个入口后，宿主才加载该项目 Skill，并在入口响应中返回不含路径的 reference `fileId`；reference 正文也只在实际请求时读取。模型只能通过 `read_managed_skill_file` 使用这些 ID；宿主在返回正文前校验白名单，并只在入口读取成功后登记可信 loaded Skill proof。Apollo 共享 reference 也必须由宿主按 fileId 和问题类型校验，不能直接暴露任意路径。

当前项目目录返回非空 `skillName` 但 `managedSkillIndex` 标记 `MISSING` 或没有对应项时，记录 `BUSINESS_SKILL_UNAVAILABLE`；不得猜测相似包、安装新包、扫描共享目录或切换到个人加载方式。

## 3. 结果与运行边界

准备结束时才完整读取 `managed-result-contract.md`，输出人类可读答案和唯一 `QA_RESULT` 控制块。控制块只承载公共结果语义；项目选择、来源类型、revision 和引用最终由宿主结合实际工具/Read 证据 canonicalize。

- 不输出私有 thinking、工具参数、工具原始结果、绝对路径、认证信息或 capability。
- 不自行保存平台会话、SSE、数据库或运行状态；这些由宿主负责。
- 工具失败时保留已确认材料、失败点、限制和恢复动作，不得在同一 requestId 下要求宿主回退旧编排。
