# Agent Skill 批量安全审计报告

> 扫描目录：`library-demo`　生成时间：2026-11-18 22:06:35

## 1. 总览

- 扫描 Skill 数：**5**；安全通过：**2**；存在高危：**3**；未评估：0；含沙盒对照：1

| Skill | 分类 | 安全评级 | 风险分 | 高危 finding | 沙盒对照 |
|---|---|---|---|---|---|
| `android-log-analysis` | unknown | 高危 | 53 | 4 | 无 |
| `calculator` | unknown | 安全 | 0 | 0 | 有 |
| `code-review` | 冗余 | 高危 | 0 | 1 | 无 |
| `es-log-query` | 安全 | 高危 | 36 | 8 | 无 |
| `requirement-spec` | 冗余 | 安全 | 0 | 0 | 无 |

## 2. 高危风险项（过滤）

### `android-log-analysis`

- [skillspector:HIGH] decode_xlog_py2.py (partial)
- [skillspector:HIGH] Output Rules
- [tier1:HIGH] System Prompt Leakage: Output Rules
- [tier1:HIGH] analysis-evasion: decode_xlog_py2.py (partial)

### `code-review`

- [tier1:HIGH] Non-placeholder email address: git@gitlab.gz.cvte.cn

### `es-log-query`

- [skillspector:HIGH] .env
- [skillspector:HIGH] .env
- [skillspector:HIGH] .env
- [skillspector:HIGH] .env
- [skillspector:HIGH] .env
- [skillspector:HIGH] .env'
- [tier1:HIGH] Privilege Escalation: .env 
- [tier1:HIGH] Privilege Escalation: .env'

## 3. 沙盒对比（Tier3 A/B）

| Skill | overall (with/without) | goal_acc (with/without) | lift(goal) | pass@k (with/without) | 状态 |
|---|---|---|---|---|---|
| `calculator` | 1.000 / 1.000 | 1.000 / 1.000 | 0.000 | 1.000 / 1.000 | succeeded |

## 4. 明细

- **android-log-analysis**（library-demo/android-log-analysis）：评级 高危，风险分 53，C/H/M/L = 0/2/7/11
- **calculator**（library-demo/calculator）：评级 安全，风险分 0，C/H/M/L = 0/0/6/7
- **code-review**（library-demo/code-review）：评级 高危，风险分 0，C/H/M/L = 0/1/5/10
- **es-log-query**（library-demo/es-log-query）：评级 高危，风险分 36，C/H/M/L = 0/6/8/10
- **requirement-spec**（library-demo/requirement-spec）：评级 安全，风险分 0，C/H/M/L = 0/0/5/17
