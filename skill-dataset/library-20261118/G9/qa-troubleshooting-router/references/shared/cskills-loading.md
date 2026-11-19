# CSkills 业务 Skill 加载（共享）

本文件供 `personal-local-v1` 的 `QA` 与 `TROUBLESHOOTING` 共同使用。`managed-agent-v1` 不执行 CSkills 命令，所需 Skill 由可信宿主提供。

## 1. 统一入口 Skill 版本门禁

个人 QA 模式在调用远程 MCP、业务 Skill 或其他知识前，从当前实际使用的 `SKILL.md` frontmatter 读取 `version`，再执行：

```text
cskills info qa-troubleshooting-router
```

只比较本地 `version` 与返回的远端 `Version`：两者版本号相同即通过。不校验名称、目录 basename、canonicalPath、metadata、manifest、checksum 或 hash，也不因安装目录与用户指定目录不同而阻断。用户显式指定 Skill 路径时，直接以该路径的 `SKILL.md` 为本地版本来源。

版本不同时（包括本地版本高于远端），停止当前请求并展示两个版本。远端版本更高时，取得用户明确确认后可执行：

```text
cskills sync qa-troubleshooting-router --pull-only
```

本地版本更高时说明差异，请用户选择与远端同版本的本地 Skill，不自动降级或发布。同步后重新读取实际使用路径的 `version` 并查询远端版本，只有两者相同才重新执行当前模式门禁；同步更新了其他目录不能算当前路径校验通过。`cskills` 不可用、远端查询失败、版本缺失或无法解析时，说明实际限制并停止，不得声称版本一致。

### TROUBLESHOOTING 能力降级

以上严格远端版本一致门禁继续用于 QA。TROUBLESHOOTING 使用已加载的本地入口时，记录实际版本；远端版本查询按需进行，不作为调用 MCP 的前置步骤；远端查询失败或版本不一致只标注限制，不自动中断其他调查。所需业务 Skill 本地可读时同样记录实际版本与适用性；本地缺失则报告业务知识缺口，不猜测替代。安装与同步仍需明确授权。本例外同样适用于下文第 3、4 节的版本比较。

## 2. 业务 Skill 查询名称来源

业务 Skill 的查询与安装参数使用当前模式路由返回的 `skillName`：

- `QA`：使用当前 `get_project_route_catalog` 返回的已选项目 `skillName`；分类后直接按 projectUid 获取详情，不需要提交分类结果。
- `TROUBLESHOOTING`：使用当前 `get_project_route_catalog` 选中分类响应中的 `skillName`。

不对 `skillName`、返回的 `Name` 或本地 frontmatter `name` 做名称一致性校验。名称为空是合法的 `business_skill=not_required`，按当前模式核心继续通用流程；不得从项目名、分类名或相似搜索结果猜测替代 Skill。调用命令时将名称作为单个参数安全传递。

## 3. 本地路径解析与安装

1. 用户显式指定路径时优先使用该路径；否则按当前项目安装、全局安装的顺序定位。可用 CSkills metadata 的 `canonicalPath` 帮助定位，但它不是校验条件；可读取实际可访问的安装路径或链接路径。
2. 读取本地 `SKILL.md` 的 `version`，执行 `cskills info <skillName>`，按第 1 节只比较版本号。版本相同即可继续，记录本地路径和本地、远端版本，不计算或记录制品 hash。
3. 未安装时展示来源分类、查询名称、远端版本、用途和安装范围，取得用户明确确认后安装。项目安装目录不可安全写入时，说明原因并确认全局安装范围：

```text
cskills add <skillName> --local --agent claude-code,codex
cskills add <skillName> -g --agent claude-code,codex
```

4. 安装或同步完成后重新读取本地版本并查询远端版本，只有版本相同才继续；不得仅凭 Installed 文案判断成功。随后按实际读取的 `SKILL.md` 导航加载必要 references。

## 4. 版本冲突与禁止行为

- 业务 Skill 版本不同时按第 1 节处理；同步使用 `cskills sync <skillName> --pull-only`，须取得用户明确确认，不覆盖未经确认的本地修改。
- 禁止 `--force`、静默覆盖、批量模糊安装或从多个搜索结果静默选择。
- QA 与排障期间禁止 `cskills publish`。加载失败时保留当前模式已取得的事实和恢复指引，不切换个人/托管加载方式。
