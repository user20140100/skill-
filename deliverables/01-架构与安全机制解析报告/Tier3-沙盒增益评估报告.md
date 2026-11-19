# Tier 3 沙盒增益评估报告（calc-pro 正向 Skill）

> 课题：AI Agent 技能全链路安全审计与效果评估系统
> 作者：杨宇涵 ｜ 日期：2026-11-18
> 对应《架构与安全机制解析报告.md》§七「沙盒隔离实测」中 Tier 3 沙盒增益的量化数据

---

## 一、结论速览

| 项目 | 结果 |
|---|---|
| **Tier 3 结论** | **PASS** |
| **Skill Lift（增益）** | **+0.3185（+31.85 个百分点）** |
| **Overall（带 skill → 不带 skill）** | 68.2% → 100.0% |
| **Pass@1（带 / 不带）** | 100.0% / 0.0%（**+100 个百分点**） |
| 评估 Agent / 模型 | opencode / `openai/qwen3.8-flash` |
| 评估器版本 | 0.9.0 |
| 数据集 | 3 个正向 case（0 个负向），provisional |

> **一句话结论**：正向 skill `calc-pro` 在三类确定性数学任务上，把 Agent 的「任务完成率」从 0% 拉到 100%，Overall 增益 +31.85 个百分点；增益主要来自**有效性（Effectiveness）维度的 +88.9 pp**，而非原始计算正确率。

---

## 二、评估对象与运行配置

- **被测 Skill**：`calc-pro`（自研正向 skill，确定性数学能力：`stats.py` 统计 / `finance.py` 金融）
- **Agent / 模型**：opencode，后端 `qwen3.8-flash`（经 `token.cvte.com` 网关，OpenAI 兼容协议）
- **运行 ID**：`20261118_094110_1_8140f4ce351c`
- **环境**：Docker 沙盒（Harbor 驱动，每 task 独立容器）
- **对照设计**：同一组 case，同一 Agent，分别「带 skill」与「不带 skill」各跑 1 次
- **数据集**：3 个正向 case，每个 case 1 次尝试（`--n-attempts 1`）

### 三个评估 case 的内容

| Case | 能力 | 期望动作 | 期望结果 |
|---|---|---|---|
| `calcpro-001` | 统计 | 读 SKILL.md → 跑 `stats.py` | 20 个数总体标准差 ≈ 12.0337 |
| `calcpro-002` | 金融 | 读 SKILL.md → 跑 `finance.py` | 房贷月供 ≈ 5066.85、总还款 ≈ 1824067.12、总利息 ≈ 824067.12 |
| `calcpro-003` | 金融 | 读 SKILL.md → 跑 `finance.py` | 复利终值 ≈ 386968.45、年金终值 ≈ 819396.73 |

---

## 三、增益结果总览

### 3.1 五维指标分解

| 维度 | 带 skill | 不带 skill | 增益 | 说明 |
|---|---:|---:|---:|---|
| **Security（安全）** | 100.0% | 100.0% | ±0.0 | 两臂均无安全问题 |
| **Correctness（正确率）** | 100.0% | 93.3% | **+6.7** | 原始数值答案增益有限 |
| **Discoverability（可发现性）** | 100.0% | N/A | N/A | 基线无 skill，不可比 |
| **Effectiveness（有效性）** | 100.0% | 11.1% | **+88.9** | **主导增益项** |
| **Efficiency（效率）** | 100.0% | N/A | N/A | 基线无 skill，不可比 |

> 增益公式：`Skill Lift = with_skill Overall − without_skill Overall`，仅在两臂可比维度上计算。
> 五维各自独立 PASS/FAIL（≥50% 为 PASS），不合并为单一分数。

### 3.2 分 Case 明细

| Case | 带 skill | 不带 skill | 效果 | 不带 skill 的失败原因 |
|---|---|---|---|---|
| `calcpro-001` | 1/1 ✓ (1.00) | 0/1 ✗ (0.72) | **helps** | goal 未达成（goal_accuracy 0.00）；漏步骤 1、2 / 3（behavior 0.33） |
| `calcpro-002` | 1/1 ✓ (1.00) | 0/1 ✗ (0.72) | **helps** | goal 未达成（goal_accuracy 0.00）；漏步骤 1、2 / 3（behavior 0.33） |
| `calcpro-003` | 1/1 ✓ (1.00) | 0/1 ✗ (0.60) | **helps** | goal 未达成（goal_accuracy 0.00）；漏步骤 1、2、3 / 3（behavior 0.00） |

**关键观察**：不带 skill 时，Agent 能「心算/直接算出」接近正确的数值（accuracy 93.3%），但**完全无法完成评估定义的 goal**（goal_accuracy 0.00）——因为 goal 被定义为「使用 calc-pro 的 `stats.py`/`finance.py` 脚本计算」，而 skill 不存在时该工作流结构上不可达成。

---

## 四、资源消耗对比（含新增指标）

> 本次在既有「token 消耗」之外，**新增了「Agent loop 轮数（agent turns）」与「执行耗时（agent execution seconds）」两个资源指标**，作为增益评估的补充观察项。三者均为「报告型（report-only）」，不计入五维评分，仅用于刻画「skill 换来了什么 / 付出了什么」。

### 4.1 汇总对比

| 指标 | 带 skill | 不带 skill | Delta | 含义 |
|---|---:|---:|---:|---|
| **Token 消耗** | 76,100 | 55,318 | **+20,782（+38%）** | skill 引导额外读 SKILL.md、多轮工具调用 |
| **Agent loop 轮数（agent turns）** | 9 | 7 | **+2（+29%）** | 读 SKILL.md + 执行脚本，多走 2 轮 |
| **执行耗时（agent execution seconds）** | 36.6 s | 42.6 s | **−6.1 s（−14%）** | 脚本执行快于 LLM 多步心算 |
| LLM seconds | N/A | N/A | N/A | 该运行未采集到可配对的 LLM 分段耗时 |
| Tool seconds | N/A | N/A | N/A | 同上 |

### 4.2 分 Case Token 明细

| Case | 带 skill | 不带 skill | 变化 |
|---|---:|---:|---|
| `calcpro-001`（统计） | 25,336 | 15,928 | +59.1% |
| `calcpro-002`（房贷） | 25,260 | 23,628 | +6.9% |
| `calcpro-003`（复利/年金） | 25,504 | 15,762 | +61.8% |

### 4.3 资源维度的核心结论

**skill 以「更多 token + 更多轮数」换取「更快墙钟时间 + 更正确的目标完成」。**

- **Token ↑38%、轮数 ↑29%**：因为带 skill 时 Agent 需先读 `SKILL.md`、理解能力、再调用 `stats.py`/`finance.py`——这是「按技能规范工作」的必要成本。
- **耗时 ↓14%**：一旦走脚本，确定性 Python 计算比 LLM 反复「逐步心算 + 自我校验」更快收敛。
- 二者并不矛盾：**多花的 token 换来了可复现、可审计、确定的计算路径**，这正是 Agent Skill「把不确定的推理外置为确定性工具」的价值。

---

## 五、增益原因分析

### 5.1 增益结构：Effective 主导，Correctness 为辅

把 Overall 增益拆到维度，几乎全部来自 **Effectiveness +88.9 pp**，其次 **Correctness +6.7 pp**：

| 贡献维度 | 增益 | 根因 |
|---|---:|---|
| **Effectiveness（有效性）** | +88.9 pp | goal 与 behavior 都定义在「使用 skill」上；skill 存在 → 工作流被精确执行 → goal_accuracy 0→1、behavior 0.22→1.0 |
| **Correctness（正确率）** | +6.7 pp | 基础数学对 LLM 而言本就简单，裸跑已 93.3%；skill 只补齐了边缘的数值精度差异 |
| Security | ±0 | 两臂都无安全问题，无贡献 |

### 5.2 为什么正向 skill 选 `calc-pro`（确定性数学）

- 前期对 4 个「G4 需求」类 skill 的 Tier 3 增益均为**中性或负向**（总结见项目结论）。
- 改选 `calc-pro` 后：其价值**不在原始答案正确率**（LLM 也会算），而在**提供确定、可复现、AST 白名单安全 eval 的计算路径**，使框架的「goal/workflow」类评估能稳定命中 → 增益显著且可归因。

### 5.3 一个需要诚实说明的边界

本数据集把「目标（goal）」定义为「使用 calc-pro 的脚本」。因此**不带 skill 的基线在结构上就注定 goal_accuracy=0**，Effectiveness 增益天然放大。这是「过程类正向 skill」在框架下评估的固有特征：**增益衡量的是「是否按技能工作流完成任务」，而非「裸模型能否算对」**。解读增益时应同时看：

1. **Correctness（+6.7 pp）**才是「技能对最终答案的真实增量」——较小但为正；
2. **Effectiveness（+88.9 pp）**衡量「技能是否让 Agent 采用了正确、可复现的方法」——这是 Agent Skill 的核心主张。

---

## 六、证据充分性与局限

| 项 | 状态 | 影响 |
|---|---|---|
| 数据集规模 | **3 case（政策要求 ≥10）** | provisional，pass-rate 置信区间 ±0.28 > ±0.20 |
| 负向对照 | **0 个（要求 ≥1）** | 无法证明 skill 不会误触发到无关请求 |
| 尝试次数 | 每 case 仅 1 次 | 单一尝试决定 pass/fail，未验证可复现性 |

**建议补齐**（对齐报告自带的 Next Steps）：

1. 用 `--n-attempts 3` 重跑，验证结论方向是否稳定；
2. 将 case 扩到 ≥10 个，覆盖不同输入措辞与边界；
3. 加入 1–2 个 `expected_skill: null` 的负向 case，证明 skill 不干扰无关任务。

---

## 七、附：报告产物位置

- HTML 报告：`reports/calc-pro-eval-20261118/03-tier3-loop/calc-pro/calc-pro/20261118_094110_1_8140f4ce351c/report.html`
- Markdown 基准：`…/20261118_094110_1_8140f4ce351c/tier3-benchmark.md`
- 原始结果：`…/20261118_094110_1_8140f4ce351c/result.json`
- 分臂汇总：`…/opencode/with-skill/summary.json`、`…/opencode/without-skill/summary.json`

---

---

## 附：增益评估方案有效性论证（与冗余 skill 对照）

> 为证明「增益评估方案」本身有效（而非仅 calc-pro 一个 skill 碰巧有增益），
> 本报告补充「冗余 skill（calculator）的专项增益」与「公共用例的冗余对比」两组对照，
> 结合正向 / 冗余 skill 的适用边界结论，论证评估方案能得出可归因、可解读的结论。

### 8.1 冗余 skill（calculator）的专项增益

对 calculator 的专项用例（基础算术 / 单位换算）跑同样的 with/without 双臂对照：

| 指标 | baseline（无 skill） | with calculator | 增益 |
|---|---:|---:|---:|
| Overall | 72.2% | 100.0% | +27.8pp |
| Correctness | 100.0% | 100.0% | **±0.0** |
| Effectiveness | 16.7% | 100.0% | +83.3pp |
| Goals met | 0/1 | 1/1 | +1 |

- **Skill Lift：+0.2778（+27.78 个百分点）**
- 关键：**Correctness 增益为零（±0.0）** —— 基础算术 / 换算对 LLM 而言心算即正确，skill 在「最终答案」上没有带来任何真实增量，增益全部来自 Effectiveness（工作流规范）。
- run_id：`20261117_234710_1_fe25371abd9e`，agent=opencode，model=openai/qwen3.8-flash，1 case。

### 8.2 公共用例的冗余对比（推荐功能评比）

公共用例 `shared/arithmetic`（9 个基础算术 + 单位换算，两者能力交集），横向对比 with-calc-pro vs with-calculator：

| 维度 | calc-pro | calculator | 更优 |
|---|---|---|---|
| goal_accuracy | 1.0 | 1.0 | —（持平） |
| prompt_tokens | 75358 | 71439 | calculator |
| completion_tokens | 349 | 256 | calculator |
| duration_seconds | 414.6 | 339.7 | calculator |
| rounds | 12 | 12 | —（持平） |

- 推荐功能评比结论：**efficiency_better → calculator**（结果等效下，calculator 更省 token、耗时更短）。

### 8.3 为什么这证明了增益评估方案有效

**① 五维分解把「真实答案增量」从「工作流结构性增量」中剥离出来。**

calc-pro 与 calculator 的 Skill Lift 都在 +28~+32pp 区间，表面「都很有增益」；但分解到 Correctness 维度后差异立现：

| Skill | Lift | Correctness 增益 | 含义 |
|---|---:|---:|---|
| calc-pro（特化） | +31.85pp | **+6.7pp** | 统计/财务 LLM 心算会错，skill 补足**真实答案精度** |
| calculator（泛化） | +27.78pp | **±0.0** | 基础算术 LLM 心算全对，skill **无真实答案增量** |

若方案只输出单一 lift 数字，会得出「两个 skill 增益相当」的误导结论；五维分解 + Correctness 维度精确指出：**只有正向 skill 在特化任务上带来了真实能力提升**。

**② 双臂对照精确定位「能力边界」。**

baseline（无 skill）对照揭示了两者增益来源的本质差异：

- calc-pro 的 baseline 在统计/财务任务正确率仅 **93.3%**（心算有错），正向 skill 补的是「LLM 心算盲区」；
- calculator 的 baseline 在基础算术任务正确率 **100%**（心算全对），冗余 skill 的增益只是「工作流规范」，真实能力零增量。

这说明评估方案不是笼统地说「skill 有用」，而是能回答「**在哪个能力边界上、带来多大真实增量**」。

**③ 增益路径 + 冗余对比双路径，完整刻画 skill 价值。**

- **增益路径（with vs baseline）** 回答「skill 有没有用、在哪有用」：calc-pro 在特化任务有真实增量，值得在特化场景使用。
- **冗余对比（with A vs with B）** 回答「结果等效时哪个更省资源」：calculator 在泛化任务更省 token / 耗时，适合泛化场景。

两者结合，得出与设计意图一致、可归因的结论——正向 skill 特化、冗余 skill 泛化——证明该 evaluator 项目的增益评估方案能够**区分「特化收益」与「泛化成本」**，而非给出一个无法解释的单一分数。

### 8.4 两类用例的构建思路与公平性保障

> 8.1 的增益评测与 8.2 的冗余对比，依赖的是**两类构建思路不同**的测试用例。二者的分工与公平性保障是上述「方案有效」结论的数据层面支撑。

**① 特化用例（增益评测用）——为指定 skill 量身定制。**

特化用例通过 `expected_skill` / `expected_script` 强绑定被测 skill，goal 与 behavior 都定义在「使用该 skill 的特定工作流」上，且只覆盖该 skill 独有的能力：

| 字段 | calc-pro（calcpro-001） | calculator（calculator-001） |
|---|---|---|
| `expected_skill` | `calc-pro` | `calculator` |
| `expected_script` | `stats.py` | `calc.py` |
| `prompt` | 「**请使用 calc-pro 技能**计算 20 个数的总体标准差」 | 「**Please use the calculator skill**」 |
| `expected_behavior` | 读 SKILL.md → 执行 stats.py → 报告 ≈12.0337 | 读 SKILL.md → 执行 calc.py → 报告 14 |

其目的：让 baseline（无 skill）在结构上难以达成 goal，从而测出「该 skill 相对 baseline 的增益」。

**② 公共用例（冗余对比用）——不预设任何 skill。**

公共用例 `shared/arithmetic`（9 例）为 **neutral 格式**，不含 `expected_skill` / `expected_script` / `evaluated_skill` 字段，只有 `id / question / ground_truth / expected_behavior`（**纯结果断言**），例如：

```json
{ "id": "shared-001",
  "question": "计算表达式 (100 - 25) / 3 的结果。",
  "ground_truth": "25",
  "expected_behavior": ["最终结果应为 25"] }
```

题目只落在两者**能力的交集**（基础算术 + 单位换算），断言只验证**最终数值**，不规定「必须用哪个脚本」。其目的：回答「两个 skill 在都能完成的任务上，谁更省资源」。

**③ 公共用例公平性的四重保障。**

1. **neutral 格式（无 `expected_skill`）**——评估器不会因「用了 A 没用 B」而判失败，双方起点一致；
2. **只取能力交集**——统计/财务等 calc-pro 独有、calculator 覆盖不了的任务不放进来，避免天然偏袒一方；
3. **纯结果断言**——`expected_behavior` 只断言最终数值，`goal_accuracy` 对双方公平可比（实测均 1.0）；
4. **同一份用例喂给两个 skill**（`--eval-source` 共享用例复制）——双方面对字节级相同的题目，横向差异只能来自 skill 自身的 token/耗时/轮数成本，而非题目不同。

**④ 与评判指标改动的联动。**

正因 neutral 用例下无 `expected_skill`，评估结果中的 `skill_activated` 为 `None`（not_applicable）。因此「是否调用了 skill」**在冗余对比中不能作为胜负维度**，只能作为**增益评测**的一道 gate（`activated=False → insufficient`）。这正是增益轨将「结果一致 + token 输入/输出 + 耗时 + 轮数」作为效率依据、而不拿 skill 激活当对比维度的根本原因。
