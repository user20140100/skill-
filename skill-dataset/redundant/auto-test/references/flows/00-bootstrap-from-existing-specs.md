# 00-bootstrap. 从既有 specs 反向回填子流程

## 何时进入此流程

`01-init.md` 步骤 1 探索项目时，发现项目已有 e2e/Playwright 等测试脚本目录（如 `tests/`、`e2e/`、`playwright/`、`test/e2e/` 等），但 `.auto-test/` 下没有对应的 doc/plan/nl 上游产物。

不能视而不见、也不能直接覆盖。这违反 SKILL 的「步骤不能跳」硬约束（缺 doc 不能有 spec）。必须在进入 `01-init` 后续步骤之前，先决定如何对齐既有 specs。

## 入口判断

满足以下任意一项时进入此流程：

- 项目根目录或常见路径下存在 `*.spec.ts` / `*.spec.js` / `*.test.ts` 且属于 e2e（不是单元测试）。
- 探索时识别出明确的 e2e 目录命名（`tests/`、`e2e/`、`playwright/`、`cypress/`）。
- `.auto-test/case/specs/` 之外存在 Playwright 用例。

## 必须先与用户确认的三选一

由 LLM 主动列出选项让用户选，不可代替决定：

| 选项 | 含义 |
| --- | --- |
| A. 重新走 skill 链路 | 既有 specs 视为遗产，保留不动；`.auto-test/` 走完整 init→doc→plan→nl，由用户后续决定是否替换 |
| B. 反向回填 | 把既有 specs 反推为 doc/plan/nl，之后正向链路与既有 specs 保持双向追溯（推荐用于覆盖范围已稳定的项目）|
| C. 只接管新模块 | 既有 specs 不动，本次只对新增/未覆盖模块走 init→doc→plan→nl |

未确认前不得继续 `01-init.md` 的步骤 2/3/4。

## 选项 B：反向回填执行步骤

仅当用户选 B 时执行，否则跳过本节。

### B-1 扫描既有 specs

按目录列出每个 spec 文件，提取：

- `test('...')` 标题
- `describe('...')` 分组
- 主要交互动作（点击/输入/断言）
- 用到的 URL / 路由
- 用到的固定数据 / fixture

输出 `.auto-test/.tmp/spec-inventory.md` 作为中间产物（不进 git）。

### B-2 路由聚合

按 `02-doc-plan-nl.md` 的「产物组织约定」中 `<route-key>` 规则，把 specs 归类到路由。一个 spec 横跨多路由时，拆解到各自路由名下。

### B-3 反推 doc

对每个路由调用 `agents/doc-reverse.agent.md`（按 02-doc-plan-nl.md 的「Agent 启动协议」启动），输入：

- 该路由聚合后的 spec 标题/动作/断言摘要
- 可选：对应源码（若 `componentRoot` 已确定）

输出 `.auto-test/docs/<route-key>.md`，frontmatter 必须含：

```yaml
source: reverse-engineered-from-spec
needReview: true
linkedSpecs:
  - <既有 spec 路径>
```

### B-4 生成 plan/nl

按 `02-doc-plan-nl.md` 步骤 3/4 正向生成 plan、nl，但每条用例必须在 frontmatter 增加 `linkedSpec` 字段，回链到原 spec 文件，方便后续判断"哪些既有 spec 已对齐 / 哪些缺失"。

### B-5 双向校验

完成后必须输出对齐报告 `.auto-test/.tmp/spec-alignment.md`：

- 已对齐：spec ↔ nl 双向追溯。
- 仅 spec 无 nl：spec 描述的行为 plan 没覆盖，需后续补 plan/nl。
- 仅 nl 无 spec：plan 推出的用例 spec 没实现，标记为待生成。

报告产出后才允许结束本流程。

## 选项 A / C 后续处理

- 选项 A：直接进入 `01-init.md` 步骤 2 起的常规流程。`.auto-test/` 与既有 specs 暂无关联，需在最终交付时由用户决定是否替换。
- 选项 C：在 `.auto-test/config.json` 增加 `targets[]` 限定本次只覆盖新模块；既有 specs 保持原状。

## 禁止事项

- 禁止在用户未确认前读取并修改既有 specs。
- 禁止把既有 specs 当作 plan/nl 直接使用——必须先沉淀 doc。
- 禁止在 B 流程中删除或移动既有 spec 文件。
- 禁止把反向回填得到的 doc 标记为 `source: external`，必须用 `reverse-engineered-from-spec`。
