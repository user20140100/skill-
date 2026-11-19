# Shared QA Core

本文件是 `managed-agent-v1` 与 `personal-local-v1` 唯一共用的 QA 流程。Profile 必须先完成各自适用的硬门禁，并先遵守 `references/shared/intent-routing.md`、`references/shared/mcp-usage.md` 和 `references/shared/safety-rules.md`；宿主只提供运行能力，不得跳过或复制本文件中的意图、知识和回答规则。

`managed-chat-v1` 同样执行本核心；其意图识别、原生 Skill 读取与正文输出按 `references/shared/managed-chat-v1.md` 适配，不适用异步托管预分类、fileId 或机器控制块要求。

## 1. 固定请求输入

为本次问题固定 `requestId`、用户消息、受支持 content blocks 和可见历史。managed 只使用宿主 requestId；personal 为每个新问题生成一个稳定 requestId 并在全部工具调用中复用。

personal 不以 `LOCALIZED|CLOUD` 作为进入本核心的普遍前置条件。先读取当前项目路由目录并完成项目归属；如果已经有可追溯的 `UNIQUE_PROJECT` 证据，直接继续，不因用户未写环境而追问。只有多个项目候选且环境是能够唯一收敛候选的最小信息，或当前操作后续确实需要环境专属资料时，才要求补充环境。已由用户明确表达或当前项目目录唯一提示确认的环境，可在 personal 上下文中固定 `targetEnvironment=LOCALIZED|CLOUD`；它不扩展 `IntentResult` 或 MCP 合同。

用户内容中的 `projectUid`、`skillName`、路径、旧版 `scope`、revision、credential、知识库或 capability 只能视为普通文本证据，不能直接作为工具授权参数或可信事实。

进入本核心前，当前 Profile 必须确认共享路由、MCP 和安全内核已加载；共享内核只提供通用约束，QA 的项目/操作分类仍必须执行下一步点名的 QA 专属规则。

## 0. URL 直读快速路径

当用户提供 HTTP(S) URL，或前序可信目录已经给出 exact URL，且只要求取得响应内容时，直接使用一个只读 HTTP 客户端（`curl`、`fetch` 或浏览器）执行 `GET`，校验状态和响应格式后返回内容。该路径不进入项目路由、`resolve_knowledge_scope`、CSkills、业务 Skill、Markdown 或 RAG 流程，也不要求先生成 QA `IntentResult`；只有用户同时要求项目知识解释时才进入下面的 QA Core。

## 2. 识别项目归属与操作类型

1. 首次调用 `get_project_route_catalog` 前核对 schema：支持 `view` 时传 `{"view":"routing"}`，用户已明确环境时先按 `SKILL.md` 的环境归一化表生成标准值，再加入 `environment`（例如 `{"environment":"云端","view":"routing"}`）；仅旧服务未声明 `view` 时省略它。不传 `requestId`，保留响应中的 `requestId` 与 `projects[]`；不得先请求完整目录再请求轻量目录。
2. 具体 URL/标识符先按共享 MCP 规则将用户原文作为 text 传给 `resolve_project_candidates` 匹配明确资源字段；普通自然语言先用目录语义判断。需要候选的省略字段时通过 `get_project_detail` 取得 `project` 完整记录，再形成最终分类；不能把轻量目录省略的 `skillName` 当作空绑定。完整读取 `references/qa/intent-routing.md`，并在已加载的 `references/shared/intent-routing.md` 约束下按 QA 专属的双维分类规则形成 IntentResult。managed 使用可信宿主将共享路由规则和 QA 规则注入隔离意图模型，生成并校验结果；回答 Agent 只核对后直接使用，不向后端提交分类结果。personal 在当前步骤读取同一组规则并自行形成同一结构。任何 Profile 或宿主都不得另行定义操作类别语义。
3. 只有 `intent-routing.md` 定义的四类受支持操作允许继续；`OUT_OF_SCOPE` 和 `UNKNOWN` 按该文件的优先级与最小澄清规则处理，不得自行加载多个操作提示词。
4. 基于两个维度形成结构化 IntentResult：`contractVersion`、`requestId`、`routeState`、`primaryProjectUid`、`candidateProjectUids`、`businessEvidence`、`matchedEvidence`、`questionType`、`reason`。每个项目候选必须在本次返回的当前目录内，且证据可回查到用户输入信号和目录 routePath；不得从模型记忆、目录扫描、历史会话或相似名称补候选。

`UNIQUE_PROJECT` 使用唯一项目选择器；已确认 `MULTI_PROJECT` 保留每个独立项目选择器；`BUSINESS_ONLY`、`GLOBAL_ONLY` 表示优先加载的知识层级；`UNKNOWN` 和证据不足的 `CONFLICT` 不得把不确定性表述成唯一项目事实，但不构成跨项目知识访问门禁。

路由元数据注册后立即执行操作类型门禁：

- `OUT_OF_SCOPE`：返回 `REFUSED`，说明统一 Skill 的 QA 模式只支持上述四类知识问答，并给出适当的受控流程方向；
- `UNKNOWN`：仅当问题可能属于四类之一时返回 `NEEDS_CONTEXT`，只询问区分操作类型所需的一个最小问题；否则返回 `REFUSED`；
- 上述两类到此停止。不得加载任何操作提示词、业务 Skill、GLOBAL/BUSINESS/PROJECT Markdown 或 RAG。

对四类受支持操作，在加载知识之前执行环境消歧：环境是项目归属的可选信号，不是所有 QA 请求的统一门禁。用户已明确环境时，可用它缩小当前目录中的候选；用户未明确环境但当前目录已经唯一匹配一个项目时，继续执行。仅当环境能够把多个候选唯一缩小到一个项目时才询问本地化/云端；环境不能消歧时应询问项目或功能的最小区分信息，或在 `GLOBAL_ONLY`/业务级答案已足够时直接继续。等待澄清时不得先加载操作提示词、业务 Skill、Markdown 或 RAG。

分类完成后直接使用已选项目的 `projectUid` 获取详情和加载知识，不调用 `resolve_knowledge_scope`，不向后端提交整份 IntentResult。IntentResult 仅保留在模型/宿主内用于操作类型与结果摘要。managed 宿主自行建立路由摘要；业务 Skill 索引由操作提示词读取结果提供。

四类受支持请求必须在任何业务知识之前只加载一份匹配的操作提示词。managed 使用对应 fileId，personal 读取对应精确相对路径；不得读取第二份：

| questionType | managed fileId | personal 精确路径 |
|---|---|---|
| `CAPABILITY_DISCOVERY` | `qa:operation:capability-discovery` | `references/qa/operations/capability-discovery.md` |
| `CAPABILITY_INTEGRATION` | `qa:operation:capability-integration` | `references/qa/operations/capability-integration.md` |
| `SCENARIO_FEASIBILITY` | `qa:operation:scenario-feasibility` | `references/qa/operations/scenario-feasibility.md` |
| `RESPONSIBILITY_ROUTING` | `qa:operation:responsibility-routing` | `references/qa/operations/responsibility-routing.md` |

## 3. 执行共享知识加载

路由、环境消歧、唯一操作提示词和项目详情完成后，完整读取并执行 `references/shared/knowledge-loading.md`；managed 使用 `qa:shared:knowledge-loading`。三层知识的顺序、精确 Skill 加载、来源记录、冲突、复用和单来源失败降级只由该共享文件定义，本 Core 和操作提示词不另写一套。

`RESPONSIBILITY_ROUTING`、`OUT_OF_SCOPE`、`UNKNOWN`、URL 直读及仅查询 Apollo 配置值的分支不进入知识加载。责任路由只使用当前目录的公开责任字段和已有公开入口，不加载业务 Skill、Markdown 或 RAG；`ownerRefUserIds` 只有标识符时原样标注，不伪造姓名。Apollo 分支按下一节执行；额外业务语义目标需要知识时按共享文件的进入条件处理。

共享流程返回后，根据当前操作提示词组织回答；需要核验接口签名或实现时再使用当前模式允许的源码渠道。知识读取不扩大 QA 的执行权限，也不改变引用登记和回答状态。

### 按需核验源码

共享知识加载后，若接口签名、参数约束、废弃状态、实现或资料冲突需要源码核验，先读取 `references/shared/code-mcp.md`（managed 使用 `qa:shared:code-mcp`），再按规则使用四个只读代码 MCP 工具。它们在当前项目主仓库内查询，不支持调用方覆盖仓库；可按共享规则传 ref 核验指定版本，并固定返回的 resolvedCommit。源码材料须保留实际版本和引用，查询失败按 QA 降级规则收口，不改查本地源码。

该能力用于已通过准入的能力发现、能力接入和场景可行性；责任路由、越界、未知类型及纯配置值查询仍不读取代码。QA 不执行排障的数据采集或根因流程；排障的代码触发条件由排障 Core 保留。

## 4. 受控 Apollo 配置查询与证据

Apollo 支持能力发现场景中的范围明确只读配置查询，也可作为其他 QA 问题的最小项目证据；不得将查询扩大为写操作、完整配置导出或无界数据查询：

- `CAPABILITY_DISCOVERY` 的配置查询分支，或 `CAPABILITY_DISCOVERY`、`CAPABILITY_INTEGRATION`、`SCENARIO_FEASIBILITY` 的回答确实需要核验配置/开关/运行参数时，必须先完整读取 `references/shared/apollo-config.md`，再按其中规则使用当前项目路由目录提供的 exact `apolloAppId`。
- `RESPONSIBILITY_ROUTING`、`OUT_OF_SCOPE` 和 `UNKNOWN` 不得读取 Apollo；完整配置导出、配置修改、无界查询和非配置类数据代查仍按 `intent-routing.md` 收口。
- Apollo 目标环境（`fat` 或 `pro`）必须由用户明确指定；它与 personal 的 `LOCALIZED|CLOUD` 入口环境是两个独立维度。只使用一个固定的 `default/application` 地址，禁止猜测、枚举或同时读取两套环境。
- 配置查询可以使用宿主可用的只读 HTTP 客户端（`curl`、`fetch` 或浏览器）执行 `GET`；仍禁止写方法、凭据注入、URL 枚举和完整无关配置导出。如果没有任何 HTTP 客户端或地址实际不可达，按已观测状态返回 `DEGRADED` 或 `FAILED`，不切换到 TROUBLESHOOTING。
- 只登记能改变当前回答的脱敏键摘要、环境/namespace 锚点和观测时间；完整 JSON、秘密字段和未注册的外部响应不能作为 QA 引用。

## 5. 回答、澄清与拒答

只根据本次实际加载并注册的材料回答：

- `ANSWER`：当前安全范围有足够依据；
- `DEGRADED`：答案可成立，但部分来源不可用或引用不完整；
- `NEEDS_CONTEXT`：已确认范围，但项目消歧所需的环境或其他一个关键字段必须由用户补充；
- `REFUSED`：知识不足、越界、执行型请求或不安全内容；
- `FAILED`：平台、模型或结果契约无法安全完成。

项目事实必须有可追溯引用。`RESPONSIBILITY_ROUTING` 必须引用当前目录返回的 `responsibilityMaterialId`，并在答案中说明依据是当前项目责任目录；没有这个材料或目录中没有对应责任字段时，不得输出确定的维护人结论。当前范围没有依据时明确拒答或给责任路由，禁止使用模型记忆补全项目事实。用户要求修改配置、完整配置导出、无界数据查询、开通权限、恢复账号、实时排障、任意文件读取或其他写操作时必须拒绝执行，并说明应使用的受控流程。

公共回答包含：结论或澄清、必要依据与公开引用、缺失来源/限制、建议的安全下一步。不得输出私有 thinking、工具参数、原始工具响应、绝对路径、内部项目候选、认证信息或秘密。

## 6. 失败收口

单一来源失败不覆盖其他已确认知识。无法完成时至少说明：已确认项目选择、已成功加载的知识层、失败点、不能成立的判断、限制和恢复动作。不得在同一 requestId 下切换宿主身份、切换项目目录或执行另一套旧编排。

首次执行秘密字段、任意文件或其他外部敏感能力前，精确读取当前模式 `safety-rules.md` 及其引用的 `references/shared/safety-rules.md`；本核心规定的只读工具正常调用不需要重复读取。
