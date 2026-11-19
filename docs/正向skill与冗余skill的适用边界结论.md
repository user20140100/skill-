# 正向 Skill 与冗余 Skill 的适用边界结论

> 记录时间：2026-11-18
> 来源：Tier3 沙盒 A/B 双臂评测（SkillEvaluator）与冗余对推荐链路
> 关联报告：[`reports/recommendation.md`](../reports/recommendation.md)

## 一、结论摘要

| 任务类型 | 正向 skill（calc-pro） | 冗余 skill（calculator） | 更优方 |
|---|---|---|---|
| 特化任务（统计 / 财务等） | 增益显著（lift +29.6pp） | 无法覆盖（能力范围外） | **calc-pro** |
| 泛化任务（基础算术 / 单位换算） | 结果正确但成本高 | 结果正确且省 token、耗时短 | **calculator** |

一句话结论：

> **冗余 skill 更适用于处理泛化任务，正向 skill 更适用于处理特化任务。**
> 这与两者「泛化精简」与「专业化扩展」的设计思路相吻合，体现了该评测体系的合理性。

## 二、评测对象与设计思路

| | calc-pro（正向 skill） | calculator（冗余 skill） |
|---|---|---|
| 定位 | 专业计算套件，在官方 calculator 基础上**扩展**统计 + 财务 | 基础计算器，仅算术表达式 + 单位换算 |
| 脚本结构 | 4 个脚本模块化依赖链（calc.py → stats.py / finance.py → cli.py） | 单脚本（calc.py） |
| SKILL.md 篇幅 | 长（覆盖三类任务、命令格式、依赖关系） | 短（精简指令） |
| 设计取向 | **特化**：针对 LLM 心算易错的精确数值任务 | **泛化**：覆盖最通用、最基础的计算需求 |

两者在「基础算术 + 单位换算」能力上高度重叠（Tier2 相似度 0.913，HIGH_SIMILARITY），构成冗余对。

## 三、两层评测框架

评测体系通过两条不同的对比路径，分别回答两个不同问题：

1. **增益评测（with-skill vs baseline）**
   对某个 skill 的**专项用例**，比较「使用该 skill 的 agent」与「不使用该 skill 的 agent（基线）」两个分支，衡量该 skill 相对基线带来的**增益（lift）**。

2. **冗余对比（with-skill A vs with-skill B）**
   在**公共用例**（两者都能处理的交集任务）上，比较「分别使用两个 skill 的 agent」分支，衡量两者在结果与效率上的**横向差异**。

两者不可混为一谈：增益评测回答「这个 skill 有没有用」，冗余对比回答「两个 skill 用哪个更划算」。

## 四、实测数据

### 4.1 正向 skill 专项任务（特化）—— 增益显著

对 calc-pro 的专项用例（统计 + 财务，共 3 个特化任务）跑完整 with/without 双臂对照：

| 指标 | baseline（无 skill） | with calc-pro | 增益 |
|---|---:|---:|---:|
| Overall | 70.4% | 100.0% | **+29.6pp** |
| Effectiveness | 11.1% | 100.0% | +88.9pp |
| Goals met | 0/3 | 3/3 | +3 |

- **Skill Lift：+0.2963（+29.63 个百分点）**
- 专项任务样例：20 个数据的总体标准差（`stats.py`）、贷款月供（`finance.py`）等——这些任务基线 LLM **心算无法可靠完成**（Goals met 0/3），借助 calc-pro 的统计/财务脚本后达到 100%。
- run_id：`20261118_114431_1_266ece03707b`，agent=opencode，model=openai/qwen3.8-flash。

> 结论：正向 skill 在**特化任务**上相对基线体现了**明显的增益**。

### 4.2 公共任务（泛化）—— 结果等效、效率分出胜负

公共用例 `shared/arithmetic`（9 个基础算术 + 单位换算任务，两者能力交集），横向对比 with-calc-pro vs with-calculator：

| 维度 | calc-pro | calculator | 更优 |
|---|---|---|---|
| goal_accuracy | 1.0 | 1.0 | —（持平） |
| prompt_tokens（输入） | 75358 | 71439 | calculator |
| completion_tokens（输出） | 349 | 256 | calculator |
| duration_seconds（耗时） | 414.6 | 339.7 | calculator |
| rounds（轮数） | 12 | 12 | —（持平） |

- 增益结论：**efficiency_better → calculator**（结果等效下，calculator 更省 token、耗时更短）。
- run_id：calc-pro `20261118_133129_1_6b6705a1a030`；calculator `20261118_133911_1_490f7d2858db`。

> 结论：在**泛化任务**上，冗余 skill（calculator）的**效率与成本更优**。

## 五、核心结论

1. **正向 skill（calc-pro）适合特化任务**：在统计、财务等超出基础能力、LLM 心算易错的专业场景，它带来显著增益（lift +29.6pp）。

2. **冗余 skill（calculator）适合泛化任务**：在基础算术、单位换算等通用场景，它能以更少的 token 开销与更短的耗时完成同样的结果（结果均 1.0，效率更优）。

3. **两者互补而非互斥**：正向 skill 的价值在「能力边界扩展」，冗余 skill 的价值在「通用任务成本控制」。这与两者的设计思路一致——calc-pro 是 calculator 的**专业化扩展**，calculator 是**精简泛化的基础能力**。

4. **评测体系合理性**：三层评估（Tier1 安全 / Tier2 语义去重 / Tier3 A/B 双臂）能够同时捕获「增益」（with vs without）与「效率」（A vs B）两个正交维度，从而区分「特化收益」与「泛化成本」，得到符合设计意图的结论。

## 六、评测设计说明

本节说明增益评测与冗余对比所依赖的**两类测试用例的构建思路**，以及公共用例的公平性保障。

### 6.1 特化用例（增益评测用）——为指定 skill 量身定制

特化用例通过 `expected_skill` / `expected_script` 强绑定被测 skill，goal 与 behavior 都定义在「使用该 skill 的特定工作流」上，且只覆盖该 skill 独有的能力：

| 字段 | calc-pro（calcpro-001） | calculator（calculator-001） |
|---|---|---|
| `expected_skill` | `calc-pro` | `calculator` |
| `expected_script` | `stats.py` | `calc.py` |
| `prompt` | 「**请使用 calc-pro 技能**计算 20 个数的总体标准差」 | 「**Please use the calculator skill**」 |
| `expected_behavior` | 读 SKILL.md → 执行 stats.py → 报告 ≈12.0337 | 读 SKILL.md → 执行 calc.py → 报告 14 |

其目的：让 baseline（无 skill）在结构上难以达成 goal，从而测出「该 skill 相对 baseline 的增益」。

### 6.2 公共用例（冗余对比用）——不预设任何 skill

公共用例 `shared/arithmetic`（9 例）为 **neutral 格式**，不含 `expected_skill` / `expected_script` / `evaluated_skill` 字段，只有 `id / question / ground_truth / expected_behavior`（**纯结果断言**），例如：

```json
{ "id": "shared-001",
  "question": "计算表达式 (100 - 25) / 3 的结果。",
  "ground_truth": "25",
  "expected_behavior": ["最终结果应为 25"] }
```

题目只落在两者**能力的交集**（基础算术 + 单位换算），断言只验证**最终数值**，不规定「必须用哪个脚本」。其目的：回答「两个 skill 在都能完成的任务上，谁更省资源」。

### 6.3 公共用例公平性的四重保障

1. **neutral 格式（无 `expected_skill`）**——评估器不会因「用了 A 没用 B」而判失败，双方起点一致；
2. **只取能力交集**——统计/财务等 calc-pro 独有、calculator 覆盖不了的任务不放进来，避免天然偏袒一方；
3. **纯结果断言**——`expected_behavior` 只断言最终数值，`goal_accuracy` 对双方公平可比（实测均 1.0）；
4. **同一份用例喂给两个 skill**（`--eval-source` 共享用例复制）——双方面对字节级相同的题目，横向差异只能来自 skill 自身的 token/耗时/轮数成本，而非题目不同。

### 6.4 与评判指标改动的联动

正因 neutral 用例下无 `expected_skill`，评估结果中的 `skill_activated` 为 `None`（not_applicable）。因此「是否调用了 skill」**在冗余对比中不能作为胜负维度**，只能作为**增益评测**的一道 gate（`activated=False → insufficient`）。这正是增益轨将「结果一致 + token 输入/输出 + 耗时 + 轮数」作为效率依据、而不拿 skill 激活当对比维度的根本原因。
