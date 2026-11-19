# 冗余 Skill 推荐功能需求文档

> 功能名称：冗余冲突 Skill 评估与双结论更优 Skill 推荐
> 所属课题：AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统
> 依据：`docs/杨宇涵 实习课题.md` 阶段二要求 + 三层评估（SkillEvaluator）实践结论
> 状态：开发依据稿（v1.2，2026-11-18；新方案：双结论推荐 + 完整 Tier1 安全审查 + catalog 安全预扫描）

---

## 1. 背景与目标

### 1.1 课题原文要求

> 针对冗余冲突的 skill，评估后向用户推荐更优的 skill，可联网进行搜索相关 skill 供用户查看选择

### 1.2 目标

当系统（Tier2 语义去重）检测到某个 skill 与当前 skill 存在高重复度（冗余冲突）时：

1. 对冲突双方进行**可比的**行为增益评估（Tier3 沙盒对照实验）；
2. 对冲突双方进行**完整 Tier1 安全审查**（SkillSpector 静态安全扫描 + SkillEvaluator Tier1 质量/安全/Schema 静态检查）；
3. 依据增益结论与安全结论，**分别**给出「安全角度推荐」与「增益效果推荐」两个结论；
4. 将两个结论一并呈现，**最终"哪个更优"的决策交由用户**（系统不强行合成单一 verdict）；
5. 支持**联网搜索**外部/公司库内的相关 skill，作为补充候选供用户查看、选择；
6. 输出一份**可复现、可演示**的推荐报告。

### 1.3 设计原则（来自三层评估实践，必须遵守）

- **P1 可比性优先**：两个 skill 的增益结论只有在**同一组 eval case、同一 grader、同一 agent、同一模型、同一 attempts** 下才可比较。禁止用各自独立数据集上的 Skill Lift 绝对值直接比大小。
- **P2 先筛后评**：Tier2 去重便宜、只读本地，必须先跑并筛出候选，再对少量候选跑 Tier3（Tier3 每 skill 双臂约 10–30 分钟）。安全审查同样便宜，可对 catalog 全量前置预处理。
- **P3 规则确定性**：硬性门槛、安全评级、排序与结论类型由**确定性规则**完成；大模型只负责报告叙述与相近分数的 tie-break，且必须引用证据字段，不得覆盖硬规则。
- **P4 相似 ≠ 冗余**：Tier2 的 `SIMILAR` 是 advisory 级；结论必须允许"替换 / 合并 / 保留两者"，不得强制二选一。
- **P5 用例中立**：共享用例的 grader 只判任务产出，不得把"必须调用某 skill 的脚本"写入 ground truth（否则 baseline 天然 0 分，测量失真）。
- **P6 安全审查完整化**：安全审查 = **完整 Tier1 流程 = SkillSpector 静态安全扫描 + SkillEvaluator Tier1**，二者并列；任何一方检出的 critical/high 问题都计入安全结论。
- **P7 决策权交用户**：系统只输出安全 / 增益两个维度的独立结论，**不合成单一 verdict**；"哪个更优"由用户结合自身场景决定。两条结论可能不一致，属正常现象。

---

## 2. 功能范围与非目标

### 2.1 范围内

- 冗余对检测（复用 SkillEvaluator Tier2）
- **catalog 安全预扫描**（对 catalog 内每个 skill 跑完整 Tier1，报告按 skill 索引存储）
- 共享用例 Tier3 增益评估
- **完整 Tier1 安全审查**（SkillSpector + SkillEvaluator Tier1）
- 证据归一化与**双结论**推荐判定（规则 + LLM 报告）
- 联网搜索补充候选（公司库 `cskills find` + 外部库）
- 推荐报告生成

### 2.2 非目标（本期不做）

- 自动修复/自动合并冗余 skill（属阶段四加分项，另立）
- 对全部库内 skill 的实时大规模重评（成本不可控）
- 训练/微调专用推荐模型
- 自动合成一个"加权总分"并据此强制选一个 skill（与 P7 相悖）

---

## 3. 术语与定义

| 术语 | 定义 |
|---|---|
| 正向 skill | 功能单一、无风险、作为基准或推荐候选的 skill（对应数据集 `positive/`） |
| 冗余/冲突 skill | 公司库快照中与正向 skill 语义高度相似、被 Tier2 命中的 skill（对应 `library-20261118/<组>/<skill>`，由用户从相似列表选定） |
| 冗余对 | Tier2 判定相似度 ≥ 0.75 的一对 skill |
| 候选 skill | 进入 Tier3 评估的 skill（正向 + 冗余对成员） |
| 增益 / Skill Lift | 同一 skill 相对其 baseline 臂的 Overall 差值（`lift.json`） |
| 多维增益 | 综合「结果 / 流程 / token 消耗 / 执行时间 / 执行轮数」5 个维度对两个 skill 增益的比较方式 |
| 可比分数 | 候选 skill 在**同一组 case** 上的 with-skill 分数（`goal_accuracy` / `overall` / `pass@k`） |
| **完整 Tier1 安全审查** | 由 **SkillSpector**（静态安全扫描，产出 `risk_assessment` + `issues[]`）与 **SkillEvaluator Tier1**（质量/Schema/安全静态检查，产出 `overall_status` + `severity_counts`）两部分构成的安全审查 |
| **安全结论** | 依据完整 Tier1 安全审查，对"哪个 skill 更安全"给出的独立结论 |
| **增益结论** | 依据共享用例 Tier3 增益评估，对"哪个 skill 增益更优"给出的独立结论 |
| 双结论推荐 | 报告同时输出安全结论与增益结论、不合成单一 verdict 的推荐形态 |
| 推荐报告 | 面向用户的最终结论文档（安全结论 + 增益结论 + 证据 + 候选） |

---

## 4. 总体流程

```
输入：正向 skill + 冗余 skill（用户指定，或由 Tier2 全量扫描自动发现）
                    │
        ┌───────────▼───────────┐
        │ 阶段零 catalog 安全预扫描 │  对 catalog 内每个 skill 跑完整 Tier1，
        └───────────┬───────────┘  报告按 skill 索引存储（一次性，可复用）
                    │
        ┌───────────▼───────────┐
        │ 阶段一 冗余检测（Tier2）  │  cheap，只读，先跑
        └───────────┬───────────┘
                    │ 相似对 + 分类 + 分数（matches / SIMILARITY findings）
        ┌───────────▼───────────┐
        │ 相似度 ≥ 0.75?          │──否──> 结束：无冗余，不触发推荐（记录 SIMILAR 以下为 INFO）
        └───────────┬───────────┘
                    │ 是
        ┌───────────▼───────────┐
        │ 阶段二 共享用例 Tier3    │  只对 top-N（默认 ≤3）候选；每 skill 各跑 with/baseline 双臂
        └───────────┬───────────┘
                    │ result.json / lift.json / pass_at_k_lift.json
        ┌───────────▼───────────┐
        │ 阶段三 证据归一化        │  提取可比分数 + 完整 Tier1 安全结论 + token 成本
        └───────────┬───────────┘
                    │ 结构化证据对象（增益证据 + 安全证据）
        ┌───────────▼───────────┐
        │ 阶段四 双轨规则判定      │  安全轨结论 + 增益轨结论（确定性规则，不合成单一 verdict）
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │ 阶段五 联网搜索候选      │  cskills find / 外部库；默认仅 Tier1+描述级比对，未实测标注
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │ 阶段六 LLM 生成推荐报告  │  引用证据字段，输出双结论 JSON + Markdown
        └───────────────────────┘
```

---

## 5. 需求分解

### 5.0 阶段零：catalog 安全预扫描（前置，可复用）

- 目的：保证 catalog 中存入的每个 skill 均已通过完整 Tier1 安全审查，且审查报告已按 skill 索引存储，供后续 `judge` 阶段直接读取。
- 范围：对 `catalog`（公司库选定的 skill + 冗余 skill calculator）逐个跑完整 Tier1：
  ```bash
  # SkillSpector 静态安全扫描
  docker compose run --rm skillspector scan /scan/<skill> --no-llm
  # SkillEvaluator Tier1（质量/Schema/安全静态检查）
  docker compose run --rm skillevaluator tier1 /skills/<skill> --no-llm
  ```
- 存储：审查报告按 `<skill相对路径>` 索引落盘（如 `reports/security/<组>_<skill>/skillspector.json` 与 `skillevaluator-tier1.json`），并在 catalog 侧记录每个 skill 的扫描时间与 skill digest，保证安全结论可追溯、可复现、双方用同一扫描器同一配置。
- 变更触发：skill 内容变更（digest 变化）→ 该 skill 的安全报告失效，需重新扫描。

### 5.1 阶段一：冗余检测（复用 Tier2，对公司库全量比对）

- 命令（`detect` 子命令封装，dry-run 打印 / `--run` 执行）：
  ```bash
  # ① 预先对公司库快照建 embedding catalog（一次性）
  skillevaluator similarity-check /skills/library-20261118 --save-catalog /app/reports/company-catalog.json --full-body
  # ② 正向 skill 对公司库 catalog 语义比对
  skillevaluator similarity-check /skills/positive/<正向> --catalog /app/reports/company-catalog.json \
    --output-dir /app/reports/company-match/<正向> --report json --full-body
  ```
  CLI：`python -m skill_recommend detect --base positive/<正向> --library library-20261118 [--threshold 0.75] [--run]`
- 输出解析：读 `skillevaluator-similarity.json`，提取 `category="SIMILARITY"` finding 的 `entry_a`（正向 skill）、`entry_b`（命中的公司库 skill）、`path_b`（库内相对路径）、`score`、`classification`（`SIMILAR`/`HIGH_SIMILARITY`/`EXACT_DUPLICATE`）。
- 触发条件：`score ≥ 0.75`（`--threshold` 默认值）；`LOOSELY_RELATED`（0.50–0.75）与 `DISTINCT` 不进入候选列表。
- `--full-body` 必须开启（否则仅比较 name+description，易漏"描述不同但指令重复"）；catalog 与查询须同 mode。
- 该环节同时承担「联网搜索相关 skill 供用户查看选择」：相似列表即搜索候选，用户从中**参数式选定**一个冗余 skill（终端命令，无可视化页面）。

### 5.2 阶段二：共享用例 Tier3 评估

- 用例准备：一套 skill 中立的共享任务集 `evals/evals.json + evals/files/`（同一份），grader 只判任务产出。两个候选 skill 目录各放一份同内容副本；由 `pipeline --eval-source <共享用例skill>` 自动复制（只拷 `evals.json` + `files/`，跳过 `results/` 运行产物，保证 `dataset_digest` 一致）。
- **共享用例设计约束（新增）**：用例须保证 grader 只判"任务产出"（P5），且**不偏袒任一 skill**。因 calc-pro 是 calculator 的**能力超集**（多 stats/finance），共享用例**只取双方能力交集**——复杂算术（嵌套括号/运算优先级/乘方/取模/一元负号）、百分比、单位换算；**不加入** stats/finance 等超集任务（否则会偏袒 calc-pro）。两者底层 `calc.py` 行为等价，交集用例对双方公平。
  - 用例要求"复杂"而非"简单"：避免只给 `2 + 3 * 4` 这类一眼可心算的题，用多运算符、括号嵌套、乘方、取模、百分比、多单位换算的组合，使 LLM 不借助 skill 脚本难以可靠心算。
  - 预期：双方在交集用例上均能得出正确结果 → 结果相当 → 进入多维综合（流程 / token / 时间 / 轮数），可能判"结果相当但综合增益更优"或"两者增益相当、均可"（见 6.3）。
- CLI：`python -m skill_recommend pipeline --base positive/<正向> --candidate library-20261118/<组>/<选定冗余skill> --eval-source <共享用例skill> [--run]`。
- 命令（每候选各跑一次）：
  ```bash
  skillevaluator tier3 evaluate <skill路径> --agents opencode --model openai/<模型> \
    --n-attempts 1 --max-cases 1 --timeout-multiplier 3 \
    --results-dir ./reports/reco-results
  ```
- 结果落盘：`<results-dir>/<skill-name>/<run>/<agent>/result.json`、`lift.json`、`pass_at_k_lift.json`；用 `run_config.json + result.json` 齐全且无 failed/error 的最新 run。
- 可选替代（严格共基准）：`skillevaluator tier3 interact <A> <B> --eval-source <共享数据集skill> --metric goal_accuracy`，同源跑 baseline/A/B/AB，附 interaction 项。
- 成本约束：单次双臂 10–30 分钟；只评 top-N（默认 3）。

### 5.3 阶段三：证据归一化

对每个候选 skill 提取如下证据对象：

| 字段 | 来源 |
|---|---|
| `skill_name` / `run_id` | run 目录 |
| `goal_accuracy` / `overall` / `pass@k`（with-skill） | result.json / lift.json |
| `skill_execution` / `skill_efficiency`（流程） | result.json `agents.<agent>.with_skill` |
| `prompt_tokens`（输入）/ `completion_tokens`（输出）/ `total_tokens` | result.json `token_usage...with_skill.totals` |
| `duration_seconds`（执行时间） | result.json 顶层 |
| `rounds`（执行轮数） | trajectory.json `len(steps)`（各 trial 之和/均值） |
| `skill_lift`（参考，非主判据） | lift.json |
| `dataset_digest` / `agent` / `model` / `n_attempts` | run_config.json（用于证明可比性） |
| **`security`（结构化，见 7.2）** | 阶段零的完整 Tier1 安全审查报告（SkillSpector + SkillEvaluator Tier1） |

### 5.4 阶段四：双轨规则判定

见第 6 节。

### 5.5 阶段五：联网搜索候选

> 公司库内的「相似 skill」搜索已在**阶段一**通过 Tier2 对公司库 catalog 全量比对完成（见 5.1）。本节为**补充渠道**，用于扩展候选范围。

- 公司库关键词：`cskills find <关键词>`（如 commit / git / changelog / code-review）；`cskills info <name>` 取描述与文件结构。
- 外部库：agentskills.io、GitHub（可选，需网络可达）。
- 语义复核：`judge --company-report <相似报告>` 复用阶段一的 Tier2 相似报告，把命中项作为带 embedding 分数的候选（`source="company-library"`），与关键词候选合并去重。
- 对搜索到的候选：默认只做 Tier1 + 描述级相似比对，标注"未实测"；用户选中后才用共享用例补跑 Tier3（懒评估）。

### 5.6 阶段六：报告生成（双结论）

- LLM 输入：阶段三的归一化证据对象（增益证据 + 安全证据）+ 阶段四的双轨规则结论 + 阶段五候选清单（结构化）。
- LLM 职责：分别润色「安全结论」与「增益结论」的叙述、解释相近分数的选择、归纳外部候选；**不得新增事实、不得推翻规则结论、不得擅自合成单一"最终推荐"**。
- 输出：结构化 JSON（供程序）+ Markdown（供人阅读），两者字段一致，均包含 `security_recommendation` 与 `gain_recommendation` 两个结论。

### 5.7 CLI 接口（参数式选择，无可视化页面）

| 命令 | 作用 | 关键参数 |
|---|---|---|
| `detect` | 阶段一：建 catalog + 正向 skill 比对，打印相似公司 skill 列表 | `--base`、`--library`、`--threshold`、`--run` |
| `pipeline` | 阶段零+一+二：catalog 安全预扫描 + 正向比对 + 共享用例复制 + Tier3×2 | `--base`、`--candidate`、`--library`、`--eval-source`、`--agent`、`--model`、`--run` |
| `judge` | 阶段三/四/六：输入相似报告 + 结果目录 + 安全报告，产出双结论推荐报告 | `--similarity-report`、`--results-dir`、`--skills`、`--security-dir`、`--search`、`--company-report`、`--llm`、`--out` |
| `search` | 阶段五补充：`cskills find`/`info` 关键词搜索 | `--keyword`、`--info` |

- 演示 skill 一律参数传入，不硬编码；冗余 skill 通过 `pipeline --candidate` 参数选定（终端命令，不做网页/可视化）。
- `judge` 新增 `--security-dir`：指向阶段零预扫描的安全报告目录，按 skill 名回填到 Evidence。

---

## 6. 推荐判定规则（确定性双轨）

### 6.1 前置条件（证据完整性 / 可比性）

| 条件 | 判定 | 对结论的影响 |
|---|---|---|
| Tier3 结果不完整 | `execution_status != succeeded` 或 `goal_accuracy` 缺失 | 增益结论标注"证据不足"，只输出安全结论，不做定量增益比较 |
| skill 从未激活（INCONCLUSIVE） | 激活分全 0 | 增益结论标注"未激活，无法参与增益比较" |
| 可比性不满足 | dataset_digest / agent / model / attempts 不一致 | 增益结论降级为"定性参考"，并注明不可比 |
| 安全报告缺失 | 阶段零未扫描或报告丢失 | 安全结论标注"安全审查缺失"，提示需先补扫描 |

> 注：安全结论与用例无关，不受可比性影响；增益结论与安全无关，不受安全评级影响。两条结论彼此独立（P7）。

### 6.2 安全轨判定（完整 Tier1 = SkillSpector + SkillEvaluator Tier1）

**安全审查构成**（二者并列）：

| 来源 | 关键字段 |
|---|---|
| SkillSpector | `risk_assessment.score` / `.severity` / `.recommendation` / `.max_issue_severity` + `issues[]` |
| SkillEvaluator Tier1 | `overall_status` + `severity_counts{critical/high/medium/low}` + `finding_groups[]` |

**安全评级（确定性规则）**：

| 评级 | 判定 |
|---|---|
| `safe` | SkillSpector 无 critical/high issue（`max_issue_severity ∈ {NONE, LOW, MEDIUM}` 或 `recommendation == SAFE`），**且** Tier1 `severity_counts.critical == 0 && high == 0` |
| `unsafe` | SkillSpector `max_issue_severity ∈ {HIGH, CRITICAL}` 或 `recommendation != SAFE`，**或** Tier1 `severity_counts.critical > 0 || high > 0` |

**结论三情形（含话术）**：

| 情形 | 安全结论 | 话术模板 |
|---|---|---|
| 双方 `safe` | 两者均安全 | "两者均通过完整 Tier1 安全审查（SkillSpector + SkillEvaluator Tier1），安全维度无差异，无需从安全角度二选一。" |
| 一方 `safe`、一方 `unsafe` | 推荐 safe 方 | "安全角度更推荐「{safe}」；「{unsafe}」存在高危安全 finding（附 finding 摘要），不建议采用。" |
| 双方 `unsafe` | 推荐风险更低方 | "双方均存在安全问题；相较而言安全角度更推荐「{较低风险方}」。" 附双方风险摘要。 |

**双方 unsafe 时的风险比较优先级（确定性）**：SkillSpector `risk_assessment.score` 低者 > `severity` 等级低者（NONE<LOW<MEDIUM<HIGH<CRITICAL）> SkillSpector critical/high issue 计数少者 > Tier1 critical/high 计数少者。

### 6.3 增益轨判定（多维增益）

增益比较在**同一共享用例集**上进行，综合 5 个维度（取 with-skill 臂）：

| 维度 | 数据来源（result.json / trajectory.json） | 方向 |
|---|---|---|
| 结果 | `goal_accuracy`（首选）/ `overall` / `pass@k` | 越高越好 |
| 流程 | `skill_execution` + `skill_efficiency` | 越高越好 |
| token 消耗 | `prompt_tokens`（输入）+ `completion_tokens`（输出） | 越低越好 |
| 执行时间 | `duration_seconds` | 越低越好 |
| 执行轮数 | `rounds`（trajectory `len(steps)` 之和/均值） | 越少越好 |

**判定规则（确定性，结果优先）**：

1. **结果**：Δ goal_accuracy ≥ 0.10 → 明确更优（`clear_better`）；0.05 ≤ Δ < 0.10 → 有条件更优（`conditional`）；Δ < 0.05 → 结果相当，进入第 2 步多维综合。
2. **多维综合**（结果相当时）：对「流程、token 消耗（输入+输出）、执行时间、执行轮数」4 个维度逐项 pairwise 比较，各记"更优 / 相当 / 更差"：
   - 某方**领先 ≥ 3 项** → 判「结果相当，但综合增益更优 {该方}」（`efficiency_better`）；
   - 否则 → 判「两者增益相当、均可」（`both_acceptable`）。

**"两者增益相当、均可"时的具体差异输出**：逐项列出 5 维差异（结果 / 流程 / token 输入 / token 输出 / 执行时间 / 执行轮数），并注明"该差异不足以支撑明确的增益优劣"。可给出**参考倾向**，但必须标注"仅供参考，最终由用户决定"。

**体现正向 skill 更优**：当双方结果相当、但正向 skill（calc-pro）在流程与效率维度（更少执行轮数 / 更短时间 / 更省 token）综合领先时，增益结论应体现「calc-pro 增益更优（结果相当但更高效）」，而非笼统的"两者均可"。该预期依赖 Tier3 实测验证（见 9.4），不作为硬编码结论。

### 6.4 双结论输出（决策交用户）

- 报告输出 `security_recommendation` 与 `gain_recommendation` 两个结论，各自附证据字段与话术。
- **不合成单一 verdict**；两条结论可能不一致（如"安全推荐 A" + "增益推荐 B"），属正常现象，最终"哪个更优"由用户决定（P7）。
- LLM 只负责润色两个结论的叙述、引用证据字段，不得新增事实、不得覆盖规则结论、不得擅自合并成单一推荐。

---

## 7. 数据契约

### 7.1 输入

```json
{
  "base_skill": "positive/<正向>",
  "candidate_skill": "library-20261118/<组>/<选定冗余skill>",
  "library": "library-20261118",
  "shared_eval_source": "positive/changelog 或自定义中立用例skill",
  "security_dir": "reports/security",
  "options": {"full_body": true, "threshold": 0.75, "agent": "opencode", "model": "openai/qwen3.8-flash"}
}
```

### 7.2 推荐报告输出（核心字段，双结论）

```json
{
  "run_id": "...",
  "redundant_pair": [{"name": "A", "similarity": 0.898, "classification": "SIMILAR"}, {"name": "B"}],
  "evidence": [
    {
      "skill": "A",
      "goal_accuracy": 1.0, "overall": 0.88, "pass_at_k": 1.0, "lift": 0.28,
      "skill_execution": 1.0, "skill_efficiency": 1.0,
      "prompt_tokens": 84554, "completion_tokens": 775,
      "duration_seconds": 222.96, "rounds": 13,
      "run_id": "...", "dataset_digest": "...", "agent": "opencode", "model": "...", "n_attempts": 1,
      "security": {
        "skillspector": {"risk_score": 0, "severity": "LOW", "recommendation": "SAFE", "max_issue_severity": "NONE", "issue_count": 0},
        "tier1": {"overall_status": "passed", "severity_counts": {"critical": 0, "high": 0, "medium": 6, "low": 11}},
        "verdict": "safe",
        "high_severity_findings": []
      }
    }
  ],
  "comparable": true,
  "security_recommendation": {
    "verdict": "both_safe | recommend_a | recommend_b",
    "winner": "A | B | null",
    "narrative": "两者均通过完整 Tier1 安全审查……",
    "reasons": []
  },
  "gain_recommendation": {
    "verdict": "clear_better | conditional | efficiency_better | both_acceptable | insufficient",
    "winner": "A | B | null",
    "delta_goal_accuracy": 0.0,
    "dimension_comparison": {
      "result": {"A": 1.0, "B": 1.0, "winner": null},
      "process": {"A": 1.0, "B": 1.0, "winner": null},
      "prompt_tokens": {"A": 84554, "B": 90000, "winner": "A"},
      "completion_tokens": {"A": 775, "B": 800, "winner": "A"},
      "duration_seconds": {"A": 222.96, "B": 250.0, "winner": "A"},
      "rounds": {"A": 13, "B": 15, "winner": "A"}
    },
    "efficiency_wins": {"A": 4, "B": 0},
    "narrative": "两者结果相当，但 A 在效率维度综合领先……",
    "reasons": []
  },
  "external_candidates": [{"name": "...", "source": "cskills", "evaluated": false, "similarity": 0.0}],
  "report_markdown": "..."
}
```

> 相比 v1.1：删除单一 `rule_result.verdict`（replace/merge/keep_both），改为 `security_recommendation` + `gain_recommendation` 两个结论；`evidence[].tier1_security`（字符串）升级为 `evidence[].security`（结构化对象）。

---

## 8. 验收标准

### 8.1 功能验收

- [ ] 给定一对已知冗余 skill，Tier2 正确检出（score ≥ 0.75）并给出分类；
- [ ] catalog 内每个 skill 均在阶段零完成完整 Tier1 安全审查，报告按 skill 索引存储；
- [ ] 两个候选在**同一共享用例集**上完成 Tier3，结果可比（`comparable: true`）；
- [ ] 报告同时输出 `security_recommendation` 与 `gain_recommendation` 两个结论；
- [ ] 安全结论覆盖三情形：双方 safe / 一方 unsafe / 双方 unsafe（后者给出风险更低方）；
- [ ] 增益结论覆盖：明确更优 / 有条件更优 / 两者均可（Δ<0.05 时列出具体差异）；
- [ ] 报告不合成单一"最终推荐" verdict（P7）；
- [ ] `cskills find` 能返回相关候选并标注"未实测"；
- [ ] 报告含可复现信息（dataset_digest / agent / model / attempts / run_id / 安全扫描时间与 digest）。

### 8.2 质量验收

- [ ] 不出现"不同数据集 lift 直接比大小"的结论；
- [ ] 不把"必须调用某脚本"写入共享用例 ground truth（P5）；
- [ ] 安全评级用完整 Tier1（SkillSpector + SkillEvaluator Tier1），不把 SCHEMA/QUALITY finding 误当安全漏洞；
- [ ] LLM 未覆盖规则结论、未擅自合成单一推荐；
- [ ] 安全结论与增益结论彼此独立、互不污染。

---

## 9. 答辩测试 Skill 清单

> 数据集：`skill-dataset/`（positive 15 / redundant 30 / security 7）；catalog 由「4 个公司库 skill + calculator」构成。

### 9.1 主演示对（端到端：Tier2 → 完整 Tier1 → 共享用例 Tier3 → 双结论推荐）

| 角色 | Skill | 说明 | 预期 |
|---|---|---|---|
| 正向 skill | `positive/calc-pro` | 专业计算套件（算术 + 统计 + 财务），无外部依赖 | 作为 base，跑完整流程 |
| 冗余 skill | `official/calculator` | 官方计算器（仅算术 + 单位换算） | 与 calc-pro 相似度 0.898（已实测），进入评估 |

### 9.2 catalog 构成（4 个公司库 skill + calculator）

选型原则：**与正向 skill（calc-pro，计算/数学域）语义相似度低**，避免 Tier2 误命中，验证"只命中 calculator"。

| catalog skill | 所属组 | 域 | 与 calc-pro 关系 |
|---|---|---|---|
| `code-review` | G2 | 代码评审 | 无关（预期相似度 < 0.5） |
| `requirement-spec` | G4 | 需求规格 | 无关（预期相似度 < 0.5） |
| `es-log-query` | G9 | 日志查询 | 无关（预期相似度 < 0.5） |
| `android-log-analysis` | G9 | 日志分析 | 无关（预期相似度 < 0.5） |
| `calculator` | official | 计算 | **冗余对成员，Tier2 唯一命中（0.898）** |

### 9.3 共享用例设计（复杂计算、离线可判定、不偏袒任一 skill）

- 用例须 skill 中立、grader 只判任务产出（P5）；**只取双方能力交集**（两者 `calc.py` 行为等价），不加入 stats/finance 超集任务。
- 复杂计算用例（代表集，全部落在交集内）：

| 类别 | 用例表达式 | 预期结果 |
|---|---|---|
| 嵌套/优先级 | `(100 - 25) / 3` | 25 |
| 乘方 | `2 ** 10` | 1024 |
| 混合 | `(3 + 5) ** 2 - 64 / 8` | 56 |
| 取模+乘法 | `17 % 5 + 12 * 3` | 38 |
| 一元负号+乘方 | `-(5 - 10) + 2 ** 3` | 13 |
| 百分比 | `7.5% of 480` | 36 |
| 单位换算（温度） | `100 celsius to fahrenheit` | 212 |
| 单位换算（距离） | `5 miles to km` | 8.047 |
| 单位换算（重量） | `10 kg to lbs` | 22.05 |

- 预期增益结论：双方在交集用例上均得正确结果 → 结果相当 → 进入多维综合（流程 / token / 时间 / 轮数）；预期 calc-pro 因更清晰的模块结构 + 统一 `cli.py` 入口而在效率维度综合领先 → 判「结果相当但综合增益更优 calc-pro」（`efficiency_better`，见 6.3）。若效率维度也未分出胜负，则回退「两者增益相当、均可」并列出 5 维差异表。

### 9.4 双结论演示预期

| 维度 | 预期结论 |
|---|---|
| 安全结论 | 两者经 SkillSpector 均为 SAFE（score 0 / LOW / 0 issue）→ "两者均通过完整 Tier1 安全审查，安全维度无差异" |
| 增益结论 | 双方结果均接近 1.0（结果相当）→ 进入多维综合；预期 calc-pro 在流程/效率维度综合领先 → "结果相当但综合增益更优 calc-pro"（`efficiency_better`，见 6.3/9.3） |

> 说明：calc-pro 与 calculator 安全等价，故演示中安全轨为"打平"；若需展示安全轨区分能力，需另选一组安全等级有差异的 skill（如 `security/` 组）。

### 9.5 联网搜索演示

| 动作 | 命令/来源 | 预期 |
|---|---|---|
| 公司库搜索 | `cskills find calc` / `cskills find calculator` | 返回公司库内相关 skill，作为"外部候选"供选择 |
| 详情查看 | `cskills info <name>` | 取描述/文件结构，做描述级相似比对，标注"未实测" |

### 9.6 演示风险与规避

- **Tier3 耗时**：单对双臂 20–30 分钟 → 答辩前用 `--max-cases 1 --n-attempts 1` 预热跑通并留存产物。
- **模型额度**：当前网关月额度已耗尽，已切免额模型 `qwen3.8-flash` → 评估统一用它，保证可比。
- **安全结论打平**：calc-pro/calculator 都 SAFE → 安全轨无区分度；属预期，不是缺陷，报告会以"均安全"话术呈现。

---

## 10. 风险与依赖

| 风险/依赖 | 影响 | 缓解 |
|---|---|---|
| Tier3 结果跨 skill 不可比 | 增益结论无效 | 强制共享用例集 + 记录可比性字段 |
| Tier3 成本高 | 无法全量评估 | 先 Tier2 筛 top-N，懒评估外部候选 |
| 用例设计带 skill 偏向 | 基线失真 | 用例 grader 只判任务产出（P5）；交集优先 |
| 安全结论与增益结论冲突 | 用户困惑 | 明确标注"两条结论独立，最终由用户决定"（P7） |
| 安全维度两者等价 | 安全轨退化 | 以"均安全"话术明确呈现，不强行制造差异 |
| 安全报告与代码不同步 | 安全结论失真 | 按 skill digest 记录扫描版本，变更即重扫 |
| 安全口径混淆 | 把质量噪声当安全漏洞 | 完整 Tier1 分 SkillSpector 与 SkillEvaluator Tier1 两个来源，只以 critical/high 判 unsafe |
| LLM 判定不稳定 | 演示翻车 | 规则确定性双轨，LLM 仅叙述 |

---

## 11. 开发执行情况与进度

### 11.1 已完成的开发

- **代码结构**（`skill-recommend/`，纯 stdlib、Python 3.9，无第三方依赖）：
  - `models.py` 数据结构（`SimilarityMatch` / `Evidence` / `RuleResult` / `ExternalCandidate` / `RecommendationReport`）
  - `config.py` 阈值与常量（相似度 / 增益差 / 硬门槛 / LLM 网关）
  - `tier2.py` 相似报告解析（同时支持 `SIMILARITY` 与 `INTER_SKILL`）
  - `tier3.py` Tier3 结果解析（`result.json`/`lift.json`/`pass_at_k_lift.json`）
  - `rules.py` 确定性规则判定（硬门槛 → 可比性 → 分数差 → tie-break）
  - `report.py` 报告渲染（中文叙述 + Markdown）
  - `llm.py` 可选 LLM 报告增强（失败回退模板）
  - `search.py` 联网搜索（`cskills find`/`info` + 语义候选合并）
  - `judge.py` 判定编排、`pipeline.py` 命令编排 + 共享用例复制、`detect.py` 相似检测、`cli.py` 4 个子命令
- **测试**：43 个 `unittest` 用例全绿（TDD，含真实 calculator 产物 golden fixture）。
- **官方实现隔离**：`skill-evaluation-pipelines/`、`skill-security-scanners/` 零改动；推荐功能只做 `docker compose run` 命令编排与产物只读解析，原 Tier2/Tier3 可独立运行。

### 11.2 待开发（v1.2 双结论方案引入的改动）

- [x] 阶段零 catalog 安全预扫描（SkillSpector + SkillEvaluator Tier1，报告按 skill 索引存储）
- [x] `Evidence.tier1_security`（str）升级为 `Evidence.security`（结构化对象），并接线回填（`load_security_from_report`）
- [x] `rules.py` 改为双轨：安全轨（完整 Tier1 评级 + 三情形）+ 增益轨（含"两者均可"差异输出），删除单一 verdict
- [x] `report.py` 输出 `security_recommendation` + `gain_recommendation` 双结论
- [x] `judge` 新增 `--security-dir` 参数
- [x] 单元测试覆盖双轨四情形 + 三安全情形

### 11.3 开发进度清单

- [x] 需求文档（本文件，v1.2，双结论方案）
- [x] 核心数据模型与阈值配置
- [x] Tier2 相似报告解析（SIMILARITY + INTER_SKILL）
- [x] Tier3 结果解析（归一化 Evidence）
- [x] 完整 Tier1 安全审查解析与 Evidence 接线（v1.2 新增）
- [x] 确定性双轨推荐规则（安全结论 + 增益结论，v1.2 改造）
- [x] 双结论报告渲染 + 可选 LLM 叙述（v1.2 改造）
- [x] 联网搜索（关键词 + 语义合并）
- [x] 流程编排：`detect` / `pipeline`（含安全预扫描）/ `judge`（含 `--security-dir`）/ `search`
- [x] 共享用例自动复制（`--eval-source`，dry-run 不落地）
- [x] 单元测试（62 例全绿，含双轨用例）
- [ ] Docker 真实端到端跑通 `detect → pipeline → judge`（待 Docker 环境 + 演示 skill 确定）
- [ ] 编写 skill 中立的共享用例集（`evals/evals.json + files/`）
- [ ] 确定答辩演示对（正向 calc-pro + 冗余 calculator）与 4 个 catalog skill

---

*文档结束。后续实现请以本需求 + 上述设计原则为准，改动流程或规则须同步更新本文档。*
