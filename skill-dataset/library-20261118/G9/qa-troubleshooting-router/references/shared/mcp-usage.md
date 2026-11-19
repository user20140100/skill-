# aiTroubleShot MCP 统一调用约束

本文件供 `QA` 与 `TROUBLESHOOTING` 共同使用，规定同一 `aiTroubleShot` MCP 的身份、请求上下文、参数和失败处理。个人 MCP 注册仍只按 `references/shared/mcp-setup.md` 的确认门禁执行；本文件不授予任何写权限。

## 1. 固定身份与请求上下文

- 两种模式使用同一个 server name：`aiTroubleShot`。不得因为模式不同注册第二份 server、切换 URL、切换用户身份或把 QA 与排障结果交叉复用。
- URL 直读快速路径只为获取用户指定 URL 的响应，不需要调用 `aiTroubleShot` 或建立项目知识上下文；只有进入 QA/TROUBLESHOOTING 项目知识流程时才适用本文件其余 MCP 约束。
- 个人模式使用当前宿主已经核验的 MCP；托管模式使用可信宿主注入的 MCP。个人认证凭证来自平台 API Key 并由宿主通过 `AI_TROUBLE_SHOT_MCP_TOKEN` 引用；Token、Authorization、actor、owner、callback 和用户身份由宿主建立，模型只能检查状态或使用工具，不能读取、拼接、覆盖或要求用户提供秘密值。
- 目录入口 `get_project_route_catalog` 接收可选字符串 `environment` 和 `view`；当前 schema 支持时显式使用 `view:"routing"`。环境已知时必须先按 `SKILL.md` 的“首次请求前识别并归一化环境”表生成标准值，不透传用户原话或 `LOCALIZED|CLOUD`；例如 `{"environment":"云端","view":"routing"}`，未知时使用 `{"view":"routing"}` 获取全部项目；旧服务未声明 `view` 时才省略该字段，由服务端建立或宿主绑定请求上下文；需要 `requestId` 的后续调用复用返回值和当前模式上下文，不自行生成或覆盖。新请求或环境变化时重新建立请求，不沿用旧分类或工具结果；项目选择可以来自当前目录，不受旧授权上下文限制。

## 2. 工具和参数

- `get_project_route_catalog` 是两种模式共用的只读项目路由工具，响应使用 `projects[]`，调用目录不改变支持模式。两种模式的项目知识读取统一执行 `references/shared/knowledge-loading.md`，使用当前身份下已核验的 `search_project_knowledge` 和 `load_scoped_markdown`；排障另按 Profile 使用观测、代码和记录工具。工具清单由当前模式门禁确认，不以另一模式可用的工具替代。
- 每次调用前核对当前服务端 schema 的 required、`additionalProperties`、版本和关键字段。参数只能来自用户本轮输入、当前路由/分类响应、当前目录选择器或当前工具真实返回；禁止占位值、猜测值、内部 capability、API Key、credentialId、kbId 或凭证字段。
- 首次目录和意图分类在同一请求中各执行一次；按需匹配线索、读取项目详情属于该目录的补充操作，可以在分类前完成，不受此一次限制。后续调用复用已验证结果。项目、分类、仓库、环境和资源只能按当前目录或用户明确选择更新，不通过隐式授权上下文校验阻断请求。

## 3. 结果与失败

- MCP 返回只能作为来源化证据使用：校验响应结构、项目归属、版本和时间，记录具体调用来源；不得把模糊记忆或“之前查过”当作当前结果，不得输出原始响应或无界知识正文。
- 工具失败时只依据已读取的契约修正一次明确的入参错误；不得枚举参数、项目、集群、地址或工具名试探，也不得因为一个工具失败就切换模式或旧编排。保留已经验证的其他来源，并按模式契约报告限制。
- 所有诊断和知识问答调用默认只读。写操作、配置修改、权限、账号、发布和排障记录提交必须由对应模式的独立确认门禁控制；本文件及任何只读工具都不能扩大授权。

## 4. 轻量目录与完整字段匹配

当当前 tools/list 的目录 schema 包含 `view` 时，路由请求显式传 `view: "routing"`；旧服务没有该字段时才保持原调用。轻量目录仅用于项目识别，省略字段不代表项目没有相应能力或资产。

- 首次目录建立 requestId。后续 `resolve_project_candidates` 和 `get_project_detail` 复用它及本轮归一化后的 environment，不重新获取目录或创建新请求。
- 用户提供输入后，可调用 `resolve_project_candidates({requestId, environment?, text})`，text 直接传用户原文（1～32768 字符），不拆 signals、不指定 type。服务端只匹配代码仓库、鲸云应用和项目入口等明确资源；普通业务描述、职责、别名及特征由模型语义识别。无命中继续语义路由，多命中保留歧义。
- 匹配服务检索完整当前公开目录字段，不访问 URL。URL 用于项目归属时走匹配工具；只有用户要求取得 URL 响应时才走 GET 快速路径。
- 按返回的候选、routePath、field、value 和 source 判断依据；多命中不能压成唯一项目，空结果不能解释为该业务能力不存在。环境用于消歧，不猜测 appId 全局唯一。
- 选择项目或需要核实某个合理候选时，调用 `get_project_detail({requestId, projectUid, environment?})`，取得 skillName、仓库、部署、Apollo、维护人和链接等原有完整字段。将详情作为当前目录的补充证据，随后再进入业务 Skill/知识或排障采证。
- 这两项工具是只读路由工具，可在加载项目知识前使用，也可用于责任路由；不授予业务知识或运行时访问权限。
- 旧服务未声明 view 时，首次目录请求保持 full 兼容调用。已取得轻量目录但详情或匹配工具缺失时，保留自然语言路由结果及工具限制，不通过重复目录调用创建另一个 requestId。不要因显示截断直接选择 GLOBAL_ONLY；宿主保存完整结果，只向模型投影必要字段。
