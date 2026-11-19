# Personal QA MCP Setup

本文件只在 personal 硬门禁确认当前宿主缺少兼容 `aiTroubleShot` MCP 时读取。managed 禁止读取或执行。

## 固定配置

| 项目 | 值 |
|---|---|
| server name | `aiTroubleShot` |
| 远程 URL | `https://ai-trouble-shot.test.seewo.com/api/mcp` |
| Token 环境变量 | `AI_TROUBLE_SHOT_MCP_TOKEN` |
| Claude Code scope | `user` |

Token 必须是用户自己的 4A/UC 登录 Token，并由用户在启动 Claude Code/Codex 的环境中提供；共享服务 Token 不能访问 QA 工具。只能检查已设置/未设置，不得读取、显示、保存或要求用户在对话中发送值。服务端根据 Token 建立用户 principal，模型参数不能指定或覆盖 `actorRef`、用户、角色、owner 或 callback 身份。

## 执行门禁

1. 展示将检测的宿主、固定 server name、URL、认证环境变量和 user scope。
2. 明确说明同名不兼容配置不会覆盖或删除。
3. 等待用户对本次配置操作明确确认。
4. 确认后使用 canonical Skill 中的脚本：`sh <canonical-skill-root>/scripts/setup-qa-mcp.sh --yes --agent auto`。
5. 禁止 `sh -x`、`set -x` 或把 Token 作为命令参数。

脚本为 Claude Code 执行 `claude mcp add-json --scope user aiTroubleShot <json>`，为 Codex 执行 `codex mcp add aiTroubleShot --url https://ai-trouble-shot.test.seewo.com/api/mcp --bearer-token-env-var AI_TROUBLE_SHOT_MCP_TOKEN`。

至少一个宿主安装或已有兼容配置时返回 `MCP_SESSION_RESTART_REQUIRED`。用户重启宿主并开启新会话后重新执行 personal 全部门禁。冲突或失败时只显示差异类型和不含 Token 的恢复动作，不自动移除、覆盖或重命名配置。
