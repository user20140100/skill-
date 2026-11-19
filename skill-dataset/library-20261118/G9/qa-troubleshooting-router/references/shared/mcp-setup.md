# Personal Unified MCP Setup

本文件用于 `personal-local-v1` 的首次前置 Token 检查，以及门禁通过后的 MCP 注册。前置检查不依赖版本、模式或 MCP 是否已注册。managed 由可信宿主提供 MCP，不执行本流程。

两种模式的 MCP 身份、请求上下文、参数来源、结果复用和失败处理统一遵守 `references/shared/mcp-usage.md`；本文件只负责个人宿主的注册、冲突检查和重启门禁。

## 固定配置

| 项目 | 值 |
|---|---|
| MCP server name | `aiTroubleShot` |
| 远程 URL | `https://ai-trouble-shot.test.seewo.com/api/mcp` |
| 平台入口 | `https://ai-trouble-shot.test.seewo.com/web/` |
| 个人 API Key 环境变量 | `AI_TROUBLE_SHOT_MCP_TOKEN` |
| Claude Code scope | `user` |

本流程只注册一份可同时服务 QA 与 TROUBLESHOOTING 的远程 MCP，不下载或启动本地 Server。认证凭证是平台个人 API Key：请登录平台后进入“右上角用户名菜单 → API Key 管理”创建，再将明文只配置到启动 Claude Code/Codex 的环境变量 `AI_TROUBLE_SHOT_MCP_TOKEN`。Skill 模型只能检查“已设置/未设置”，不得读取、展示、写入文件、作为参数传递或要求用户在对话中发送值。入口的 `scripts/report-usage.py` 可在脚本内部从环境读取 Key，仅用于固定平台的使用统计认证头；脚本不输出值或保存文件，不替代本节状态检查或业务认证。服务端根据 API Key 建立用户 principal，模型参数不能指定或覆盖 `actorRef`、用户、角色、owner 或 callback 身份。

## 个人 Token 前置检查

每次个人请求先在启动宿主的进程环境中做只读状态检查，工具输出只能是 `MCP_TOKEN_CONFIGURED` 或 `MCP_API_KEY_REQUIRED`，不得输出值。禁止 `env`、`printenv`、`echo $AI_TROUBLE_SHOT_MCP_TOKEN`、读取配置文件查找明文或开启 shell trace。可用以下命令，单引号中的内容必须作为脚本执行，不能把 Token 展开到命令参数：

```sh
sh -c '
set +x
case "${AI_TROUBLE_SHOT_MCP_TOKEN-}" in
  ""|*[![:space:]]*) ;;
  *) printf "%s\n" MCP_API_KEY_REQUIRED; exit 2 ;;
esac
cr=$(printf "\r")
case "${AI_TROUBLE_SHOT_MCP_TOKEN-}" in
  ""|*"
"*|*"$cr"*) printf "%s\n" MCP_API_KEY_REQUIRED; exit 2 ;;
  *) printf "%s\n" MCP_TOKEN_CONFIGURED ;;
esac
'
```

未设置、空值、纯空白或含 CR/LF 时检查失败。宿主不能执行状态检查、检查报错或只知道 MCP 已注册时，也按未通过处理，不推测 Token 存在。若后续 MCP 返回未认证、凭证无效或过期，同样立即停止业务流程，使用下方最终答复并将首句说明为“个人 MCP Token 无效或已过期”。不得复用历史结论掩盖认证失败。

### 未通过时的固定最终答复

必须直接在用户能看到的**最终回复**中输出以下内容并结束本轮；不得附加任何业务答案、截图解读、根因推测、证据整理、复审结论、评分或上报邀请。不要只发中间进度，也不要等其他调查完成再提示：

> **请先申请并配置个人 MCP Token，当前问答/排障已停止。**
>
> `MCP_API_KEY_REQUIRED`：当前启动环境未配置有效的 `AI_TROUBLE_SHOT_MCP_TOKEN`，或无法确认其状态。
>
> 1. 登录[问题排查平台](https://ai-trouble-shot.test.seewo.com/web/)，点击右上角“用户名 → API Key 管理”，创建个人 API Key。
> 2. 将 Key 配置到启动 Claude Code/Codex 的环境变量 `AI_TROUBLE_SHOT_MCP_TOKEN`。不要把 Key 发到对话中。
> 3. 完全退出并重新启动 Claude Code/Codex，新建会话后重新发起原问题；若尚未注册 `aiTroubleShot` MCP，再按配置流程完成注册。
>
> 完成配置前，本 Skill 不继续回答或排查原问题。

脚本不会代替用户登录平台、自动读取浏览器会话、自动复制 API Key 或替用户设置环境变量。用户需要注册 MCP 时，按下方确认、冲突和重启门禁执行，不因缺少 Token 自动运行安装脚本。

## 模式工具门禁

配置存在不代表当前模式可用。新会话必须按所选模式独立核对工具名、contract/toolset version、schema fingerprint、required 字段和 `additionalProperties`：

- `QA`：必须包含 `get_project_route_catalog`、`load_scoped_markdown`、`search_project_knowledge`，并满足 `knowledge-qa/v1` 与 `knowledge-qa-tools/v1`。
- `TROUBLESHOOTING`：必须至少能调用 `get_project_route_catalog`；其他分类、源码读取或排查记录工具仍按排障 Profile 当前步骤与服务端 schema 检查。

任一模式工具集不兼容时只让当前模式 fail closed；不得因为另一模式工具可用而继续，也不得切换模式规避失败。

## 执行门禁

1. 确认 `AI_TROUBLE_SHOT_MCP_TOKEN` 已设置，但只记录状态；未设置、空值或包含换行时输出 `MCP_API_KEY_REQUIRED` 和上述平台申请路径后停止。
2. 告知用户将检测本机 Claude Code/Codex，并在 user 配置中新增名为 `aiTroubleShot` 的远程 MCP；同名冲突不会覆盖、删除或重命名。
3. 展示固定 server name、URL、认证环境变量、目标宿主和配置影响，等待用户对本次持久化配置明确确认。
4. 从当前实际读取的 canonical `qa-troubleshooting-router` 根目录解析 `scripts/setup-mcp.sh`，不得从工作仓库、旧 Skill 或其他同名副本猜测路径。
5. 确认后执行 `sh <canonical-skill-root>/scripts/setup-mcp.sh --yes --agent auto`。CSkills 制品不保证保留脚本可执行位，必须显式使用 `sh`；禁止 `sh -x`、`set -x` 或其他会展开环境变量的调试方式。

脚本的原生命令契约为：

- Claude Code：`claude mcp add-json --scope user aiTroubleShot <json>`，Authorization 保存字面量 `Bearer ${AI_TROUBLE_SHOT_MCP_TOKEN}`。
- Codex：`codex mcp add aiTroubleShot --url https://ai-trouble-shot.test.seewo.com/api/mcp --bearer-token-env-var AI_TROUBLE_SHOT_MCP_TOKEN`。
- 核验：`claude mcp get aiTroubleShot` 与 `codex mcp get aiTroubleShot --json`。

## 结果处理

脚本逐宿主输出 `installed`、`already-configured`、`skipped`、`conflict` 或 `failed`：

- `already-configured`：URL、环境变量认证、enabled 状态和 Claude user scope 一致，保持原配置。
- `conflict`：同名配置的 URL、认证、enabled 或 scope 不一致。停止该宿主，不自动覆盖、删除或重命名，只展示差异类型。
- `failed`：保留其他宿主的独立结果，返回不含 API Key 的恢复建议。
- `MCP_SESSION_RESTART_REQUIRED`：至少一个宿主已有兼容配置。只在对话中返回状态并结束；不创建平台 run、session 或排障文件。用户重启宿主并创建新会话后，重新执行统一 Skill 的版本和当前模式全部门禁。

退出码：`0` 表示至少完成宿主检查且无冲突/失败，`2` 表示确认参数或 API Key 状态非法，`3` 表示未找到选择的宿主，`4` 表示存在冲突，`5` 表示注册或核验失败。

## 卸载边界

本流程永不自动卸载。只有用户明确要求卸载时，才可提供对应宿主的原生命令；卸载属于新的持久化操作，不能复用安装确认。
