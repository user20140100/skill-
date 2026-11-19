# 04. 从 spec 执行回归 子流程

## 目标

在 spec 已生成的前提下，按五层链路把可执行脚本跑成执行结果：

```text
spec → run
```

本流程负责"批量回归 + 失败分诊"。**不**负责单 spec 落盘后的首跑 smoke（那归 03 流程内部解决）。

## 前置条件

进入本流程前必须满足，任一不过停止并回退到对应上游：

- 入口自检（`SKILL.md §2.1`）若返回 `warningCode=NOT_INITIALIZED` 或 `STATE_CORRUPTED`，**禁止进入本流程**，必须先回 `01-init.md`。
- `01-init.md` 已完成：`.auto-test/config.json` 存在、`baseUrl` 可达、登录态已采集（`loginType=none` 除外）
- `playwright.config.ts` 存在，`testDir` 指向 `.auto-test/case/specs`，`use.baseURL` 与 `.auto-test/config.json.baseUrl` 一致，`use.storageState` 指向 `.auto-test/.auth/storageState.json`（`loginType=none` 不要求）
- 待跑的 spec 顶部注释含 `nl / plan / doc / caseId` 四元组（与 03 步骤 4 一致），缺一律拒跑
- dev server 已启动，`baseUrl` 探活返回 OK
- `playwright-cli --help` 可用（healer 阶段要用，跑前就检查避免跑完才发现浏览器探查层不可用）

## 事故级硬约束（本流程专属）

- **禁止跳过分诊伪造通过**。`failed[]` 不为空时不允许直接宣称完成；每个失败 case 必须落到 `fixed / fixmed / escalated` 之一
- **禁止主对话或 healer 修改 nl / doc / plan**。本流程只允许向 spec 顶部追加 `@healedAt` 注释、向 `runs/<runId>/` 追加文件
- **禁止 healer 并行**。同一时间只允许一个 healer subagent 处理一个 case，浏览器状态会污染
- **禁止绕过 `@playwright/cli` 协议使用其它浏览器自动化工具做 healer**

## Agent 启动协议

沿用 `02 / 03` 的启动方式：generalPurpose subagent + 模板绝对路径，不要使用 `name` 字段或 `Use the <name> subagent` 句式。

| 场景 | 模板（绝对路径） | 作用 |
| --- | --- | --- |
| 失败 case 自愈 / 分诊 | `~/.claude/skills/auto-test/agents/healer.agent.md` | 按五类根因分类，自己改 spec 或 escalated 回报 |

实际调用把 `~` 展开为绝对路径。

## 步骤 1：范围确认

主对话接到执行请求后：

1. 列出可跑 spec：`.auto-test/case/specs/**/*.spec.ts`，排除 `_seed.spec.ts`
2. 与用户确认本次范围，**禁止"看着办"**：
   - 单条 caseId
   - 单个 route（`.auto-test/case/specs/<route-key>/`）
   - 全量回归
3. 范围确认后把待跑 spec 清单回显给用户过目，再启动

## 步骤 2：前置门校验

逐项检查，任一不过停止并报告修复路径：

- 链路注释四元组完整
- `playwright.config.ts` 字段一致
- dev server 探活
- `playwright-cli --help` 可用

## 步骤 3：执行

```bash
RUN_ID="run-$(date +%s)"
RUN_DIR=".auto-test/runs/${RUN_ID}"
mkdir -p "${RUN_DIR}"

PLAYWRIGHT_JSON_OUTPUT_FILE="${RUN_DIR}/reporter.json" \
npx playwright test <筛选范围> \
  --reporter=json,html \
  --output "${RUN_DIR}/output"
```

> **禁止**用 `> file` 重定向 stdout 捕获 JSON。RTK 代理会截断大 JSON 输出导致报告损坏。必须用 `PLAYWRIGHT_JSON_OUTPUT_FILE` 环境变量让 Playwright 直接写文件。

筛选范围：

- 单条：`-g "<caseId>"` 或具体 spec 路径
- 单 route：`.auto-test/case/specs/<route-key>/`
- 全量：留空

## 步骤 4：结果归一

读 `reporter.json`，反查每个 spec 顶部注释里的 `caseId`，写出 `${RUN_DIR}/summary.json`：

```json
{
  "runId": "run-1730000000",
  "passed":    [{"caseId": "...", "specPath": "..."}],
  "failed":    [{"caseId": "...", "specPath": "...", "errorFirst": "..."}],
  "fixmed":    [{"caseId": "...", "specPath": "..."}],
  "escalated": []
}
```

`fixmed` 来自 reporter 的 skipped 中带 `test.fixme()` 的；`escalated` 步骤 5 处理后回填。

## 步骤 5：失败分诊

`failed[]` 为空 → 直接到步骤 7。

`failed[]` 不为空 → 主对话询问用户"是否进入自愈"。用户同意后**逐 case 串行**委托 healer：

1. 对每个 `failed` 项启动一次 `agents/healer.agent.md` subagent
2. healer 按其模板要求返回结构化摘要 `{caseId, status, rootCause, rounds, evidence, suggestedNextStep}`
3. 主对话根据 `status` 更新 `summary.json`：
   - `fixed` → 从 failed 移到 passed，spec 顶部注释已由 healer 加 `@healedAt`
   - `fixmed` → 从 failed 移到 fixmed，healer 已写入 `${RUN_DIR}/fixme.json`
   - `escalated` → 从 failed 移到 escalated，附 `suggestedNextStep`

healer 摘要里禁止贴 a11y 树 / console 全文 / network 原文，只读结构化摘要。

## 步骤 6：escalated 路由

`escalated` 列表非空 → 主对话依据 `rootCause` 与 `suggestedNextStep` 决定：

| rootCause | 路由 |
|---|---|
| i18n | 报告用户：建议进入 02 流程修订对应 nl 的预期文案 |
| business-change | 报告用户：建议进入 02 流程修订 plan / nl |
| real-bug | 报告用户：附 healer 摘要中的 evidence，由用户决定开 bug 还是修代码 |

**主对话不在本流程内直接修 nl/doc/plan**，必须由用户确认后另起 02 流程。

## 步骤 7：完成判定

唯一判定条件：

- `failed[]` 为空（要么全 pass，要么失败的都被分诊到 fixed / fixmed / escalated）

满足即流程结束，进入步骤 8 出报告；否则停止并报告卡在哪个 case 上。

## 步骤 8：报告

写出 `${RUN_DIR}/report.md`，骨架：

```markdown
# Run <runId>

- 跑测范围：<...>
- 起止时间：<...>

## 汇总

- passed: N
- failed→fixed: N
- failed→fixmed: N
- failed→escalated: N

## escalated 列表

| caseId | rootCause | suggestedNextStep |
|---|---|---|
| ... | i18n | 02 修订 nl 文案 |

## fixme 列表

| caseId | reason |
|---|---|
| ... | ... |
```

报告本身不写进 spec 文件。

## 与 03 的边界

- 03 的"首跑 smoke"：单 spec 落盘后的自检，由 generator/healer 在 03 内部解决
- 04 的 run：基于已落盘 spec 集做批量回归，关注汇总结果与失败分诊路由

healer 模板两边共用，仅调用时机不同。

## 不能跳过的理由

- 跳过前置门 → 拿 selector 不合规或链路断裂的 spec 跑，浪费时间且报错误导
- 跳过分诊 → 把 i18n 漂移当 selector 漂移修，埋"假绿"地雷，下次回归才爆
- 跳过 escalated 路由 → 主对话不知道有 nl/doc 漂移，永远修不到根
- 跳过 `@healedAt` 注释 → 后续无法分辨"原始 spec"与"被自愈过的 spec"，回归追溯混乱

## Step 8 追加：生成测试看板

report.md 写完后，自动调用 `06-report.md` 生成看板：

1. 运行 `node ~/.claude/skills/auto-test/scripts/report_gen.mjs --root <项目根>`
2. 拷贝 `~/.claude/skills/auto-test/templates/dashboard.html` → `.auto-test/reports/dashboard.html`
3. 将 `.auto-test/reports/history.json` 内容内联注入到 dashboard.html 的 `<script>` 标签前，格式为 `<script>window.__DASHBOARD_DATA__ = <JSON>;</script>`（使 file:// 协议下也能正常加载数据）
4. 告知用户可打开 `.auto-test/reports/dashboard.html` 查看看板

此步骤失败不阻塞 run 流程的完成判定——看板是增值产物，非完成门。
