# 03. 从 nl 生成 spec 子流程

## 目标

在 nl 已生成的前提下，按五层链路把自然语言用例落成可执行的 Playwright 脚本：

```text
nl → spec
```

本流程不负责执行用例（执行属于 run 子流程），但**必须对每条 spec 跑一次首跑 smoke**，确认脚本可被 Playwright 正确加载并在真实页面跑通；跑不通的 spec 不得宣称生成完成。

## 前置条件

进入本流程前必须满足：

- 入口自检（`SKILL.md §2.1`）若返回 `warningCode=NOT_INITIALIZED` 或 `STATE_CORRUPTED`，**禁止进入本流程**，必须先回 `01-init.md`。
- `01-init.md` 已完成：`.auto-test/config.json` 存在、`baseUrl` 可达、登录态已采集（`loginType=none` 除外）。
- `02-doc-plan-nl.md` 已为目标路由生成 doc/plan/nl，且校验全部通过。
- 目标 nl 文件 frontmatter `pendingCode: false`。`pendingCode: true` 的 nl **禁止**进入本流程，必须先回到 02 流程结合代码事实补完。
- `playwright.config.ts` 存在，`testDir` 指向 `.auto-test/case/specs`，`use.baseURL` 与 `.auto-test/config.json.baseUrl` 一致，`use.storageState` 指向 `.auto-test/.auth/storageState.json`（`loginType=none` 时不要求）。
- dev server 已启动，`baseUrl` 探活返回 OK（参考 `01-init.md` 步骤 4.0）。

任一项不满足，停止并回退到对应上游流程，不在本流程临时补救。

## 事故级硬约束（本流程专属）

- **禁止跳过 nl 直接写 spec**。spec 必须由具体某条 nl 文件驱动，禁止根据 plan 段落或 doc 直接生成 spec。
- **禁止编造 selector / 文案 / 状态**。任何 selector、可见文案、按钮 enable/disable 状态、提示语、跳转 URL，都必须由 generator 在真实页面探查得到，否则停止并报告。
- **禁止伪造通过**。spec 写完必须真实执行一次 smoke，未通过不得标注为完成；`expect` 不能被注释或替换为 `expect(true).toBe(true)`。
- **禁止跨路由合并 spec**。一个 spec 文件只对应一条 nl。
- **禁止删除/覆盖 nl/plan/doc 内容**。本流程只允许向上游 frontmatter **追加**字段（`specRef`、`linkedSpecs`），其余区块原样保留。
- **selector / mock 单一来源**。case spec 内**禁止**出现裸 selector 字符串或 `getByRole/getByText/getByPlaceholder` 等查询调用，所有 locator 必须从 `_selectors.ts` import；所有 `page.route` mock 必须从 `_mocks.ts` import。case generator 缺 selector / mock 时，必须**回写** `_selectors.ts` / `_mocks.ts` 并在返回的 `additions` 字段中声明新增项；不得 inline 绕过。违反此约束等于丢失"探查解耦"的全部收益，并破坏后续维护时的单点改动能力。
- **CJK 文案正则匹配**。`_selectors.ts` 中凡 `name` / `getByText` 值含连续 CJK 字符（≥2 字），必须用正则并在每两个字符间插入 `\s*`（如 `'确定'` → `/确\s*定/`）。原因：UI 组件渲染时可能在相邻汉字间注入空格，精确字符串匹配必然失败。

## Agent 启动协议

沿用 `02-doc-plan-nl.md` 的启动方式：generalPurpose subagent + 模板绝对路径，**不要**使用 `name` 字段或 `Use the <name> subagent` 句式。

| 场景 | 模板（绝对路径） | 作用 |
| --- | --- | --- |
| 真实页面探查并产出 Playwright 脚本 | `~/.claude/skills/auto-test/agents/generator.agent.md` | 按 nl 步骤逐步在真实页面操作，落地 spec 文件 |
| 首跑失败时定位与修复 | `~/.claude/skills/auto-test/agents/healer.agent.md` | 根据失败用例与运行日志，给出最小修复或回退方案 |
| 需要重新提取代码事实 | `~/.claude/skills/auto-test/agents/code-fact.agent.md` | 仅在 nl 与真实页面冲突、需要回退到代码确认时使用 |

实际调用把 `~` 展开为绝对路径。主进程必须只把 subagent 摘要作为决策输入，不得把 subagent 的中间猜测当作既成事实。

调用 `agents/code-fact.agent.md` 时，下发 prompt 必须显式包含「完整读完目标文件及其本仓库内部引用，禁止只读片段、禁止抽样、禁止 token 优化」约束，并要求在「引用文件」段标注 `[已完整读取 N 行]`。未标注或行数不符必须打回重读。

## 产物组织约定（强制）

spec 文件**必须**按 nl 同构方式组织，禁止扁平堆放：

```text
.auto-test/
  case/
    nl/
      <route-key>/
        <feature-slug>-<seq>.md
    specs/
      <route-key>/
        _seed.fixture.ts               # 该路由的 seed（登录态 + 路由就绪 fixture）
        _selectors.ts                  # 该路由的全部 locator factory（单一来源）
        _mocks.ts                      # 该路由的全部 page.route mock 工厂（单一来源）
        <feature-slug>-<seq>.spec.ts   # 与 nl 一一对应，仅做组装与断言
```

> 目录名是 `specs`（复数），与 `01-init.md` 步骤 3 中 `playwright.config.template.ts` 的 `testDir` 保持一致。
> seed 文件名固定为 `_seed.fixture.ts`，**禁止**用 `_seed.spec.ts`——会被 Playwright 默认 testMatch 收录，导致 case spec import 时触发 "test file should not import test file" 错误。
> `_selectors.ts` / `_mocks.ts` 与 seed 同目录，便于路由内 import；不放 `agents/` 或 `templates/`。

### 命名规则

- spec 文件名 = 对应 nl 文件名把 `.md` 换成 `.spec.ts`，**不允许重命名 / 拆分 / 合并**。
- 一条 nl 对应**唯一**一个 spec 文件、**唯一**一个 `test(...)` 用例；多步骤拆 step 用 `test.step()`，不要拆成多个 test。
- describe 名固定为 `<route-key> / <feature-slug>`（与 plan 内的功能分组对齐）。
- test 名必须等于 nl frontmatter 的 `title`（中文允许）。

### seed / selectors / mocks 文件

每个路由首次进入本流程时，generator 必须生成三件套：

- `_seed.fixture.ts`：复用 `playwright.config.ts` 的 `storageState`，提供 `test` fixture（导出扩展后的 `test` + `expect`），自动导航到该路由并等待路由就绪标志。**只放路由就绪判定，不放业务断言**。
- `_selectors.ts`：导出**带语义命名**的 locator factory（如 `q1YesButton(page)` / `submitButton(page)` / `errorBanner(page)`），内部使用 `getByRole / getByLabel / getByPlaceholder / getByText / getByAltText / getByTitle / getByTestId` 七选一。
- `_mocks.ts`：导出按用途命名的 `page.route` 装配函数（如 `mockAuthUserOk(page, opts)` / `mockHistoryEmpty(page)` / `mockSubmitFail(page)`）。

case spec 通过 `import { test, expect } from './_seed.fixture'`、`import { submitButton, ... } from './_selectors'`、`import { mockAuthUserOk, ... } from './_mocks'` 复用三件套。同一项目内必须统一一种 seed 形态（fixture 风格优先），首次定下后不再变形。

## 步骤 1：选择目标 nl

主进程接到生成 spec 的请求后：

1. 列出 `.auto-test/case/nl/` 下所有 `pendingCode: false` 且 `specRef` 为空的 nl，按 `<route-key>` 分组。
2. 与用户确认本次范围：单条 / 整路由 / 全部。范围必须明确，**不允许"看着办"**。
3. 制定执行计划（见步骤 1.1 调度模型），并按计划进入步骤 2。

必须严格按照要求启动对应的 subagent，不然会浪费更多的 token，结果也必然是错的，导致生产级别事故。

### 步骤 1.1：调度模型（Phase 化）

为提升速度同时不破坏正确性，采用如下调度：

**Phase A — seed/selectors/mocks 串行**
对本批涉及的每个 `<route-key>`，先以 `mode=seed` 串行调用一次 generator，产出 `_seed.fixture.ts` + `_selectors.ts` + `_mocks.ts`。**禁止**多个路由的 seed 并行，避免初始化三件套与 CLI session 探查证据交叉污染。

**Phase B — case 并行（跨路由）**
seed 全部完成后，**不同路由的 case generator 可并行**（同一 `Agent` 工具调用消息内多 tool 块）。
- 并行度上限：跨路由并发 ≤ Agent 工具一次最大并行度；超出按路由分批。
- 同一路由内的 case generator 仍**串行**：避免多个 generator 同时回写同一份 `_selectors.ts` / `_mocks.ts` 造成竞写。跨路由并行时必须使用不同短 session（`playwright-cli -s=at-<hash8>`）隔离浏览器状态。

**Phase C（可选，预留）— 同路由 isolated context 并行**
如要进一步压时间，可让 generator 为同一路由的不同 case 使用独立短 session（`playwright-cli -s=at-<hash8>`）并行探查，建议并发 N=2~3。前提：`_selectors.ts` / `_mocks.ts` 已稳定（Phase B 至少跑通一轮），不再有"回写"动作。当前流程默认**不开启** Phase C，需用户显式要求。

## 步骤 2：单条 nl 的 spec 生成

对每条选中的 nl：

1. **读取 nl 全文**（主进程，不丢给 subagent 转述）。提取：`caseId`、`title`、`docRef`、`planRef`、`pendingCode`、操作步骤、预期结果、覆盖点、待确认。
2. **冲突检查**：若 nl 含 `pendingCode: true` 或"待确认"区块非空，停止本条，把待确认项报告给用户，不进入 generator。
3. **决定输出路径**：`.auto-test/case/specs/<route-key>/<feature-slug>-<seq>.spec.ts`。如目标路径已存在 spec 且对应 nl 的 `specRef` 已指向该文件，需确认是覆盖（必须给出原因）还是跳过；不允许静默覆盖。
4. **首次进入路由**：若 `_seed.fixture.ts` / `_selectors.ts` / `_mocks.ts` 任一不存在，先按 Phase A 以 `mode=seed` 调用 generator 单跑一次（任务描述中标注"仅生成 seed/selectors/mocks 三件套，不写业务用例"）。
5. **启动 generator subagent**：按"Agent 启动协议"调用 `agents/generator.agent.md`，输入见模板"输入契约"。
6. **接收 generator 输出**：generator 必须返回结构化 JSON（见 generator 模板"输出契约"），缺字段视为失败。`status=ok` 必须 `dryRunStatus=passed` 且 `smokeStatus=passed`。
7. **结构化校验取代主进程二次 smoke**：主进程**不再**额外执行 `npx playwright test <specPath>`。改为：
   - 读取 `smokeReportPath` 指向的 Playwright JSON reporter 输出（generator 写入 `.auto-test/runs/last/<caseId>.smoke.json`）。
   - 校验 `stats.expected ≥ 1`、`stats.unexpected == 0`、`stats.flaky == 0`、对应 spec 文件的 test `status == "passed"`、`duration > 0`。
   - 任一不满足等同 smoke 失败，进入步骤 3。
   - 此校验仅做"信任契约"，不重复执行测试；批次最终的全量 smoke 在步骤 4 统一执行，覆盖"集成态"问题。
8. **回填上游**（强制，全部成功后再做）：
   - 编辑 nl 文件 frontmatter：`specRef: <相对项目根的 spec 路径>`。
   - 编辑 plan 文件：在该 nl 对应行追加 `spec` 列或在 frontmatter 的 `linkedSpecs` 数组追加 spec 路径。
   - 编辑 doc 文件：在 frontmatter `linkedSpecs` 数组追加 spec 路径，长度应 = 该路由非 pendingCode 的 nl 数量。
   - 三处任一回填失败，必须回滚 spec 文件（删除新建 spec 或恢复原 spec），保持链路一致。
9. **失败回路**：dry-run 或 smoke 不过时，进入步骤 3。

## 步骤 3：失败处理

失败处理顺序，**禁止跳序**：

1. **看真实失败原因**：
   - dry-run 失败（`dryRunStatus=failed`）：读取 generator 返回的 `dryRunLog`，定位 TS 编译错或 `playwright test --list` 报错；这类失败不应进入 healer，应由 generator 自行重写一轮（generator 内部回合上限 1）。
   - smoke 失败：读取 `.auto-test/runs/last/` 下的 trace/video/json，定位首个失败 step。
2. **判定归属**：
   - **selector / 等待时序 / 弱断言** → 启动 `agents/healer.agent.md`，仅修 spec / `_selectors.ts`，禁止改 nl。
   - **页面真实行为与 nl 描述不一致**（按钮文案变了、字段不存在、跳转目标变了等） → 停止 spec 修改，回到 02 流程修订 nl（可能需要重跑 `code-fact`），修订完成再回到本流程步骤 2。
   - **dev server / 登录态 / 配置问题** → 停止本流程，回 01-init 修复基础设施。
3. **修复后必须重跑 dry-run + smoke**，未重跑通过不得继续回填。
4. **重试上限**：单条 nl 的 healer 修复回合 ≤ 3。超过则停止并向用户报告，不得继续盲目重试。

## 步骤 4：完成校验

本批次所有 spec 处理完后，统一校验，任一项不过则整体回滚到处理前状态：

- 每个 spec 都能反向追溯到唯一 nl（spec 顶部注释含 `nl: <nl 路径>`、`plan: <plan 路径>`、`doc: <doc 路径>`、`caseId: <caseId>`）。
- 每条非 pendingCode 的 nl `specRef` 已回填且文件存在。
- 每个 plan 的 `linkedSpecs` 元素都存在；元素数 = 该 plan 下非 pendingCode 的 nl 数。
- 每个 doc 的 `linkedSpecs` 与 `linkedNl` 一一对应（按非 pendingCode 过滤后）。
- spec 目录下不存在不能反查 nl 的孤儿文件；不存在跨路由 spec。
- 每个 spec 至少有 1 个非平凡断言（`expect(...).toBeVisible() / toHaveText() / toHaveURL()` 等），无 `expect(true).toBe(true)` 这类占位断言。
- **静态校验整批**：执行 `npx tsc --noEmit -p .` 与 `npx playwright test --list`，无错误。
- **selector / mock 单一来源校验**：`grep` 检查 `<feature-slug>-<seq>.spec.ts` 文件中是否包含 `getByRole(` / `getByText(` / `getByPlaceholder(` / `getByLabel(` / `page.route(` 直接调用，命中即视为违反单一来源约束，必须回到对应 generator 重写。
- **全量批次 smoke**：`npx playwright test --reporter=list --workers=2`（dev server HMR 抖动风险高，先按 workers=2 起步；如机器规格允许且后续验证稳定，可在项目级配置上调到 3）。如需 JSON 报告，用 `PLAYWRIGHT_JSON_OUTPUT_FILE=<path>` 环境变量写文件，**禁止** `--reporter=json > file` 重定向（RTK 代理会截断大 JSON stdout 导致报告损坏）。`fullyParallel: false` 在 `playwright.config.ts` 中保持不变，使同一文件内 test 串行——目前每个 spec 一个 test，等价于文件级并行。一次通过；retries 命中也视为不稳定，必须报告。

## 步骤 5：交付报告

完成后给用户一个简短报告，至少包含：

- 本次生成的 spec 列表（路径、对应 caseId、smoke 状态）。
- 跳过 / 暂未生成的 nl 列表与原因（pendingCode、待确认、用户限定范围之外）。
- 已知不稳定 spec（首跑通过但 retry 中过的）。
- 调度阶段耗时（Phase A seed 串行 / Phase B case 并行的墙钟时间），便于评估并发收益。
- 下一步建议：进入 run 流程做完整回归 / 修订哪些 nl / 哪些 doc 待人工确认。

报告本身不写入 spec 文件，避免污染产物；可写入 `.auto-test/runs/last/spec-gen-report.md` 或 `.auto-test/.tmp/`。
