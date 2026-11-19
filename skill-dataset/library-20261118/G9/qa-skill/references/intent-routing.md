# 双维意图识别规则

本文件是 `qa-skill` 的唯一意图分类规则源。managed 的隔离意图适配器与 personal 的本地 Agent 必须执行同一份规则；任何宿主 Prompt 不得另行定义操作类别语义。

## 1. 两个独立维度

- **项目归属**：只在当前 `get_project_route_catalog` 返回的项目集合内形成 `routeState`、`primaryProjectUid`、`candidateProjectUids`、`businessEvidence` 和 `matchedEvidence`。项目证据必须同时回查到用户输入原文和当前目录 `routePath`。
- **操作类型**：描述用户本轮真正想完成的结果，不得用项目名称、领域关键词或候选项目代替。

### 1.1 目标环境识别前提

目标环境不是 `IntentResult` 字段，也不能由项目归属或操作类型反推。personal 只根据当前问题和紧接当前问题的澄清回复识别环境：

- 明确指向“本地化”时固定为 `LOCALIZED`；
- 明确指向“云端”时固定为 `CLOUD`；
- 没有环境表达、同时出现两种环境、比较两种环境或表达存在冲突时，环境视为未确定，必须先向用户询问“请问这个问题属于本地化还是云端环境？”。

不得根据项目名称、仓库路径、客户现场、私有化、线上/测试/生产、MCP 地址、历史问题或模型常识推断目标环境。环境确定后，仍须使用当前 `get_project_route_catalog` 返回的目录形成项目证据；不能以环境标签替代项目归属证据。

## 2. 操作类型闭集

| questionType | 用户真正要完成的结果 | 边界示例 |
|---|---|---|
| `CAPABILITY_DISCOVERY` | 判断某能力是否存在、由哪个技术平台或基础服务承载、能力目录在哪里 | “有没有按学校生成 room_id 的能力？” |
| `CAPABILITY_INTEGRATION` | 理解并接入一个已知能力，包括接口、参数、版本、流程或约束 | “滑动验证怎么接？”“这个方法哪个版本支持？” |
| `SCENARIO_FEASIBILITY` | 评估一个业务场景的方案、流程与基础服务能力是否可行 | “限定教室查课节应该怎么设计？” |
| `RESPONSIBILITY_ROUTING` | 找维护人、责任团队、联系人、已知项目的责任边界或资料入口 | “开放平台谁维护？”“管理后台链接在哪？” |
| `OUT_OF_SCOPE` | 问题排查、实时诊断、账号恢复、实时状态或数据代查、执行修复、配置修改、权限开通及其他非四类操作 | “接口为什么超时，帮我排查”“把误注销账号恢复” |
| `UNKNOWN` | 看似可能属于四类知识问答，但信息不足以唯一判断操作类型 | 只有项目名或含糊的“帮我看看” |

只有前四类属于 `qa-skill` 支持范围。

## 3. 分类优先级与重叠消解

1. 显式的问题排查、实时诊断、账号恢复、数据代查或执行型诉求优先归为 `OUT_OF_SCOPE`，即使输入包含可识别项目或顺带询问能力。
2. 问“能力是否存在、由哪个技术平台或基础服务承载、能力目录在哪里”归 `CAPABILITY_DISCOVERY`。
3. 问“谁维护、哪个团队负责、联系人是谁、已知项目的责任边界或资料入口在哪里”归 `RESPONSIBILITY_ROUTING`。
4. 不得因为出现“接入、对接、接口、调用、集成、怎么做”等通用动作词就自动归为 `CAPABILITY_INTEGRATION`；必须以用户最终交付结果为准。
5. 多个受支持目标同时出现时选择主要交付结果；无法唯一选择时归为 `UNKNOWN`，只提出一个能区分类别的最小澄清问题，不得加载多份操作提示词。

## 4. IntentResult 约束

输出只包含 `contractVersion`、`requestId`、`routeState`、`primaryProjectUid`、`candidateProjectUids`、`businessEvidence`、`matchedEvidence`、`questionType` 和 `reason`。不得加入业务 ID、Skill、知识库、凭证或任意资源选择字段。

项目候选必须来自本次实时目录。无法建立可追溯且能区分项目的证据时，使用符合现有路由契约的 `GLOBAL_ONLY`、`UNKNOWN` 或冲突状态，不得依赖模型记忆、目录扫描、历史会话或相似名称猜测唯一项目。
