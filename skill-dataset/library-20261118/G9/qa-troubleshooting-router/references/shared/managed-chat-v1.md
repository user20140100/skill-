# Managed Chat v1

本 Profile 用于平台拉起 Claude CLI 的交互式聊天。宿主提供原始问题、会话恢复、预算、取消和只读工具；业务判断由 Agent 按本 Skill 执行。它与具有平台 run 和落库合同的 `managed-agent-v1` 独立。

## 运行适配

- 宿主不提供可信 IntentResult。由 Agent 结合完整用户目标自主选择 QA 或 TROUBLESHOOTING，自主识别环境、项目和操作类型，随新证据纠正判断；不要要求用户选择内部操作类型。
- 整理常见问题、故障处理知识或排查路径属于知识整理，进入 QA；定位某次真实异常才进入 TROUBLESHOOTING。没有具体项目时，可先询问要整理哪个项目。项目已明确时直接继续。
- 请求 Apollo appId 属于已知项目元数据查询。先按明确部署环境查询目录，再按项目精确名称/别名读取详情；详情已有 appId 时直接回答并注明来源，不必读取 Apollo 配置服务。测试/生产是 Apollo 维度，云端/边缘是项目维度。
- 项目名、精确别名、明确资源标识优先于描述中的泛词；“云端”“环境”“测试”等只用于环境判断，不能独立建立业务项目或多项目选择。
- 框架和项目 Skill 用原生 Read/Skill 读取，按入口精确导航；业务 Skill 根目录由可信宿主提供，exact skillName 取本次项目详情。不安装、同步或配置个人 MCP；缺失来源保留其他证据和缺口。
- MCP schema 和后端权限为准，使用同一 aiTroubleShot MCP。目录返回的 requestId 用于后续要求该字段的工具；不自行生成、替换，也不提交凭据。宿主通过透明代理处理认证，不要求额外的 scope、读取证明或操作类别。
- 只读 ccloud-cli、WebFetch、知识和代码 MCP 按实际证据目标使用；无访问能力时明确缺口。业务状态写入、部署、配置修改和平台记录提交不属于本聊天工具权限。
- ccloud-cli 使用宿主解析并提供的绝对路径，首次有证据目标时执行 `--help` 核验可执行性，再按共享 ccloud reference 的实际环境导航。数据库查询通过宿主的 `query_ccloud_resource` 只读工具执行，不经 Bash 传任意 raw-command；参数和 schema 为准。无需安装、登录或修改 CLI 配置。

## 共用业务流程

1. 读取 `references/shared/intent-routing.md`、`references/shared/mcp-usage.md` 和 `references/shared/safety-rules.md`，按当前目标选择唯一模式。
2. QA：读取 `references/qa/qa-core.md`；本 Profile 自主分类，读取选中操作的精确提示词。能力发现也包括有项目依据的知识解释、常见问题及排查路径整理、项目元数据查询。不要因明确查询 appId 而询问能力发现/接入/可行性/责任路由。
3. TROUBLESHOOTING：读取 `references/troubleshooting/troubleshooting-core.md`，执行其数据优先、真实证据、因果链和独立复审规则。有 Agent 能力时使用独立 review Agent；不可用时在当前会话切换对抗立场复审，明确限制。运行适配使用本 Profile 的原生只读工具，不要求平台 run、回调、工作区产物或排障机器控制块；本会话中维护必要任务、事实和复审结论。
4. 需要项目知识时按 `references/shared/knowledge-loading.md` 依次尝试来源。本 Profile 的 Skill 读取采用本节原生工具适配，不使用 fileId/managedSkillIndex，不预加载或枚举全部 reference。运行时渠道规则仍按各 Core 的精确导航读取。

## 输出

直接回复人类可读正文，说明事实来源、结论、限制和下一步。拒答、澄清和工具失败也直接回复；不输出 QA_RESULT、TROUBLESHOOTING_RESULT 或其他平台机器控制块。不触发个人评分上传或平台报告提交。

同一 Claude 会话允许复用仍适用的事实，当前环境、配置、部署及数据变化时重新核验。已完成某一步不等于证据闭环；不能为了返回答案跳过共用核心的证据要求。
