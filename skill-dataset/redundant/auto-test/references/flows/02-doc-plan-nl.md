# 02. 从初始化到生成 nl 子流程

## 目标

在 init 完成后，按五层链路生成到自然语言用例 `nl`：

```text
init → doc → plan → nl
```

本流程不生成 Playwright spec，不运行测试。

## 前置条件

进入本流程前必须满足：

- 入口自检（`SKILL.md §2.1`）若返回 `warningCode=NOT_INITIALIZED` 或 `STATE_CORRUPTED`，**禁止进入本流程**，必须先回 `01-init.md`。
- `.auto-test/config.json` 存在。
- `.auto-test/docs/` 存在。
- `.auto-test/case/plans/` 存在。
- `.auto-test/case/nl/` 存在。
- `componentRoot` 已确认或明确无代码。

前置条件不满足时，停止并回到 `01-init.md`。

## Agent 启动协议

本子流程中凡是需要启动 subagent，统一使用 generalPurpose subagent + 模板路径的方式启动。skill 自带的 `agents/*.agent.md` **没有**注册到 Claude Code 的 subagent 列表，所以**唯一标识就是文件路径**——既不要用 `name` 字段，也不要用 `Use the <name> subagent` 句式，那样必然失败。

### 标准启动方式：generalPurpose + 模板路径

启动 prompt 的第一行必须要求 subagent 先读取对应模板，模板路径用绝对路径。模板位于 skill 目录：

| 场景 | 模板（绝对路径） | 作用 |
| --- | --- | --- |
| 阅读和审计代码 | `~/.claude/skills/auto-test/agents/code-fact.agent.md` | 只读源码，审计并返回页面、路由、字段、交互、状态、异常、隐式行为、边界处理、防御缺失等事实摘要 |
| 从代码反推需求文档 | `~/.claude/skills/auto-test/agents/doc-reverse.agent.md` | 根据代码事实生成 `.auto-test/docs/` 下的 reverse-engineered doc 草稿 |
| 页面探索增强 plan | `~/.claude/skills/auto-test/agents/planner.agent.md` | 打开真实页面，补充页面事实、用户路径、边界和错误场景 |
| 生成自然语言用例 nl | `~/.claude/skills/auto-test/agents/nl-author.agent.md` | 根据 plan 生成中文自然语言用例 |

> 实际调用时把 `~` 展开为用户主目录绝对路径（例如 `/Users/<you>/.claude/...`），subagent 工具不会做 shell 展开。
> 流程文档与日志中**只用文件路径**指代 agent，不要再用旧的 `auto-test-code-fact` 等名字。

启动模板：

```text
Launch a generalPurpose subagent with prompt:

请先读取并严格遵循 <模板绝对路径>。

任务：<一句话任务描述，与模板职责对齐>
输入：
- 项目根目录：<root>
- componentRoot：<componentRoot>
- 目标模块：<target>
- 上游文档：<doc path or none>
- 本次问题：<question>
约束：所有源码必须完整读完（不传 offset/limit、不抽样、不跳读），目标文件 import 的本仓库内部模块必须递归跟读到底；不要为了节省 token 偷懒，漏读 = 事故。
输出：按模板要求返回结果，并在「引用文件」中标注每个文件 [已完整读取 N 行]。
```

主进程收到 subagent 结果后，只能使用其摘要，不得把 subagent 未确认的信息当成事实。如发现「引用文件」未标注 `[已完整读取 N 行]` 或某文件 N 明显小于实际行数，必须打回重读，不得继续下游步骤。

## 步骤 1：确定 doc 来源

读取 `.auto-test/config.json` 的 `docs.mode`。

### docs.mode=external

项目已有需求文档。

要求：

- 在 `.auto-test/docs/` 中生成需求映射文档。
- 映射文档必须链接到已有需求文档。
- 映射文档记录原始路径、原始 hash、关联源码候选和后续反链位置。
- 不直接覆盖或改写原需求文档。

### docs.mode=internal

项目没有外部需求文档，需要先从代码反推需求。必须严格按照要求启动对应的 subagent，不然会浪费更多的token，结果也必然是错的，导致生产级别事故。

要求：

- 必须先按"Agent 启动协议"调用 `agents/code-fact.agent.md`，阅读代码并返回功能事实摘要。
- 再按"Agent 启动协议"调用 `agents/doc-reverse.agent.md`，根据代码事实摘要生成 `.auto-test/docs/` 下的反推需求文档。
- 反推需求文档必须标记 `source: reverse-engineered` 和 `needReview: true`。

### docs.mode=none

不推荐继续自动生成 plan/nl。

只有用户明确要求“暂时不接入需求也继续基于代码探索”时，才允许转为类似 `internal` 的反推路径。否则停止并提示缺少 doc 来源。

## 步骤 2：判断代码是否可用

根据 `componentRoot` 和项目结构判断是否有可读代码，必须严格按照要求启动对应的 subagent，不然会浪费更多的token，结果也必然是错的，导致生产级别事故。

如果需要阅读代码：

- 主进程不得大段读代码后直接推导。
- 必须按"Agent 启动协议"调用 `agents/code-fact.agent.md`。
- `agents/code-fact.agent.md` 只返回事实摘要，不返回大段源码。
- **下发任务时必须显式写明「完整读完目标文件及其本仓库内部引用，禁止只读片段、禁止抽样、禁止 token 优化」**。漏写这一条会让 subagent 倾向于只读前几百行就下结论，造成行为漏列事故。

代码审计摘要应包括：

- 页面入口和路由。
- 用户可见功能。
- 表单字段和校验规则。
- 按钮、菜单、tab、弹窗等交互。
- 权限、状态、空态、异常态。
- 隐式行为：文档未提及但代码存在的逻辑（trim、截断、默认值、排序等）。
- 边界处理：输入长度限制、特殊字符、空白字符的实际处理方式。
- 防御性缺失：外部输入消费点缺少 try-catch、类型守卫或格式校验的位置。
- 与需求文档不一致或无法确认的点。

## 产物组织约定（强制）

doc / plan / nl 必须按"路由 / 页面"为最小单位拆分，禁止把多个路由合并到同一个 plan 或 nl 文件。

### 目录结构

```text
.auto-test/
  docs/
    <route-key>.md            # 一个路由/页面一个反推 doc
  case/
    plans/
      <route-key>.plan.md     # 一个路由/页面一个 plan
    nl/
      <route-key>/            # 每个路由建独立子目录
        <feature-slug>-<seq>.md
```

### 命名规则

- `<route-key>`：从路由路径推导，去前导 `/`，把 `/` 换成 `-`，根路径用 `home`。
  - `/` → `home`
  - `/success` → `success`
  - `/users/:id/edit` → `users-id-edit`
- `<feature-slug>`：用例所测功能的中文转拼音/英文小写短语（≤4 个单词），`-` 分隔。例如 `submit-validation`、`history-restore`、`access-permission`。
- `<seq>`：两位数字编号，从 `01` 开始，按 plan 内顺序递增。
- 完整 nl 文件名示例：
  - `.auto-test/case/nl/home/access-permission-01.md`
  - `.auto-test/case/nl/home/submit-validation-03.md`
  - `.auto-test/case/nl/success/back-to-survey-01.md`

### 拆分原则

- **plan 按路由拆**：`/` 一个 plan、`/success` 一个 plan，绝不合并。即使某个路由只有 1-2 条用例，也单独建 plan。
- **路由级兜底（如 `*` → 重定向）**：归到被重定向到的目标路由的 plan（例如 `*` → `/` 的兜底用例属于 `home.plan.md`）。
- **nl 按功能分组**：同一路由内，按"功能"分组写 nl 文件（如"权限态"、"提交校验"、"历史回填"），每组用例编号从 `01` 起。
- **caseId 字段**：frontmatter 仍保留 `caseId`，格式为 `<route-key>/<feature-slug>-<seq>`，便于跨文件引用。
- **plan 文件内的用例 ID**：用 `<feature-slug>-<seq>` 列在表格中，与 nl 文件名一一对应。**禁止**继续使用 `M1-1 / M3-2` 这种"模块字母 + 序号"的形式（除非该模块就是路由本身）。

### 反例

- ❌ `.auto-test/case/nl/M1-1.md`（按抽象模块编号扁平堆放）
- ❌ `.auto-test/case/plans/survey.plan.md` 同时覆盖 `/` 和 `/success`
- ✅ `.auto-test/case/plans/home.plan.md` + `.auto-test/case/plans/success.plan.md`
- ✅ `.auto-test/case/nl/home/submit-validation-01.md`

## 步骤 2.5：doc 覆盖自检（强制）

doc 生成后、进入 plan 之前，主进程必须自动校验以下内容：

1. **能力地图**存在且每行"是否纳入本轮"非空
2. **页面载体地图**存在且非空
3. **能力域覆盖确认表**存在
4. **规格与实现差异**有明确结论（差异表或"无差异"声明）

自检标准（任一不满足则 doc 不合格，自动回退补充）：

- 没有能力地图：回退，让 doc-reverse 补充
- 没有页面载体地图：回退补充
- 没有能力域覆盖确认表：回退补充
- 没有规格与实现差异结论：回退补充
- 能力地图中存在"是否纳入本轮"为空的行：回退补充

AI 自主判断覆盖范围是否合理：
- 核心用户路径对应的能力域必须纳入
- 仅在明确属于其他模块职责、或用户显式指定排除时才标"否"
- 有疑问时倾向纳入（宁多勿漏）

自检通过后直接进入 plan，无需等待用户确认。

## 步骤 3：生成 plan

plan 生成按三种情况处理。**无论哪种情况，都必须按上面的「产物组织约定」按路由拆分 plan，每个路由一个文件。**

必须严格按照要求启动对应的 subagent，不然会浪费更多的token，结果也必然是错的，导致生产级别事故。
### 有需求文档 + 有代码

使用需求文档和代码审计**双驱动**生成 plan。需求文档定义"应该测什么"，代码审计发现"还需要测什么"——两者同等权重。

要求：

- 需要代码事实时，先按"Agent 启动协议"调用 `agents/code-fact.agent.md`。
- **必须**按"Agent 启动协议"调用 `agents/planner.agent.md` 做一次真实页面探索，**禁止**以"已有代码事实摘要 / 已有登录后 snapshot / 已知足够信息"为由跳过。planner 的职责不是补 snapshot，而是产出页面级的用户路径、边界条件、错误态——这些用 code-fact 推不出来，用一次性 snapshot 也覆盖不全。
- planner 调用前主进程必须先确认 dev server 探活 OK、登录态已采集（参考 `01-init.md` 步骤 4.0 / 4.1），否则停止并回 01-init 修复。
- plan 必须引用 doc。
- plan 必须区分来自需求的规则和来自代码的事实。
- 如果需求和代码不一致，标记为待确认，不自行裁决。
- **code-fact 行为必须全量纳入 plan 决策**：code-fact 行为清单中文档未提及的行为（如边界输入处理、防御性缺失、隐式 trim/截断逻辑），plan 必须逐条决策是否纳入。纳入的生成对应用例行；不纳入的必须在 plan 用例表格中显式标注 `coverage: skipped` + 原因，禁止静默忽略。
- **代码审计发现的边界和缺陷与需求同权**：code-fact 中 `kind=defensive-gap` 的行为必须在 plan 中生成对应的缺陷发现型用例（测试类型标记为"异常/缺陷探测"），不允许因为"文档没提"而排除。

### 有需求文档 + 没有代码

直接根据需求文档生成 plan。

要求：

- plan 只能表达“应该测试什么”。
- 不能编造页面事实、selector、真实按钮状态或运行路径。
- plan 标记 `pendingCode: true`。

### 只有代码 + 没有需求文档

不能直接从代码跳到 plan。

要求：

- 先按 `docs.mode=internal` 反推需求文档。
- 再用反推需求文档和代码事实生成 plan。
- plan 标记 `source.doc: reverse-engineered` 和 `needReview: true`。

### 步骤 3.5：回填 doc.linkedPlans（强制）

plan 生成完毕后，**主进程必须立即编辑对应 doc**，把刚生成的 plan 路径追加到 doc frontmatter 的 `linkedPlans` 数组里。doc 是早于 plan 生成的，`doc-reverse` agent 写出的 `linkedPlans: []` 必然是空的，由本步骤负责回填。

要求：

- 路径用相对 doc 文件的相对路径（如 `../case/plans/<route-key>.plan.md`）或项目根相对路径，全 doc 内统一。
- 一个 doc 对应一个 plan（按路由拆分约定），`linkedPlans` 长度应 = 1；多于 1 视为路由聚合错误，停止并报告。
- 回填后 doc 内容其余部分不得修改。

### 步骤 3.6：plan 覆盖完整性要求（强制）

每个 plan 文件在用例表格之前，必须包含以下三个覆盖保障结构：

#### 固定覆盖清单对照表

plan 文件头部必须输出固定覆盖清单对照表，覆盖以下 11 个维度，每个维度标注状态：

```markdown
## 固定覆盖清单对照表

| 维度 | 状态 | 对应用例 | 备注 |
| --- | --- | --- | --- |
| 主流程与替代流程 | 已覆盖 | submit-validation-01 | - |
| 状态机与状态切换 | 已覆盖 | status-change-01 | - |
| 入口与退出 | 已覆盖 | navigation-01 | - |
| 外部依赖与异步链路 | 不适用 | - | 纯前端页面无外部调用 |
| 页面区域与交互载体 | 已覆盖 | ... | - |
| 数据展示与内容规则 | 已覆盖 | ... | - |
| 编辑/筛选/搜索/操作类交互 | 已覆盖 | ... | - |
| 异常与失败恢复 | 已覆盖 | error-handling-01 | - |
| 边界与临界值 | 已覆盖 | boundary-01 | - |
| 性能/兼容性/权限安全 | 不适用 | - | 非本轮覆盖范围 |
| 数据持久化验证 | 已覆盖 | persist-reload-01 | 写入后 reload 确认 |
```

状态固定为：`已覆盖`、`不适用`、`未覆盖`、`待确认`。

- `不适用` 必须写原因
- `数据持久化验证`：应用使用 localStorage / IndexedDB / cookie / 文件等本地持久化时，必须覆盖"写入后刷新页面（硬 reload）确认数据仍存在"和"删除后刷新确认数据已移除"两条路径。无本地持久化时标"不适用"。
- `未覆盖` 和 `待确认` 是阻塞项，存在时 plan 不能通过门禁

#### 模块补充覆盖项

在固定清单之后，根据模块特性补充额外覆盖项：

```markdown
## 模块补充覆盖项

| 补充维度 | 状态 | 对应用例 | 备注 |
| --- | --- | --- | --- |
| 录制后台保活 | 已覆盖 | background-keep-alive-01 | 模块特有 |
| 多端状态同步 | 待确认 | - | 需确认是否本轮覆盖 |
```

#### 四视角检查标记

plan 中每个功能块（对应 doc 能力地图中的一个能力域）必须显式经过四视角检查，在用例表格中增加一列或在功能块标题下方标注：

```markdown
### 能力域：录制控制

四视角检查：
- 状态：✅ 已覆盖（开始/暂停/继续/完成四态）
- 交互：✅ 已覆盖（按钮点击、快捷键）
- 异常：✅ 已覆盖（录制冲突、存储满、权限拒绝）
- 边界：✅ 已覆盖（最大时长、最小时长、并发录制）

| 用例 ID | 标题 | 测试类型 | 优先级 | ... |
```

规则：
- 四视角为：`状态`、`交互`、`异常`、`边界`
- 每个视角标注 `✅ 已覆盖（简要说明）` 或 `⬜ 不适用（原因）`
- 禁止留空不标注
- 若某个视角标注"不适用"，必须写原因

### 步骤 3.7：plan 覆盖自检（强制）

plan 生成后、进入 nl 之前，主进程必须自动校验：

1. **固定覆盖清单对照表**：11 个维度全部为"已覆盖"或"不适用"
2. **模块补充覆盖项**：全部为"已覆盖"或"不适用"
3. **四视角检查**：每个能力域功能块都有完整的四视角标注

自检标准（任一不满足则自动修复）：

- 固定覆盖清单存在"未覆盖"：AI 自主补充对应测试用例，将状态改为"已覆盖"
- 固定覆盖清单存在"待确认"：AI 根据 doc 能力地图和代码事实自主决策——属于本路由职责的纳入覆盖，不属于的标"不适用+原因"
- 模块补充覆盖项存在"未覆盖"：同上，自主补充
- 任何能力域缺少四视角检查标记：自动补充
- 四视角中存在空标注：自动补充

AI 决策原则：
- **宁多勿漏**：有疑问时倾向覆盖，生成对应测试用例
- **不适用必须有依据**：标"不适用"时，原因必须可追溯到 doc 中的能力域覆盖确认表（已标"否"的能力域）
- **边界和异常不能省**：即使主流程简单，边界和异常视角也不能标"不适用"，除非该能力域确实无状态变化和外部输入

自检通过后直接进入 nl 生成，无需等待用户确认。

## 步骤 4：生成 nl

nl 必须基于 plan 生成。**输出路径必须遵循「产物组织约定」**：`.auto-test/case/nl/<route-key>/<feature-slug>-<seq>.md`，禁止扁平堆在 `.auto-test/case/nl/` 根目录。

### 有代码

使用 plan 结合代码事实推导 nl。

必须严格按照要求启动对应的 subagent，不然会浪费更多的token，结果也必然是错的，导致生产级别事故。
要求：

- 如果生成 nl 需要判断操作路径、字段规则、页面状态、异常分支，必须先按"Agent 启动协议"调用 `agents/code-fact.agent.md`，阅读代码并返回事实摘要。
- 然后按"Agent 启动协议"调用 `agents/nl-author.agent.md`，输入 plan、上游 doc、代码事实摘要和输出目录，生成 nl。
- nl 应使用用户界面语言描述操作。
- nl 不应出现源码路径、函数名、组件名、接口路径等实现细节。

### 没有代码

主进程直接基于 plan 推导 nl。

必须严格按照要求启动对应的 subagent，不然会浪费更多的token，结果也必然是错的，导致生产级别事故。
要求：

- 不启动代码阅读类 subagents。
- 可以按"Agent 启动协议"调用 `agents/nl-author.agent.md`，但输入中必须明确没有代码事实摘要。
- nl 只能表达 plan 中的测试意图和界面操作预期。
- nl 必须标记 `pendingCode: true`。
- 禁止编造真实 selector、页面实际状态或实现细节。

### 步骤 4.5：回填 doc.linkedNl（强制）

nl 全部生成完毕后，**主进程必须立即编辑对应 doc**，把该路由所有 nl 文件路径追加到 doc frontmatter 的 `linkedNl` 数组里。

要求：

- 路径列表按文件名字典序排列，便于 diff 稳定。
- 路径形态与 `linkedPlans` 保持一致（同为相对 doc 或同为项目根相对）。
- 同时检查每个 nl 文件 frontmatter 的 `docRef` 是否指向当前 doc——任何一条对不上，停止并报告。
- 回填后 doc 内容其余部分不得修改。

## 步骤 5：完成校验

生成 nl 后必须校验：

- 每个 nl 都能追溯到 plan。
- 每个 plan 都能追溯到 doc。
- **每个 doc 必须包含「能力地图」「页面载体地图」「能力域覆盖确认表」「规格与实现差异」四个章节**，缺少任一视为 doc 不合格。
- **每个 doc 的能力地图中"是否纳入本轮=是"的能力域，必须在 plan 中有对应的功能块和测试用例**；缺少视为覆盖缺口，直接 fail。
- **每个 plan 必须包含「固定覆盖清单对照表」「模块补充覆盖项」**，且所有状态为"已覆盖"或"不适用"（无"未覆盖"或"待确认"）。
- **每个 plan 的每个能力域功能块必须有四视角检查标记**（状态/交互/异常/边界），无空标注。
- **每个 doc 的 `linkedPlans` 非空且包含其下游 plan 路径**；**`linkedNl` 非空且覆盖该路由全部 nl 文件**。如步骤 3.5 / 4.5 漏回填，本校验直接 fail。
- **plan 数量 ≥ 路由数量（兜底路由除外）**；同一路由的所有用例必须在同一个 plan，跨路由用例必须分到各自 plan。
- **nl 必须在 `.auto-test/case/nl/<route-key>/` 子目录下**，不能直接挂在 `nl/` 根目录；文件名遵循 `<feature-slug>-<seq>.md`。
- 有代码事实参与时，代码事实来自 `agents/code-fact.agent.md` 摘要。
- 无代码时，相关 plan/nl 均标记 `pendingCode: true`。
- 存在待确认项时，不能宣称链路已完全可靠。
- **planner 强制执行 gate**：步骤 3"有需求文档 + 有代码"分支生成的每个 plan，frontmatter 必须含 `plannerRunId` 字段（由 planner subagent 返回），且非空；缺失视为 planner 被跳过，直接 fail。
- **行为覆盖闭环（强制 gate）**：
  - 有代码事实时：code-fact 行为清单中每个 `B<n>` 必须在至少一个 nl 的 `behaviorRefs` 中出现，**或**在 plan 用例表格对应行显式标 `coverage: skipped` + 原因（`远端不可控` / `实现细节` / `业务确认中` 三选一）。漏一条直接 fail。
  - 所有 nl 的 `behaviorRefs` 必须能在 code-fact 行为清单中找到，禁止悬空 ID。
  - 无代码（`pendingCode: true`）时本条降级为：每条 nl 的 `behaviorRefs` 必须能在 plan 用例表格中找到对应行 ID。

任一项不满足，停止并报告缺失，不进入 spec 阶段。
