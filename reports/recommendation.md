# 冗余 Skill 推荐报告

> 生成时间：2026-11-18 22:08:33

## 1. 冗余检测

| 候选 skill | 命中 catalog skill | 相似度 | 分类 |
|---|---|---|---|
| calc-pro | calculator | 0.913 | HIGH_SIMILARITY |

## 2. 评估证据

| Skill | goal_acc | overall | pass@k | lift(goal) | prompt_tok | completion_tok | 时间(s) | 轮数 | 安全 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| calc-pro | 1.000 | 1.000 | 1.000 | 0.000 | 75358 | 349 | 414.6 | 12 | safe | succeeded |
| calculator | 1.000 | 1.000 | 1.000 | 0.000 | 71439 | 256 | 339.6 | 12 | safe | succeeded |

## 3. 安全结论（完整 Tier1）

- **结论**：两者均安全

两者均通过完整 Tier1 安全审查（SkillSpector + SkillEvaluator Tier1），安全维度无差异，无需从安全角度二选一。

## 4. 增益结论（共享用例）

- **结论**：结果相当、效率更优
- **增益更优**：calculator
- **可比性**：不满足（结论仅供参考）

两者结果相当，但「calculator」在效率维度综合领先（token 输入 / token 输出 / 执行时间 / 执行轮数），综合增益更优。

### 多维增益对比

| 维度 | calc-pro | calculator | 更优 |
|---|---|---|---|
| result | 1.0 | 1.0 | — |
| prompt_tokens | 75358 | 71439 | b |
| completion_tokens | 349 | 256 | b |
| duration_seconds | 414.613 | 339.65 | b |
| rounds | 12 | 12 | — |

## 5. 决策说明

> 以上安全结论与增益结论彼此独立，系统**不合成单一最终推荐**。
> 请结合自身使用场景，在两个维度间自行权衡选择（P7）。

## 6. 综合叙述（LLM 润色）

两者均通过完整 Tier1 安全审查（SkillSpector + SkillEvaluator Tier1），安全维度无差异，无需从安全角度二选一。

两者结果相当，但「calculator」在效率维度综合领先（token 输入 / token 输出 / 执行时间 / 执行轮数），综合增益更优。

## 8. 复现信息

- **calc-pro**：run_id=20261118_133129_1_6b6705a1a030，agent=opencode，model=openai/qwen3.8-flash，attempts=1，dataset_digest=sha256:0d25dd059dd17e7fcfe2b069cb5faa794c528ab87a8cd1c85cdc03a193e03d2a
- **calculator**：run_id=20261118_133911_1_490f7d2858db，agent=opencode，model=openai/qwen3.8-flash，attempts=1，dataset_digest=sha256:854c12951908f16b46d645ba77312c154abf802b30597ec84f2b1a1a5f858ce7
