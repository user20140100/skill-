---
name: git-add-commit
description: >-
  提交代码时使用。从 git 模板生成规范的 commit
  message，暂存文件，并推送到远程临时分支（不直接推到当前分支）。触发词：提交、commit、git commit、push 代码、保存代码。
author: shishaoxian
version: '1.3'
tags: 'git, commit, workflow, android, branching'
---

# git-add-commit

## Overview

根据修改内容生成符合项目提交模板的 commit message，并推送到远程临时分支（不直接推送到当前分支）。

## 执行步骤

### 1. 读取 Commit 模板

```bash
# 获取模板路径（通用，不写死路径）
git config --list | grep commit.template
# 输出示例：commit.template=/Users/xxx/.stCommitMsg

# 读取模板内容，了解字段结构
cat $(git config commit.template)
```

若没有配置模板，直接按以下通用格式生成 commit message：

```
[修改类型] 简要标题

[why] 原因
[how] 方案
[influence] 影响范围
[check] 测试范围
[jira] Jira号或N/A
```

### 2. 向用户确认 Jira 号

**提交前必须询问用户 Jira 号**，默认值为 `N/A`：

> 请提供 Jira 号（默认 N/A）：

### 3. 收集变更信息

```bash
git diff --stat          # 查看修改的文件统计
git diff                 # 查看详细改动内容
git status               # 查看未暂存文件
```

### 4. 生成 commit message

根据模板字段和 diff 内容填写，**修改类型**从以下选择：
- `config` — 客户配置、代码编译
- `bugfix` — 由缺陷主导的代码修改
- `feature` — 功能模块的添加

**示例：**
```
[bugfix] 修复亮度调节指令返回值格式错误

[why] KTC 反馈获取信号强度指令返回 ASCII 字符而非 HEX 格式
[how] 修改 KtcAlgorithm 中 parseSignalStrength 返回值格式化逻辑
[influence] KTC 厂商信号强度查询功能
[check] 通过 ADB 发送查询指令验证返回 HEX 格式 01
[jira] N/A
```

### 5. 确定远程临时分支名

格式：`temp{yyyyMMdd}_修改类型_修改点`

```bash
# 获取当前日期
date +%Y%m%d   # 例：20260430

# 分支名示例：
# temp20260430_bugfix_ktc信号强度返回格式
# temp20260430_feature_新增亮度调节功能
# temp20260430_config_更新hisense编译配置
```

**命名规则：**
- 修改类型：与 commit 类型一致（bugfix / feature / config）
- 修改点：**只能用英文或拼音**，不含空格，用驼峰或下划线分隔
- ❌ 禁止包含中文，如 `temp20260430_feature_验证提交流程`
- ✅ 正确示例：`temp20260430_feature_testCommitSkill`、`temp20260430_bugfix_ktcSignalFormat`

### 6. 暂存并提交

```bash
# 暂存所有相关文件（或指定文件）
git add <files>

# 直接指定 message 提交（不打开编辑器）
git commit -m "[bugfix] 修复KTC信号强度指令返回HEX格式错误

[why] ...
[how] ...
[influence] ...
[check] ...
[jira] N/A"
```

### 7. 推送到远程临时分支

```bash
# 格式：git push origin 当前分支:temp分支名
git push origin <当前分支>:<temp分支名>

# 示例（当前在 em-stable 分支）：
git push origin em-stable:temp20260430_bugfix_ktc信号强度返回格式
```

### 8. 更新 Jira（有 Jira 号时必做）

推送成功后，若 Jira 号不为 `N/A`，先验证 MCP 工具可用性：

```
检查 mcp__atlassian__jira_add_comment 是否可用
```

若工具不可用，提示用户：

> Jira MCP 未配置，无法自动更新备注。请检查 `~/.claude/mcp.json`（全局）或项目根目录 `.mcp.json`（本地）中是否有 `atlassian` MCP server：
>
> ```json
> {
>   "mcpServers": {
>     "atlassian": {
>       "command": "/opt/homebrew/bin/mcp-atlassian",
>       "args": [],
>       "env": {
>         "JIRA_URL": "https://your-jira-server.com",
>         "JIRA_PERSONAL_TOKEN": "your-personal-access-token",
>         "JIRA_SSL_VERIFY": "false",
>         "TOOLSETS": "all"
>       }
>     }
>   }
> }
> ```
>
> 安装命令：`pip3 install mcp-atlassian --break-system-packages`
>
> 配置后重启 Claude Code 即可生效。

MCP 可用时，按以下优先级确定备注模板：

```
全局 ~/.claude/CLAUDE.md 中的 jira_comment_template
        ↓（未配置）
skill 内置模板（按 commit 类型）
```

**模板选取流程：**

1. 读取 `~/.claude/CLAUDE.md`，查找 `jira_comment_template` 字段
2. **找到** → 直接使用，不打扰用户
3. **未找到** → 展示内置模板，询问用户：

   > 当前将使用以下模板填写 Jira 备注，满足需求请直接确认，如需自定义请提供新内容（将写入全局配置永久生效）：
   >
   > [展示对应内置模板内容]

   - 用户确认 → 使用内置模板，**不写任何文件**
   - 用户提供自定义 → 写入 `~/.claude/CLAUDE.md`，本次同时生效

**内置模板（fallback）：**

`feature` / `config`：
```
1、任务描述：{Jira标题 或 本次改动简述}
2、测试环境：{平台/设备型号}
3、测试方法：{验证步骤}
4、影响范围：{受影响的厂商/功能}
5、提交分支与时间：temp{日期}_{类型}_{描述}
6、自检结论：通过
```

`bugfix`：
```
1、原因分析：{根因}
2、解决方案：{改了什么}
3、影响范围：{受影响的厂商/功能}
4、提交分支与时间：temp{日期}_{类型}_{描述}
5、自检结论：通过
6、一轮设评后的项目贴验证软件：
```

调用 `mcp__atlassian__jira_add_comment` 填入确定的内容。

## 完整示例

```bash
# 1. 查看改动
git diff --stat

# 2. 暂存文件
git add app/src/bd_ktc/java/com/bd/test/feature/KtcSignalFeature.kt

# 3. 提交（直接指定 message）
git commit -m "[bugfix] 修复KTC信号强度指令返回HEX格式错误

[why] 获取信号强度指令返回值为ASCII字符30 31，而非HEX格式01
[how] 修改KtcAlgorithm.parseSignalStrength()的返回值格式化逻辑
[influence] KTC厂商信号强度查询功能
[check] ADB发送查询指令，验证返回HEX格式01
[jira] KTC-123"

# 4. 推送到临时分支（不推送到 em-stable）
git push origin em-stable:temp20260430_bugfix_ktcSignalFormat

# 5. 更新 Jira KTC-123（bugfix → 缺陷处理提交模板）
# 调用 mcp__atlassian__jira_add_comment，内容：
# 1、原因分析：获取信号强度返回 ASCII 字符而非 HEX 格式
# 2、解决方案：修改 KtcAlgorithm.parseSignalStrength() 格式化逻辑
# 3、影响范围：KTC 厂商信号强度查询功能
# 4、提交分支与时间：temp20260430_bugfix_ktcSignalFormat
# 5、自检结论：通过
# 6、一轮设评后的项目贴验证软件：
```

## 注意事项

- ❌ **不要** `git push origin em-stable`（直接推到当前分支）
- ✅ **必须** 推到 `temp{日期}_类型_描述` 格式的临时分支
- commit message 标题不超过 20 个汉字或 80 个字符
- 所有字段必须填写，无 Jira 则填 `N/A`
