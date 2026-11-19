# Jira Log Analysis Assistant — 使用指南

## 1. 配置 MCP 服务

在 `~/.cursor/mcp.json` 中添加以下配置（将 `英文域账号` 替换为你的实际账号）：

```json
{
  "mcpServers": {
    "code-review": {
      "url": "https://dssdevops-be.gz.cvte.cn/mcp/mcp?user=英文域账号",
      "enabled": true
    },
    "jira": {
      "url": "https://dssdevops-be.gz.cvte.cn/mcp/jira/mcp?user=英文域账号",
      "enabled": true
    },
    "opengrok": {
      "url": "https://dssdevops-be.gz.cvte.cn/mcp/opengrok/mcp?user=英文域账号",
      "enabled": true
    }
  }
}
```

## 2. 申请 Jira 个人访问令牌

MCP 不支持直接下载 Jira 附件，Skill 需要通过 Jira REST API 下载日志文件和回写分析结果，因此必须提供 **Jira Personal Access Token**。

点击下方链接快速申请：

> <https://jira.cvte.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens>

## 3. 配置 Token

Skill 按以下顺序获取 Token：

1. **环境变量**（推荐）— 将 Token 设置到 `SKILL_JIRA_ASSISTANT_TOKEN` 环境变量中：

   ```bash
   export SKILL_JIRA_ASSISTANT_TOKEN="你的Token"
   ```

   可将此行写入 `~/.bashrc` 或 `~/.zshrc` 以持久化。

2. **对话中直接告知 AI** — 在使用 Skill 时直接把 Token 发给 AI 即可。
