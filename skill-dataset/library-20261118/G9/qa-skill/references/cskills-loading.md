# CSkills Business Skill Loading

本文件只用于 personal Profile，且只在请求 Scope 返回 non-empty exact `skillName`、本机需要解析或变更该 Skill 时读取。

## 精确解析

1. 业务 Skill 名称只能来自请求 Scope 的 `skillName`，必须满足 `^[a-z0-9]+(?:-[a-z0-9]+)*$`；不得从项目名、业务名、目录、basename 或相似搜索结果推导。
2. 执行 `cskills info <skillName>`，要求返回 Name 与 `<skillName>` 完全一致。
3. 以 CSkills metadata 的 `canonicalPath` 为事实源，按项目级 canonical 优先、全局 canonical 次之解析。
4. 校验 package name、目录 basename、`SKILL.md` frontmatter name、version 和可得 file hash 一致；官方文件末尾同步提示按 CSkills 规范归一化后再比较。

## 安装与同步授权

本地不存在时展示包名、作者、版本、用途、安装范围和选择原因，等待用户明确确认：

```text
cskills add <skillName> --local --agent claude-code,codex
cskills add <skillName> -g --agent claude-code,codex
```

项目 `.agents/skills` 是 Harness 符号链接或不可安全写入时，只能在说明原因并再次明确确认后选择全局安装。安装后重新读取 canonicalPath、metadata、frontmatter、version 和 hash；不得仅凭 Installed 文案继续。

本地版本落后时，展示版本与本地修改状态，只有用户明确确认后才能执行：

```text
cskills sync <skillName> --pull-only
```

同步后重复完整身份校验。用户拒绝、沉默、网络失败、存在未确认本地修改或身份不一致时停止加载；不得自动选择相似 Skill。

## 禁止行为

- 禁止 `--force`、静默覆盖、批量模糊安装或修改后复用旧确认。
- 知识问答期间禁止 `cskills publish`。
- 禁止读取 Claude/Codex 链接目录作为 package 事实源。
- 加载成功后只按业务 `SKILL.md` 当前导航读取必要 references，禁止目录遍历。
