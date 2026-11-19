---
name: smart-git-commit
description: >-
  感知工作区 git 改动，按可配置模板（默认 JIRA BUG 风格）自动生成 commit message，经用户确认后执行 commit（默认不
  push）。默认从分支名解析出 BIOS 版本标识（客户+板型+版本）作为描述前缀；解析不确定会询问用户而不是猜。触发词：写 commit、生成
  commit、提交代码、按模板提交、commit 一下、生成提交信息。
compatibility: Requires git. Python 3.8+ is optional (only for scripts/parse_version_tag.py).
metadata:
  icon: ':lucide:git-commit-horizontal:'
  title: 智能 Commit 助手
version: V0.02
agent_created: true
author: panyuhang
---

# 智能 Commit 助手（模板可换）

自动感知工作区改动 → 按模板生成 commit message → **用户确认后**才 commit。

## 使用时机

用户表达"提交一下" / "帮我写 commit" / "生成 commit message" / "按模板提交" 等意图时使用。

## 铁律

1. **先感知再动笔**：禁止不看 diff 就编 commit message。
2. **必须确认**：完整展示生成结果，得到用户明确确认后才执行 commit。**严禁未经确认直接 commit。**
3. **默认不 push**：只 commit。用户明确要求才 push。
4. **禁止编造 JIRA 号**：提取不到就留空并询问用户，绝不猜一个编号。
5. **禁止编造 BIOS 版本标识**：客户 / 板型 / 版本三者只要有一个判定不确定，**必须停下来问用户**，绝不许拿"看起来像"的分支段凑数。宁可多问一句，不可写错一行。
6. **禁用 `git add -A`**：只 add 本次 commit 相关的文件。

## 工作流

### Step 1 · 感知改动

```bash
git status --short
git diff --stat
git diff --stat --cached
git branch --show-current
```

- 需要看细节时再 `git diff` / `git diff --cached`。
- **大改动（>500 行或 >20 文件）优先看 `--stat` + 关键片段**，避免上下文爆炸。
- 若改动混杂多组逻辑无关的内容，**主动提示用户拆分多个 commit**（这是市面 AI commit 工具的普遍弱点，此处必须规避）。

### Step 2 · 解析 BIOS 版本标识（jira-bug 模板必做）

**首选：跑脚本，不要手工推。** 判据表（客户白名单 / 关键词）在 `customers.md`，两个正则在脚本里。

```bash
# <skill-dir> = 本 skill 所在目录；解释器任选，脚本只用标准库（Python 3.8+ 均可）
python "<skill-dir>/scripts/parse_version_tag.py" "$(git branch --show-current)"
```

- `python` 不在 PATH 时：Windows 试 `py -3`，macOS/Linux 试 `python3`；仍不行则走下面的手工解析。
- 输出为 JSON，按退出码分流：
  - **退出码 0 / `confidence: high`** → 直接用 `tag` 字段，进 Step 3。
  - **退出码 1 / `confidence: low`** → **必须按 2.4 停下来问用户**，把 `reason` 和 `segments` 段分解一并告诉他。
- 脚本缺失或环境无 Python 时，才按 2.1–2.3 手工解析（规则与脚本完全一致，别自行发明）。

#### 2.1 规范化（手工解析时）

1. 去掉开头 `origin/`；
2. 去掉开头 `Branch_` / `branch_`；
3. 按 `/` 切段，丢空段。

#### 2.2 抽要素（手工解析时）

**① 版本 ver** —— 从末段往前找第一个匹配版本正则的段，**原样保留**（`V0.04` / `T0.00-XMC` / `V0.09a` / `v0.08`）。
找到后**把该段之后的所有段裁掉**（那些是个人/临时后缀，如 `TJY`、`PYH`、`migrate-test`），剩下的是主干。

**② 板型 board** —— 主干**第一段原样保留，整段不剥离前缀**（`CCB-H340-MA01` / `MB.IWCL.ID02`）。
若第一段不含数字（`main`、`PYH`、`jim` 这类）→ **判定失败**。

**③ 客户 customer** —— 在「基线段之后、版本段之前」的余段里按优先级找，命中即停：

| 优先级 | 规则 | 信度 |
|---|---|---|
| a | 存在 `Customer` / `Oem` / `Custom` / `定制` / `客户` 段 → 取**紧随其后**的一段 | 高 |
| b | 某段命中 `customers.md` 客户白名单 | 高 |
| c | 余段里出现 2–4 位全大写字母短码，但不在白名单里 | **低 → 必须问** |
| d | 余段只剩关键词表里的阶段/类型/占位符/人名 → **判定为无客户线** | **→ 必须问** |

**④ 定制词** —— 客户段存在 → 固定串 `主板Bios定制`；判定为无客户线时**不能写"定制"**。

#### 2.3 拼装

```
{客户}{板型}主板Bios定制{版本}
```

下表的信度结果已用 `scripts/parse_version_tag.py` 在 CCB / Insyde 两仓实测分支上回归验证：

| 分支 | 标识串 | 信度 |
|---|---|---|
| `CCB-H340-MA01/CRB_R02.03-Pre/Customer/诚迈/V0.04` | `诚迈CCB-H340-MA01主板Bios定制V0.04` | 高（规则 a）|
| `CCB-H340-MA01/CRB_R02.02/Haier/Release/V0.03` | `HaierCCB-H340-MA01主板Bios定制V0.03` | 高（规则 b）|
| `MB.IWCL.ID02/CRB_05.72.17.0009/Release/Lecoo/V0.09` | `LecooMB.IWCL.ID02主板Bios定制V0.09` | 高（规则 b）|
| `CCB-H340-MA01/CRB_R01.00/GX/ES/Debug/T0.01` | `GXCCB-H340-MA01主板Bios定制T0.01` | 高（规则 b）|
| `CCB-H340-MA01/CRB_R02.03-Pre/Release/V0.21` | —— | **低（规则 d）→ 问用户** |
| `MB.IWCL.ID02/.../Release/MAINBOARD/V0.09a` | —— | **低（规则 d）→ 问用户** |
| `MB.IWCL.ID02/CRB_05.72.17.0009/migrate/v0.08/PYH/migrate-test` | —— | **低（规则 d）→ 问用户** |
| `MB.IWCL.ID01/CRB_05.72.21.0010` | —— | **低（版本缺失）→ 问用户** |
| `CRB：05.71.44.0003` / `main` | —— | **低（板型缺失）→ 问用户** |

#### 2.4 低信度时的提问规范

用提问工具，**必须附段分解**，选项给：

1. **采用建议值**（把已解析到的部分拼出来给他看）
2. 用户在选项外直接手写完整标识串
3. 本次不带标识串（只写改动描述）

提问措辞带上原始分支名和逐段归属，例如：
> 分支 `CCB-H340-MA01/CRB_R02.03-Pre/Release/V0.21` 里没有客户段，版本 `V0.21`、板型 `CCB-H340-MA01` 都认到了。这句"定制"该写谁？

- 中文段乱码（`??` / `\344\270\255`）→ 视为解析失败，**禁止按乱码猜客户名**，直接问。
- 用户说"这次不加版本号" → 本 Step 整体跳过，进 Step 3。

### Step 3 · 提取其余上下文

- **JIRA/Issue 号**：从分支名提取（正则 `[A-Z][A-Z0-9]+-\d+`，如 `feature/PROJ-1234-xxx`，实测有效例 `Pre-Release/H16240014-532`）；分支名没有则看改动内容、文件路径有无线索；仍无 → 留空并**询问用户**。
  - **避坑**：`CCB-H340-MA01` 这类**板型号会被正则误抓**。只有明显是 issue 号的段才用，且已判定为板型/客户/版本的段一律排除，拿不准就问。
- **改动性质 → Label**：fix / feature / refactor / build / docs / test / migrate / chore，可多选。
- **变更文件 → File**：`git diff --name-only`（staged + unstaged 合并去重），路径**相对到顶层 Pkg**：
  - 从变更文件**向上层文件夹遍历**，取**第一个以 `Pkg` 结尾**的文件夹作为路径起点
  - 例：`.../PanYuhangPkg/DxeModule/Xxx/Xxx.c` → `PanYuhangPkg/DxeModule/Xxx/Xxx.c`
  - 文件不在任何 `Pkg` 目录下（如仓库根的 build.py）→ 退回 git 仓库相对路径
  - **≤8 个文件**：逐个列出；**>8 个文件**：概括目录 + 关键文件名

### Step 4 · 按模板渲染

读 `templates.md` 选模板。默认 `jira-bug`：

```
[JIRA BUG Num.]<BIOS版本标识> JIRA BUG描述
[Label]       :
[File]        :
```

- **`<BIOS版本标识>` 与 `JIRA BUG描述` 之间用单个空格分隔**。
- 版本标识前缀**只作用于 jira-bug 模板**；conventional / simple 模板保持原样。
- 标识串被跳过时该位置直接省略，**不留前导空格**。

**切换模板**：用户说"用 conventional 模板" / "用 simple 模板"，或直接编辑 `templates.md` 新增模板。

### Step 5 · 展示并等待确认

用代码块展示完整 message，并附上**推断依据**：

| 字段 | 值 | 依据 |
|---|---|---|
| JIRA 号 | PROJ-1234 | 分支名 feature/PROJ-1234-xxx |
| BIOS 版本标识 | 诚迈CCB-H340-MA01主板Bios定制V0.04 | 分支 `CCB-H340-MA01/CRB_R02.03-Pre/Customer/诚迈/V0.04`；板型=第一段、客户=`Customer` 后一段、版本=`V0.04`、命中规则 a |
| Label | fix, setup | 修改 Setup 显示逻辑、修正取值错误 |
| File | PanYuhangPkg/DxeModule/Xxx/Xxx.c | git diff --name-only（相对到顶层 Pkg） |

然后停下等回复：确认 / 修改意见 / 取消。

### Step 6 · 执行 commit

```bash
git add <本次相关文件>          # 逐个指定，禁止 -A
git commit -F <message 文件>    # 多行模板必须用 -F，不要用 -m
```

- **多行/中文 message 一律用 `git commit -F <file>`**，`-m` 在 Windows / Git Bash 下易被转义或截断。
- 临时文件写到 `<repo>/.git/COMMIT_MSG_TMP`，commit 后删除。
- commit 后展示 `git log -1 --stat` 供核对。

## 坑位清单

- **多行 `-m` 会翻车** → 用 `git commit -F`。
- **`git add -A` 会带入构建产物/临时文件** → 按文件 add。
- **分支名中文段乱码**（`诚迈` 显示成 `??` 或 `\344\270\255`）→ 当前终端不是 UTF-8。用 Git Bash 重取 `git branch --show-current`；仍乱码就**直接问用户客户名**，绝不按乱码猜。
- **先跑 `scripts/parse_version_tag.py` 再动脑**，别手工推九条规则 —— 手推容易在第 3、4 条（客户段）翻车。
- **改客户/关键词只改 `customers.md`**，别改脚本里的正则（正则对应实测命名形态，动之前先看 `customers.md` §四 的干扰项清单）。
- **板型取第一段整段**，别自作聪明剥掉 `CCB-` / `MB.` 之类前缀。
- **`T0.xx` 也是版本**，别只认 `V` 开头；反之 `Main-Test`、`TST26070901` 不是版本。
- **`MAINBOARD` 是占位符不是客户**；`Release/V0.21` 这种主线分支没有客户，不许硬写"定制"。
- **`H16240014-532` 是 JIRA 号不是版本**；`CCB-H340-MA01` 是板型不是 JIRA 号。
- **基线段有两种写法**：`CRB_R02.03-Pre`（下划线）和 `CRB：05.72.05.0006`（全角冒号），都要认。
- **分支名嵌套坑**：新分支名不能嵌在已存在分支路径下（`A/B` 已是分支就不能建 `A/B/C`），否则 `cannot lock ref`。
- **ticket / 版本标识判不出来就问**，别编。
- 大 diff 主动建议拆分，别把多件事塞进一个 commit。

## 参考：市面同类工具的能力边界

| 工具 | 模板自由度 | 备注 |
|---|---|---|
| aicommits | 仅 conventional | 大 diff 不拆 commit，body 常缺 |
| OpenCommit | conventional + emoji | 支持本地模型（Ollama），配置偏重 |
| czg / commitizen | Commitizen 固定结构 | 强制交互式问答 |
| commitgpt | 支持 custom prompt | 仍需 OpenAI key |
| Copilot / Cursor | 基础格式 | 不支持自定义结构化模板 |
| Claude Code `/commit` | conventional 风格 | 无模板定制 |

**空白点**：以上均不覆盖「按团队自有结构化模板（如 JIRA BUG 格式）填充 + 从分支名自动派生 BIOS 版本标识 + 不确定时反问 + 确认后自动 commit」，且都跑在 CLI/IDE 而非 WorkBuddy 内 → 本 skill 补这个位。
