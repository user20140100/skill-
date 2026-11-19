# Personal Classification MCP Setup

仅当 `personal-local-v1` 的环境预检确认当前宿主不能调用 `get_trouble_categories` 时读取本文件。`managed-agent-v1` 由后端通过既有 `--mcp-config` 提供 MCP，禁止读取或执行本流程。

## 固定配置

| 项目 | 值 |
|---|---|
| MCP server name | `aiTroubleShot` |
| 远程 URL | `https://ai-trouble-shot.test.seewo.com/api/mcp` |
| token 环境变量 | `AI_TROUBLE_SHOT_MCP_TOKEN` |
| Claude Code scope | `user` |

本流程只注册远程 MCP，不下载或启动本地 MCP Server。token 必须由用户在启动 Claude Code/Codex 的环境中提供；不得要求用户把 token 发到对话中，不得把 token 作为脚本参数、命令文本、文件内容或排障产物记录。

## 执行门禁

1. 确认环境变量已设置，但只记录“已设置/未设置”，不读取或展示其值。未设置、空值或包含换行时停止。
2. 告知用户将检测本机 Claude Code/Codex，并在 user 配置中新增名为 `aiTroubleShot` 的远程 MCP；同名冲突不会覆盖或删除。
3. 询问用户是否确认执行。只有得到当前操作的明确确认后，才能运行脚本。
4. 从当前实际读取的 canonical Skill 根目录解析 `scripts/setup-trouble-mcp.sh` 的绝对路径，不得从工作仓库或其他同名副本猜测路径。
5. 执行：`sh <canonical-skill-root>/scripts/setup-trouble-mcp.sh --yes --agent auto`。CSkills 制品不保证保留脚本可执行位，因此必须显式使用 `sh`，不得直接执行脚本；也不得使用 `sh -x`、`set -x` 或其他会展开环境变量的调试方式。

脚本的原生命令契约为：

- Claude Code：`claude mcp add-json --scope user aiTroubleShot <json>`，JSON 的 Authorization 值保存字面量 `Bearer ${AI_TROUBLE_SHOT_MCP_TOKEN}`。
- Codex：`codex mcp add aiTroubleShot --url https://ai-trouble-shot.test.seewo.com/api/mcp --bearer-token-env-var AI_TROUBLE_SHOT_MCP_TOKEN`。
- 核验：`claude mcp get aiTroubleShot` 与 `codex mcp get aiTroubleShot --json`。

## 结果处理

脚本逐宿主输出 `installed`、`already-configured`、`skipped`、`conflict` 或 `failed`：

- `already-configured`：URL、环境变量认证和 Claude user scope 均一致，保持原配置。
- `conflict`：同名配置的 URL、认证方式或 scope 不一致。停止该宿主，不自动覆盖、删除或重命名；展示差异类型并让用户自行决定。
- `failed`：保留其他宿主的独立结果，记录不含 token 的恢复建议。
- `MCP_SESSION_RESTART_REQUIRED`：至少一个宿主已有兼容配置。personal 模式本身无 run；只在对话中返回该状态并结束本次调用，不创建或更新排障文件。用户重启宿主并创建新会话后，重新执行 CSkills、分类 MCP 和 obs-cli 三项完整门禁。

退出码：`0` 表示至少完成宿主检查且无冲突/失败，`2` 表示确认参数或 token 状态非法，`3` 表示未找到选择的宿主，`4` 表示存在冲突，`5` 表示注册或核验失败。

## 手工卸载

只有用户明确要求卸载时才提供以下命令，本流程不自动执行：

```sh
claude mcp remove --scope user aiTroubleShot
codex mcp remove aiTroubleShot
```
