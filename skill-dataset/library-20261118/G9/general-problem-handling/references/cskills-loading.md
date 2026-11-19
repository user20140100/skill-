# CSkills Business Skill Loading

本文件只用于 `personal-local-v1`。业务 Skill 名称只来自 `get_trouble_categories` 选中分类的 `skillName`；`general-problem-handling` 不维护业务名称映射，也不从任何目录或分类名推导名称。

## 精确解析流程

1. 调用 `get_trouble_categories`，不增加参数；响应中的 `skillName` 是 CSkills 包名，不是本地路径。
2. 根据问题环境、模块和现象匹配 `category`/`description`：
   - 唯一匹配：继续。
   - 多个匹配：展示分类名和描述，请用户选择。
   - 无匹配：记录 `skill_gap`；只有用户明确要求时才运行 `cskills find` 做人工发现。
3. 读取选中项的 `skillName`；字段为空时记录 `business_skill=not_required`，跳过本文件剩余的解析与安装步骤，返回共享核心正常执行通用排障。空值是预期配置，不记为 `skill_gap`，也不限制按分类代码来源调查源码；禁止的只是从分类名、`repositoryId` 或历史记录猜测替代 Skill。
4. `skillName` 是 `skills`/`domains`/`framework` 等通用名称，或不满足 `^[a-z0-9]+(?:-[a-z0-9]+)*$` 时停止自动安装并记录分类契约错误。
5. 执行 `cskills info <skillName>`。只有命令成功且返回 `Name` 与 `skillName` 完全一致时才继续；模糊匹配不算通过。

## 本地选择与安装

1. 按“当前项目 canonical → 全局 canonical → 未安装”检查；以 CSkills metadata 的 `canonicalPath` 为事实源，不以 `.claude/skills` 或 `.codex/skills` 链接为准。
2. 校验 package name、`SKILL.md` frontmatter `name`、canonical 目录 basename 三者完全一致。
3. 已安装时记录实际 name、version、author、canonicalPath 和可得 fileHashes；不要隐式同步。CSkills 安装时追加的 `CSkills local sync hint` 是本地提示，不属于发布包正文；比较 `SKILL.md` hash 时必须先移除“紧邻文件结尾的整个 hint 注释块及其前导换行”，不得因此把正常安装误判为本地修改。
4. 未安装时检查项目 `.agents/skills`：
   - 不存在或是可写普通目录：可以选择项目级安装。
   - 是指向 `.harness/skills` 等其他目录的符号链接：禁止项目级安装，避免 CSkills 生成自引用链接；改为全局安装。
5. 展示分类、name、author、version、description、实际安装范围及选择原因，等待用户明确确认。
6. 获得确认后只执行二者之一：

```text
# 普通项目目录
cskills add <skillName> --local --agent claude-code,codex

# .agents/skills 存在 Harness 符号链接冲突
cskills add <skillName> -g --agent claude-code,codex
```

7. 安装命令结束后必须重新读取 canonicalPath、metadata、`SKILL.md` frontmatter 和规范化 hash，并与本次 `cskills info` 返回的 name/version 及 metadata fileHashes 交叉校验；不得把覆盖提示或 Installed 文案当作升级成功。
8. 校验通过后，当前会话直接读取 canonical `SKILL.md` 和必要 references，不等待宿主 Skill 列表热刷新；校验失败时停止加载并保留当前 run。

## 版本和冲突

- 项目级与全局同名时使用项目级，并在结果中记录实际路径。
- 已安装版本低于 `cskills info` 返回版本时，不重复使用 `cskills add` 的覆盖路径。展示版本差异并取得用户明确确认后，使用 `cskills sync <skillName> --pull-only`；同步后重复 metadata、frontmatter 和 hash 校验。同步失败或仍为旧版时记录 `skill_gap`，不得静默使用旧业务知识。
- metadata/规范化 hash 表明本地被修改时，展示风险并让用户选择继续、显式同步或退出；禁止自动 `sync --force`。除结尾官方 hint 外的任何差异都视为本地修改。
- 领域 Skill 的 framework compatibility 不包含当前版本时，阻止高置信排障并给出显式升级指引。
- 跨业务域时重新调用分类 MCP，并对第二个 Skill 重复精确校验和用户确认；禁止一次模糊安装多个包。

## 禁止行为

- 排障期间禁止 `cskills publish`。
- 未经用户明确要求禁止 `cskills sync`、`--force` 或覆盖本地内容。
- 禁止扫描所有 MCP 猜工具名，禁止从多个 `cskills find` 结果静默选择。
- `cskills info/add` 失败时保留当前 run 文件，记录 `skill_gap` 或 `platform_limit` 和恢复指引。
