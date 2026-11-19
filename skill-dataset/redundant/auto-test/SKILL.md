---
name: auto-test
description: >-
  端到端 UI 测试自动化 skill。需求文档 + 源码审计双驱动，建立”需求文档 doc → 测试计划 plan → 自然语言用例 nl →
  Playwright 脚本 spec → 执行结果 run”五层可追溯链路。AI
  主动审计源码，发现文档未覆盖的边界行为、隐式逻辑和防御缺失，与需求同等权重驱动用例生成。当用户提到自动化测试、生成测试用例、跑 e2e、UI
  回归、增量同步测试用例、写测试脚本、端到端测试、Playwright
  测试、回归测试、冒烟测试、测试计划、用例生成、跑测试、测试报告、需求转测试、页面测试、功能验证、test automation、regression
  test、smoke test、run tests、generate test cases、帮我测一下、这个功能需要加测试、从 PRD 生成测试时使用。
version: 1.0.6
author: huangyunzhen
tags:
  - 自动化测试
  - 端到端测试
  - UI测试
  - 回归测试
  - 需求转测试
  - 增量生成测试
  - Playwright
  - 测试用例生成
---

# auto-test

你是 auto-test skill 的流程调度者。`SKILL.md` 只回答两个问题：当前用户询问应该从哪个流程开始，以及整体链路不能违反哪些约束。具体执行细节必须读取 `references/flows/` 下的子流程文档后执行。

具体执行细节以本文件和 `references/flows/` 为准。

## 0. 事故级硬约束

auto-test 产物会影响需求理解、测试覆盖和发布质量。任何跳步、偷懒、伪造、缺数据继续生成，都可能造成测试资产错误、覆盖缺失、误报通过，属于事故级问题。

必须遵守：

- **步骤不能跳**：后一步必须依赖前一步产物。缺 doc 不能生成 plan；缺 plan 不能生成 nl；缺 nl 不能生成 spec；缺 spec 不能宣称已可运行。
- **覆盖必须证明**：每层产物必须先证明覆盖完整性，再允许进入下一层。doc 必须包含能力地图、页面载体地图、能力域覆盖确认表；plan 必须包含固定覆盖清单对照表、模块补充覆盖项和四视角检查标记。覆盖表存在”未覆盖”或”待确认”时，AI 必须自主补充或决策后清零，不允许带着缺口进入下一阶段。
- **AI 自主决策，宁多勿漏**：覆盖范围、是否纳入、是否适用等决策由 AI 自主完成，不阻塞等待用户确认。决策原则为”宁多勿漏”——有疑问时倾向纳入覆盖，标”不适用”必须有明确依据。
- **LLM 不能偷懒**：不能用”看起来应该是””常见项目一般是”替代真实项目事实。不能为了完成任务而编造路径、页面、字段、按钮、selector、需求规则或测试结论。
- **缺数据必须停**：关键输入缺失时，必须停止当前步骤，明确报告缺失项、影响范围和需要用户确认的问题。

## 1. 五层链路

主链路固定为：

```text
doc → plan → nl → spec → run
```

含义：

- `doc`：需求文档。可以来自已有需求文档映射，也可以由代码反推，但必须先沉淀成文档。
- `plan`：测试计划。由 doc 和代码审计双驱动生成——需求文档定义"应该测什么"，代码审计发现"还需要测什么"（文档未覆盖的边界、隐式行为、防御缺失、实现差异）。两者同等权重，缺一不可。
- `nl`：自然语言用例。根据 plan 生成；有代码时结合代码事实，无代码时只能基于 plan 推导并标记待实现。
- `spec`：Playwright 脚本。后续由 generator 子流程生成。
- `run`：执行结果。后续由 run 子流程生成。

## 2. 入口路由

**每次用户发出新的执行意图，无论是否在同一会话中、无论前一个子流程是否刚结束，都必须重新走一遍入口路由表，读取并执行对应子流程文档。禁止凭记忆或经验跳过子流程文档直接执行。**

"刚跑完 03 生成 spec，用户紧接着说'跑测试'" ≠ "你已经知道怎么跑测试"。你必须读 `04-spec-run.md` 后再执行。

识别用户当前询问后，只决定应该从哪个子流程开始：

| 用户意图 | 子流程 |
| --- | --- |
| 初始化 auto-test / 项目首次接入 | 读取并执行 `references/flows/01-init.md`；若初始化探索时发现已有 e2e specs，先读 `references/flows/00-bootstrap-from-existing-specs.md` 与用户对齐 |
| 从初始化走到生成 nl | 读取并执行 `references/flows/02-doc-plan-nl.md` |
| 从 nl 生成 Playwright spec | 读取并执行 `references/flows/03-nl-spec.md` |
| 跑回归 / 执行用例 / 修复失败 case / heal | 读取并执行 `references/flows/04-spec-run.md` |
| 增量同步 / 源码改了要更新用例 / sync | 读取并执行 `references/flows/05-sync.md` |
| 未提交代码要更新用例 / dirty sync | 读取并执行 `references/flows/05-dirty-sync.md` |
| 项目已有 specs 但缺 doc/plan/nl | 读取并执行 `references/flows/00-bootstrap-from-existing-specs.md` |
| 查看报告 / 覆盖率 / dashboard / 测试看板 | 读取并执行 `references/flows/06-report.md` |
| 讨论或校验五层链路规则 | 读取 `references/flows/00-chain.md` |

### 反例（禁止）

- ❌ 03 流程结束后用户说"跑测试"，直接 `npx playwright test` 然后报结果
  → 必须先读 `04-spec-run.md`，按步骤创建 runId 目录、执行、归一、分诊、出报告
- ❌ 用户说"生成用例"，凭记忆知道要走 doc→plan→nl，直接开始做
  → 必须先读 `02-doc-plan-nl.md`，按步骤执行
- ❌ 觉得"这个子流程我刚读过，不用再读了"
  → 每次新意图都必须重新读取，子流程文档可能被用户修改过

目前实现到 `init → doc → plan → nl → spec → run → sync → report`（含 heal 失败分诊、增量同步双路径、dirty sync 未提交代码同步与测试报告看板）。

## 2.1 入口自检（每次进 skill 必跑）

进任何子流程前必须先跑一次入口自检，包含三个阶段：脚本版本检查 → 已提交变更检测 → 未提交变更检测。

### 2.1.0 Playwright CLI 前置检查（最先执行）

后续流程（登录采集、页面探查、generator/healer 自愈、spec 执行）依赖 `@playwright/cli` 提供的 `playwright-cli` 命令。本步骤在所有其他自检之前执行，确保 CLI 可用。

**检测方式**：

```bash
command -v playwright-cli >/dev/null 2>&1 && playwright-cli --help >/dev/null
```

- **可用** → 静默继续，进入 2.1.1。
- **不可用** → 自动安装并继续：
  ```bash
  npm install -g @playwright/cli@latest
  playwright-cli install --skills agents
  playwright-cli --help >/dev/null
  ```

判定：

- 安装成功（exit code 0）→ 告知用户："已安装 `@playwright/cli@latest` 并写入 `.agents/skills/playwright-cli`"，继续后续自检。
- 安装失败 → **立即停止**，报告 npm 输出中的失败原因（常见原因：网络不通、权限不足、registry 配置异常），不执行后续自检或子流程。

> 将 CLI 检查放在最前面的原因：页面探查、登录态采集、generator 与 healer 都需要在当前会话中直接调用 `playwright-cli`。提前安装可以避免执行到中途才发现浏览器探查层不可用；CLI 安装后不需要重开聊天窗口。

### 2.1.1 脚本版本检查

对比 skill 源目录和项目本地脚本的 `SCRIPT_VERSION` 常量，确保项目里的脚本不是旧版本：

1. 扫描 `~/.claude/skills/auto-test/scripts/` 目录下所有 `.mjs` 文件（当前包含 `sync_common.mjs`、`sync_check.mjs`、`sync_collect.mjs`、`dirty_check.mjs`），逐个读取 `const SCRIPT_VERSION = "X.Y.Z"` 的值 → srcVer
2. 读项目本地 `.auto-test/scripts/` 同名文件的 `SCRIPT_VERSION` → localVer（文件不存在视为 `"0.0.0"`）
3. 版本比较使用 semver 逐段数值比较（按 `.` 拆分为 major/minor/patch，逐段比较数值大小），不使用字符串比较

若任一脚本 srcVer > localVer（或本地文件不存在）：

- 将 skill 源目录 `scripts/` 下所有 `.mjs` 文件拷贝到 `.auto-test/scripts/`（覆盖），然后 `chmod +x` 可执行脚本
- 告知用户："已自动更新 `.auto-test/scripts/` 中的同步脚本（vX → vY），请在合适时机 commit"
- 继续后续自检

若版本全部相同：静默继续。

### 2.1.2 已提交变更检测（sync_check）

判断是否有未同步的源码 commit：

```bash
node ~/.claude/skills/auto-test/scripts/sync_check.mjs --root <项目根>
```

> 项目根 = 用户当前工作目录或 `.auto-test/` 所在目录。`~` 必须展开为绝对路径。
> 若 `.auto-test/sync-state.json` 不存在（init 未完成）→ 自检会返回 `pending=0` 并带 `warning`，按正常路由进入对应子流程即可。

读取 stdout JSON，按 `warningCode` 与 `pending` 分诊：

| 自检结果 | 路由 |
| --- | --- |
| `warningCode = NOT_INITIALIZED` | **强制路由到 `01-init.md`**（项目未初始化，无视用户原意图） |
| `warningCode = STATE_CORRUPTED` | **强制路由到 `01-init.md` 步骤 6.4**（修复 sync-state.json） |
| `warningCode = STATE_AHEAD` | 报告用户：`lastSyncedCommit` 已不在当前分支（可能被 rebase 掉），让用户决定是手动改 sync-state 还是回退 |
| `warningCode = GIT_UNAVAILABLE` | 报告用户：当前不是 git 仓库或空仓库；如确实无 git 才用 auto-test，告知 sync 能力不可用，按用户意图路由 |
| `pending = 0` 且无 warning | 静默继续，进入 2.1.3 |
| `pending > 0` | 主动告诉用户并请求确认 |

`pending > 0` 时的提示模板：

```text
检测到 N 个 commit 待增量同步。
git-ai 状态：已安装 / 未安装（影响增量同步的语义分析精度）
现在跑 05-sync 流程？还是先处理你刚才的请求？（可选 yes / later）
```

- 用户选 `later` → 不阻塞，按原意图路由；下次进 skill 仍会再次提示
- 用户选 `yes` → 路由到 `references/flows/05-sync.md`

### 2.1.3 未提交变更检测（dirty_check）

当 pending = 0（无 commit 级待同步）**且**用户意图涉及"生成/更新测试资产"（如生成用例、跑测试、写 spec 等）时，额外检测工作区未提交变更：

```bash
node ~/.claude/skills/auto-test/scripts/dirty_check.mjs --root <项目根>
```

读取 stdout JSON：

| 结果 | 路由 |
| --- | --- |
| `hasDirtyChanges = false` | 静默继续，按用户当前意图路由 |
| `hasDirtyChanges = true` | 提示用户并请求确认 |

`hasDirtyChanges = true` 时的提示模板：

```text
检测到 N 个未提交的源码文件变更（staged: X / unstaged: Y / untracked: Z），
是否先增量同步到测试资产？(yes / later)
```

- 用户选 `later` → 不阻塞，按原意图路由
- 用户选 `yes` → 路由到 `references/flows/05-dirty-sync.md`

**入口自检不允许跳过**。无论用户当前请求是什么（包括"什么都不做只问问题"），自检都先跑。`warningCode = NOT_INITIALIZED / STATE_CORRUPTED` 时，路由表里的"用户意图"全部失效，必须先回 01-init。

## 3. 总体顺序

完整链路的总体顺序是：

```text
init → doc → plan → nl → spec → run
                            ↑
                     sync (任意阶段后由源码 commit 触发)
                     dirty-sync (未提交代码时可提前触发)
```

当前已落地：

```text
init → doc → plan → nl → spec → run → sync / dirty-sync
```

执行时必须从用户当前询问对应的子流程开始，而不是在 `SKILL.md` 中展开细节。

## 4. 子流程边界

`SKILL.md` 不规定子流程内部如何探索项目、是否启动 subagents、如何生成文件、如何校验字段。这些必须写在对应的 `references/flows/*.md` 中。

如果某个执行细节尚未写入子流程文档，不能在主流程中临时补写执行；应先补充对应子流程，再执行。
