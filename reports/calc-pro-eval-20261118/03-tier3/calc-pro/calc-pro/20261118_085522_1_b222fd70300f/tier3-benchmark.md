> **Tier 3: No complete agent result**

# Skill Benchmark: calc-pro

Publication: **NOT ASSESSED**. This report covers Tier 3 only; Tiers 1 and 2 are not covered by this report.
The verdict describes with-skill quality; lift is a separate baseline comparison.

> Budget: no limits configured

## Evaluation Metadata

- Skill: `calc-pro`
- Source digest: `sha256:cc5cdc54ca32e569265a873cccdb228d699c8fcca1cda220672b03ea27a1b679` (skill-evaluator-source-tree/2)
- Evaluation date: 2026-11-18
- Evaluator version: `0.9.0`
- Evaluated source: not recorded (not supplied by the orchestration input)
- Evaluated source revision: not recorded (not supplied by the orchestration input)
- Evaluator container revision: not recorded (not supplied by the orchestration input)
- Agents: Opencode (`openai/qwen3.8-flash`)
- Tasks: 3 evaluation tasks (3 positive)
- Dataset digest: `sha256:87945e5433576f3e44313bdb7c479700601ae1579ff93547a96a1f3a9a1f975e` (skill-evaluator-dataset-snapshot/1)
- Tier 3 run ID: `20261118_085522_1_b222fd70300f`
- Baseline: fresh
- Attempts per task: 1
- Environment: `docker`
- Tier 2 evidence: required for publication
- Tier 3 evidence: required for publication

Each task attempt ran in its own isolated Docker container.

## What This Report Answers

The three-tier evaluation checks whether the skill:

- is safe to use;
- produces correct answers;
- is discovered and activated when needed;
- helps the agent complete the user's goal and expected workflow; and
- avoids wasted skill and tool usage.

## Results at a Glance

| Measure | Opencode (Baseline → Skill Uplift) |
|---|---:|
| Overall | 100.0% — baseline incomplete (1 of 3 attempts scored); uplift unavailable |
| Required checks passed | 3/3 \| N/A \| N/A |
| Goals met | 3/3 \| N/A \| N/A |
| Security clean | 3/3 \| N/A \| N/A |
| Security | 100.0% — baseline incomplete (1 of 3 attempts scored); uplift unavailable |
| Correctness | 100.0% — baseline incomplete (1 of 3 attempts scored); uplift unavailable |
| Discoverability | 100.0% — baseline incomplete (1 of 3 attempts scored); uplift unavailable |
| Effectiveness | 100.0% — baseline incomplete (1 of 3 attempts scored); uplift unavailable |
| Efficiency | 100.0% — baseline incomplete (1 of 3 attempts scored); uplift unavailable |

**How to read this table:** baseline is the same task attempted without the target skill. Scores are rounded to one decimal; threshold-adjacent values use additional precision so their displayed band matches the verdict. Uplift is `skill score - baseline score`, computed from those displayed scores and shown in percentage points.

Example: `47.0% → 92.0% (+45.0 points)` means the skill-assisted run scored 92.0%, 45.0 percentage points above its 47.0% no-skill baseline.

**Not scored** means a signal the dimension needs produced no score, and **Not applicable** means no eval case gave its signals anything to judge; neither is a score of zero. Scoring Methodology below explains each dimension and where its evidence comes from.

### Agent coverage

- Opencode: baseline incomplete (1 of 3 attempts scored; first failure: runtime error). The agent and the Tier 3 run are marked failed. Baseline and uplift are not reported for this agent.

## Token Usage

Measured agent token usage. It is not scored and changes no score or verdict. Tokens are prompt plus completion; prompt tokens include cached tokens, which are not added again. Attempts that failed before scoring are counted. A partial total covers only the attempts with token counts; nothing is estimated. Change is with skill minus baseline, as a share of the baseline, and needs complete counts for the same attempts in both arms.

| Agent | Case | With skill | Baseline | Change | Measured attempts |
|---|---|---:|---:|---:|---|
| Opencode | All cases | 85,329 | 23,393 (partial) | N/A | skill 3/3; baseline 1/3 (2 unscored) |

Measured attempts: attempts with token counts, of those expected, in each arm. Unscored attempts failed before scoring.

- Opencode: Baseline token counts cover 1 of 3 attempts. No change: baseline incomplete (1 of 3 attempts scored).

<details>
<summary>Show token usage per case</summary>

| Agent | Case | With skill | Baseline | Change | Measured attempts |
|---|---|---:|---:|---:|---|
| Opencode | calcpro-001 | 34,630 | N/A | N/A | skill 1/1; baseline 0/1 (1 unscored) |
| Opencode | calcpro-002 | 25,249 | 23,393 | N/A | skill 1/1; baseline 1/1 |
| Opencode | calcpro-003 | 25,450 | N/A | N/A | skill 1/1; baseline 0/1 (1 unscored) |

</details>

## Tier Status

| Tier | Purpose | Status | Evidence |
|---|---|---|---|
| Tier 1 | Static validation | **NOT COVERED** | Outside this report's Tier 3 scope |
| Tier 2 | Semantic deduplication | **NOT COVERED** | Outside this report's Tier 3 scope |
| Tier 3 | Live agent evaluation | **FAILED** | 1 validator(s); 0 finding(s); Opencode baseline incomplete (1 of 3 attempts scored) |

## Findings and Observations

<details>
<summary>Show detailed findings and successful checks</summary>

- No findings or successful-check details were recorded.

</details>

## Scoring Methodology

<details>
<summary>Show dimension definitions, source signals, and thresholds</summary>

| Dimension | What it measures | Scored signals | Evidence source | Baseline in this run |
|---|---|---|---|---|
| Security | Is it safe to use? Avoids unsafe operations, secret leakage, and unauthorized access. | `security` (100%) | Deterministic checks of the agent's commands and outputs | Not available |
| Correctness | Is the answer correct? Produces factually accurate output. | `accuracy` (100%) | An LLM judge comparing the final answer with the reference answer | Not available |
| Discoverability | Was the right skill loaded when needed? Activates the right skill when relevant; ignores unrelated skills. | `skill_execution` (100%) | Deterministic checks of the agent's trajectory | Not available |
| Effectiveness | Did the skill help complete the task? Reaches the user's goal and follows the expected behavior. | `goal_accuracy` (50%) + `behavior_check` (50%) | An LLM judge of whether the user's goal was met; an LLM judge of the expected workflow | Not available |
| Efficiency | Did it avoid wasted tool or skill usage? Uses the skill and tools productively without wasted work. | `skill_efficiency` (100%) | Deterministic checks of the agent's trajectory | Not available |

- Dimension bands: PASS at 50% or above; NEUTRAL from 40% to below 50%; FAIL below 40%.
- Overall Tier 3 lift: PASS at +5 points or more; FAIL at -10 points or less; values between those bands are NEUTRAL.
- Overall verdict: PASS only when every configured dimension passes for at least one supported agent, with no with-skill case failing a required goal-accuracy or security check. A scored unmet goal or security issue in any attempt fails its case and that agent's quality verdict, even if all dimensions pass. Baseline-arm required-check failures do not change this quality verdict. Lift is reported as diagnostic evidence and does not override this gate.
- The 50% attempt pass threshold is a separate per-task gate; it is not the dimension pass threshold.
- Effectiveness is the equal-weight mean of goal completion (`goal_accuracy`) and expected workflow adherence (`behavior_check`).
- Token efficiency is a separate report-only signal. It does not change a dimension score or the overall verdict.
- The baseline is the same eval cases run by the same agent without the skill. Every dimension is compared with it when the baseline arm ran and scored that dimension.

Which number answers which question:

- **Overall verdict** (top of this card): whether the evidence supports publishing the skill. It needs every required tier, not only Tier 3 scores.
- **Dimension score**: how well the agent did on one question above when it had the skill, from 0% to 100%.
- **Overall** row: when comparable baseline scores are available, the two scores used for published Skill Lift, on the metrics and cases both arms scored comparably. Otherwise, the available arm Overall score(s). These can differ from the headline with-skill score.
- **Uplift**: the displayed skill score minus the displayed no-skill baseline score. Published Skill Lift compares Overall only on the metrics and cases both arms scored, so it can differ. Uplift does not set the verdict.
- **pass@k** (HTML report and `pass_at_k_lift.json`): the share of eval cases with at least one passing attempt out of k. It measures how repeatable success is, separately from the dimension scores.
- **Quality Score** (Tier 1, out of 100): a static review of the skill's files. It is not an input to any Tier 3 score or uplift.

Signals present in this run:

- `security` (Security): unsafe operations, secret leakage, and unauthorized access.
- `skill\_execution` (Skill Execution): whether the expected skill was found and executed.
- `skill\_efficiency` (Skill Efficiency): routing quality, workspace-aware skill reads, and productive tool use.
- `accuracy` (Accuracy): final-answer correctness against the reference answer.
- `goal\_accuracy` (Goal Accuracy): whether the user's goal was achieved.
- `behavior\_check` (Behavior Check): whether the expected workflow behavior was followed.

</details>

## Freshness

Regenerate this benchmark when the skill, evaluation dataset, target agent/model, evaluator version, environment, or scoring policy changes.
