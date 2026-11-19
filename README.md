# AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统

> 课题：AI Agent 技能全链路安全审计与效果评估系统
> 定位：基于 NVIDIA 开源项目（**SkillSpector** 安全扫描器 + **SkillEvaluator** 三层评估框架），扩展「自定义安全规则」「一键批处理审计」「冗余 Skill 推荐」三项能力，对 Agent Skill 做 **静态安全扫描 → 语义去重 → 沙盒增益评估** 的全链路审计。

---

## 1. 系统概览

### 1.1 三层评估架构

| 层 | 回答的问题 | 采用的组件 | 输出 |
|---|---|---|---|
| **Tier 1 安全验证** | 这个 skill 安全吗？格式规范吗？ | SkillSpector（静态规则 + 可选 LLM）+ Gitleaks + 质量/Schema 检查 | `flag`：safe / unsafe 高危过滤 |
| **Tier 2 语义去重** | 指令是否重复/冲突？ | embedding 向量化（本地 Ollama `bge-m3`）+ catalog 比对 | `dup`：相似度 / 冗余对 |
| **Tier 3 沙盒增益** | 这个 skill 真的帮到 Agent 吗？ | Harbor 沙盒 + opencode agent 的 with/without 双臂对照 + LLM Judge | `pass_rate_gain / Lift` |

三层结论独立记录、不合并为单一分数。

### 1.2 自研扩展（相对官方项目的新增能力）

| 扩展 | 对应课题要求 | 实现位置 |
|---|---|---|
| **任务 A**：≥2 条企业自定义安全规则（域名白名单放行 + 明文凭证检测） | 阶段三·任务 A | `custom-rules/` + SkillSpector `suppression.py` 扩展 |
| **任务 B**：一键批处理审计 CLI（扫描→过滤高危→Markdown/HTML 报告） | 阶段三·任务 B | `skill-recommend/skill_recommend/batch.py` |
| **冗余 Skill 推荐**：评估后推荐更优 skill + 联网搜索候选 | 阶段二 | `skill-recommend/`（`detect`/`pipeline`/`judge`/`search`） |

---

## 2. 仓库内容与提交边界

本仓库只随附 **3 个核心演示 Skill + 1 个共享用例集**（对应课题「3 个自建测试 Skill」），完整的 52 个 Skill 数据集为本地构建产物，**不随仓库提交**（构建方法见 [§9](#9-数据集构建流程)）。

### 2.1 提交的内容

| 内容 | 路径 | 说明 |
|---|---|---|
| 两个 NVIDIA 官方项目（含本地补丁） | `skill-security-scanners/SkillSpector/`、`skill-evaluation-pipelines/SkillEvaluator/` | 完整源码；本地补丁见 [§8](#8-本地补丁说明) |
| 自研扩展功能代码 | `skill-recommend/`、`custom-rules/` | 纯 Python 标准库，无第三方依赖 |
| 3 个演示 Skill | `skill-dataset/positive/calc-pro/`（正向）、`skill-dataset/official/calculator/`（冗余）、`skill-dataset/security/custom-rules-range/`（安全靶场） | 每个含 `SKILL.md` + 脚本 + evals |
| 共享用例集 | `skill-dataset/shared/arithmetic/` | 9 例基础算术，供 calc-pro vs calculator 公平横向对比 |
| 分析报告与文档 | `docs/`、`deliverables/` | 结论文档、需求文档、架构解析报告、复盘报告 |
| 编排与构建文件 | `docker-compose.yml`、`Dockerfile.eval-base-opencode`、`.env.example`、`.gitignore` | 环境复现所需 |

### 2.2 不提交的内容

| 内容 | 说明 |
|---|---|
| `reports/` | 三层评估运行产物（Tier1/2/3 报告、审计报告等），README 给出重生成命令 |
| `.env` | 含 LLM 网关 API key，使用 `.env.example` 模板自行填写 |
| embedding 模型镜像 | Ollama `bge-m3` 模型（1.2GB）、`skillevaluator-deps` 沙盒依赖镜像等大文件，仅提供 Dockerfile 与构建/拉取命令 |
| 其他 Skill | `skill-dataset/redundant/`（30 个）、`positive/` 其余 15 个、`security/` 其余 8 个、`official/` 其余 5 个、`library-*`、`reference/` 等，需通过 `cskills` 从公司库拉取（见 §9） |
| `custom-rules/staged/` | `toggle.py` 运行时生成的规则组装目录 |

---

## 3. 目录结构

```
.
├── README.md                         # 本文档
├── docker-compose.yml                # skillspector / skillevaluator / ollama 编排
├── Dockerfile.eval-base-opencode     # Tier3 沙盒依赖镜像（预装 nvm+node22+opencode）
├── .env.example                      # 环境变量模板（复制为 .env 后填写）
├── skill-security-scanners/
│   └── SkillSpector/                 # NVIDIA 安全扫描器（含 allow_domain 本地扩展）
├── skill-evaluation-pipelines/
│   └── SkillEvaluator/               # NVIDIA 三层评估框架（含本地适配补丁）
├── skill-recommend/                  # 自研：冗余推荐 + 批处理 CLI（纯 stdlib）
│   └── skill_recommend/
│       ├── cli.py                    # 5 个子命令入口
│       ├── detect.py / pipeline.py   # Tier2 比对 + Tier3 编排
│       ├── judge.py / rules.py       # 双结论确定性判定
│       ├── batch.py                  # 任务 B 批处理
│       └── tier2.py / tier3.py / security.py  # 产物解析
├── custom-rules/                     # 自研：自定义安全规则（任务 A）
│   ├── cvte_credential_inline.yar    # 规则 B：明文凭证检测（YARA）
│   ├── baseline.yaml                 # 规则 A：域名白名单放行（allow_domain）
│   ├── select.yaml                   # 规则 A/B 灰度开关配置
│   └── toggle.py                     # 按开关组装 staged/ 目录
├── skill-dataset/
│   ├── positive/calc-pro/            # ① 正向 skill（专业计算套件）
│   ├── official/calculator/          # ② 冗余 skill（官方计算器）
│   ├── security/custom-rules-range/  # ③ 安全靶场 skill（植入规则 A/B 样本）
│   └── shared/arithmetic/            # 共享用例集（9 例，calc-pro↔calculator 交集）
├── docs/                             # 课题文档、需求文档、结论文档
└── deliverables/                     # 交付物（架构解析/复盘/规则证实报告等）
```

---

## 4. 环境要求

| 依赖 | 版本 | 说明 |
|---|---|---|
| 操作系统 | macOS 12 Monterey（arm64） | 实测环境；Linux/Windows 需自行验证 |
| Docker | Docker Desktop 4.37.1+ | 需配置镜像加速器（`registry-mirrors` → `https://docker.m.daocloud.io`），见 [§10](#10-常见问题排查) |
| Python | 3.9+（自研代码）/ 3.12-3.15（官方项目） | 自研 `skill-recommend` 用标准库，无需安装依赖 |
| uv | 最新版 | 官方项目推荐依赖管理工具 |
| LLM 网关 | OpenAI 兼容网关（`token.cvte.com`） | Tier1/Tier3 的 LLM 环节；需 API key |
| Ollama | 本地 `bge-m3` 模型 | Tier2 embedding（网关无 embedding 模型） |
| `cskills` CLI | v5.9.4（可选） | 仅「联网搜索」与「完整数据集构建」需要 |

> **重要**：Tier2 embedding 依赖本地 Ollama（网关无 embedding 模型）；Tier1/Tier3 的 LLM 环节走 OpenAI 兼容网关。两者缺一不可。

---

## 5. 快速开始（环境搭建）

### 5.1 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，至少填写以下两项：
#   SKILL_EVAL_LLM_API_KEY=<网关 key>
#   SKILLSPECTOR_COMPAT_API_KEY=<网关 key>
```

`.env` 关键项说明（完整注释见 `.env.example`）：

| 变量 | 值 | 作用 |
|---|---|---|
| `SKILL_EVAL_LLM_PROVIDER` | `openai-compatible` | 三层评估 LLM 走网关 |
| `SKILL_EVAL_LLM_BASE_URL` | `https://token.cvte.com/v1` | 网关地址 |
| `SKILL_EVAL_LLM_MODEL` | `qwen3.8-flash` | 免额且支持强制 tool_choice（可换 `qwen3.8-max`） |
| `SKILL_EVAL_EMBEDDING_*` | `openai-compatible` / `http://ollama:11434/v1` / `bge-m3` | Tier2 embedding 走本地 Ollama |
| `SKILLSPECTOR_PROVIDER` | `openai_compatible` | SkillSpector 走同一网关 |
| `SKILLSPECTOR_MAX_LLM_CONCURRENCY` | `2` | 网关 RPM 限制，串行化请求 |
| `UV_INDEX_URL` | `https://mirrors.aliyun.com/pypi/simple/` | 容器内 uv 依赖走阿里云镜像 |
| `SKILLEVALUATOR_FORCE_PATH_COPY` | `1` | macOS VirtioFS 绑定挂载兼容 |
| `SKILLEVALUATOR_BASE_IMAGE` | `skillevaluator-deps:3.12-opencode` | 复用预构建沙盒镜像（可选） |

### 5.2 构建 Docker 镜像

按顺序构建三个镜像（tier3 依赖 local 基础镜像）：

```bash
# ① SkillEvaluator 基础镜像（含源码）
docker build -t skillevaluator:local \
  -f skill-evaluation-pipelines/SkillEvaluator/Dockerfile \
  skill-evaluation-pipelines/SkillEvaluator

# ② SkillEvaluator Tier3 镜像（FROM local，内置 Docker CLI 供沙盒）
docker build -t skillevaluator:tier3 \
  -f skill-evaluation-pipelines/SkillEvaluator/Dockerfile.tier3 \
  skill-evaluation-pipelines/SkillEvaluator

# ③ SkillSpector 安全扫描器镜像
docker build -t skillspector:local \
  -f skill-security-scanners/SkillSpector/Dockerfile \
  skill-security-scanners/SkillSpector
```

> **网络提示**：构建阶段 `pip install` 默认走 PyPI，国内环境可能极慢/超时。若失败，在对应 Dockerfile 加 `ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/` 与 `PIP_TRUSTED_HOST=mirrors.aliyun.com` 后重建（见 [§10](#10-常见问题排查)）。

**可选：构建 Tier3 沙盒加速镜像**（不构建也能跑 Tier3，只是每个沙盒会重复从 npm 慢速下载 opencode 二进制，耗时较长）：

```bash
# 基于预装 verifier 依赖的基础镜像 skillevaluator-deps:3.12 构建，
# 额外预装 nvm + node22 + opencode-ai@1.19.5，使沙盒 install() 幂等秒过
docker build -t skillevaluator-deps:3.12-opencode -f Dockerfile.eval-base-opencode .

# 构建后在 .env 中启用：
#   SKILLEVALUATOR_BASE_IMAGE=skillevaluator-deps:3.12-opencode
```

> 注：基础镜像 `skillevaluator-deps:3.12` 需先用 `docker run` 预装 Harbor 沙盒的 verifier 依赖（RAGAS/openai/anthropic/boto3 等）后 `docker commit` 生成；此加速路径为可选优化，首次复现可跳过。

### 5.3 启动 Ollama 并拉取 embedding 模型

```bash
# 启动 ollama 服务（首次会拉取 ollama/ollama 镜像）
docker compose up -d ollama

# 拉取 bge-m3 embedding 模型（1.2GB，Tier2 必需）
docker compose exec ollama ollama pull bge-m3
```

验证 embedding 可用：

```bash
curl http://localhost:11434/v1/embeddings -d '{"model":"bge-m3","input":"hello"}' \
  -H 'Content-Type: application/json'
# 应返回 1024 维向量
```

### 5.4 验证环境（doctor）

```bash
docker compose run --rm skillevaluator doctor --env-mode docker
```

`doctor` 通过即表示：扫描器就绪、LLM 网关可达、embedding 可达、沙盒就绪。

---

## 6. 三层评估复现（官方项目）

> 路径映射：宿主机 `./skill-dataset` → skillspector 容器 `/scan`、skillevaluator 容器 `/skills`；宿主机 `./reports` → 容器 `/app/reports`。

### 6.1 Tier 1 安全扫描

**SkillSpector 静态扫描**（零成本，先跑）：

```bash
# 安全靶场 skill（预期命中多条 HIGH：明文凭证等）
docker compose run --rm skillspector scan /scan/security/custom-rules-range --no-llm

# 正向 skill（预期 SAFE）
docker compose run --rm skillspector scan /scan/positive/calc-pro --no-llm

# 输出 JSON 报告
docker compose run --rm skillspector scan /scan/security/custom-rules-range \
  --no-llm --format json --output /app/reports/demo.json
```

**SkillEvaluator Tier 1**（质量 + Schema + 安全静态检查）：

```bash
docker compose run --rm skillevaluator tier1 /skills/positive/calc-pro --no-llm
docker compose run --rm skillevaluator tier1 /skills/security/custom-rules-range --no-llm
```

### 6.2 Tier 2 语义去重

对 calc-pro 与 calculator 建 catalog 比对，验证冗余对：

```bash
# ① 对 calculator 建 embedding catalog
docker compose run --rm skillevaluator similarity-check /skills/official/calculator \
  --save-catalog /app/reports/company-catalog.json --full-body

# ② 正向 skill 对 catalog 语义比对
docker compose run --rm skillevaluator similarity-check /skills/positive/calc-pro \
  --catalog /app/reports/company-catalog.json \
  --output-dir /app/reports/company-match/positive_calc-pro --report json --full-body
```

预期：calc-pro ↔ calculator 相似度 **≈ 0.913，分类 `HIGH_SIMILARITY`**（冗余对成立）。

### 6.3 Tier 3 沙盒增益

对正向 skill 跑 with/without 双臂对照：

```bash
# 正向 skill 专项增益（统计/财务用例，预期 lift +30pp 左右）
docker compose run --rm skillevaluator tier3 /skills/positive/calc-pro \
  --agents opencode --model openai/qwen3.8-flash \
  --max-cases 1 --timeout-multiplier 3 --results-dir /app/reports/reco-results

# 冗余 skill（共享用例）
docker compose run --rm skillevaluator tier3 /skills/official/calculator \
  --agents opencode --model openai/qwen3.8-flash \
  --max-cases 1 --timeout-multiplier 3 --results-dir /app/reports/reco-results
```

> 关键参数：`--timeout-multiplier 3`（baseline 臂无 skill 辅助，默认超时不够）；`--max-cases 1`（控制 LLM 费用与时长，答辩前预热）。完整双臂单 skill 约 10–30 分钟。

---

## 7. 自研功能复现

### 7.1 任务 A：自定义安全规则（`custom-rules/`）

两条正交规则：

- **规则 A（域名白名单放行，抑制层）**：把「发往企业白名单域名的外发 finding」从 kept 移到 suppressed（降误报），**不新增 finding**，经 `--baseline` 挂载。
- **规则 B（明文凭证检测，YARA）**：检测 `chpasswd` / `curl -u user:pass` / `mysql -p<pass>` / `psql 连接串` / `redis -a` / URL userinfo 等明文凭证，经 `--yara-rules-dir` 挂载。

**灰度开关**：编辑 `custom-rules/select.yaml` 的 `rule_a` / `rule_b`，然后：

```bash
# 按开关组装规则 B 的 staged/ 目录（规则 A 不落地文件，仅提示是否追加 --baseline）
python3 custom-rules/toggle.py
```

**四组对照**（`select.yaml` 分别设 `true/false`）：

| 组合 | 命令 |
|---|---|
| 基线（都关） | `docker compose run --rm skillspector scan /scan/security/custom-rules-range --no-llm --format json` |
| 仅规则 A | 同上 + `--baseline /custom-rules/baseline.yaml` |
| 仅规则 B | 同上 + `--yara-rules-dir /custom-rules/staged` |
| A + B | 同上 + `--yara-rules-dir /custom-rules/staged --baseline /custom-rules/baseline.yaml` |

**预期结果**（对 `custom-rules-range` 靶场）：

- 规则 B 的 7 个明文凭证正样本（`echo 'root:P@ss' | chpasswd` 等）**全部命中 HIGH**；负样本（`-p<password>`、`-u ${password}`、`-p` 无值）**零命中**。
- 挂规则 B 后风险分 **58 → 69**（+1 finding）；靶场综合扫描 **risk_score 59 / HIGH / DO_NOT_INSTALL**。
- 规则 A 把发往 `*.cvte.com` 的外发移入 `suppressed`（不计分），发往 `evil-c2.example.com` 的仍告警。

### 7.2 任务 B：一键批处理审计（`scan`）

```bash
# 从仓库根目录运行（自动发现含 SKILL.md 的 skill，默认 dry-run 打印命令）
python -m skill_recommend scan --dir security

# 真正执行（对 security/ 下所有 skill 跑 SkillSpector + Tier1）
python -m skill_recommend scan --dir security --run

# 启用 LLM 语义分析（需网关凭据，检出更强但更慢）
python -m skill_recommend scan --dir security --run --llm
```

输出：`reports/audit.md` + `reports/audit.html`（含「安全评级 + 沙盒 A/B 对照」的综合审计报告，`verdict == unsafe` 的 skill 进「高危风险项」表）。

### 7.3 冗余 Skill 推荐（`detect` → `pipeline` → `judge` → `search`）

针对冗余对 calc-pro（正向）vs calculator（冗余）的端到端流程：

```bash
# ① 相似检测：正向 skill 对公司库 catalog 语义比对
python -m skill_recommend detect --base positive/calc-pro --library official --run

# ② 编排：安全预扫描 + 建 catalog + 正向比对 + 共享用例 Tier3×2
python -m skill_recommend pipeline \
  --base positive/calc-pro --candidate official/calculator \
  --eval-source shared/arithmetic --run

# ③ 判定：输入 Tier2/Tier3 产物 + 安全报告，产出双结论推荐
python -m skill_recommend judge \
  --similarity-report reports/company-match/positive_calc-pro/skillevaluator-similarity.json \
  --results-dir reports/reco-results \
  --skills calc-pro calculator \
  --security-dir reports/security \
  --out reports/recommendation.md

# ④ 联网搜索（可选，需 cskills 登录 + 网络）
python -m skill_recommend search --keyword calculator
```

**推荐结论（双结论，不合成单一 verdict）**：

| 维度 | 结论 |
|---|---|
| 安全结论 | calc-pro 与 calculator 均 SAFE（SkillSpector score 0 / Tier1 high=0）→ 安全轨打平 |
| 增益结论 | 特化任务（统计/财务）→ calc-pro 更优（lift +30pp）；泛化任务（基础算术）→ 结果等效但 calculator 更省 token/耗时 |

> `judge` 的 `--similarity-report` / `--results-dir` / `--security-dir` 分别对应 §6.2 的 Tier2 报告、§6.3 的 Tier3 结果、§7.2 的安全报告目录；均可用已跑好的产物离线复现判定（无需重跑评估）。

---

## 8. 本地补丁说明

两个官方项目在 vendor 源码中落地了以下本地适配（均为复现所必需）：

### 8.1 SkillSpector（`skill-security-scanners/SkillSpector/`）

| 文件 | 改动 | 作用 |
|---|---|---|
| `src/skillspector/suppression.py` | 扩展 `SuppressionRule` 增加 `allow_domain`（精确 host + `*.` 子域名通配，可选 `methods` 维度） | 规则 A 域名白名单放行的落点 |

### 8.2 SkillEvaluator（`skill-evaluation-pipelines/SkillEvaluator/`）

| 文件（`src/skillevaluator/` 下） | 改动 | 作用 |
|---|---|---|
| `validators/security.py` | 增加 `openai_compatible` 的 provider→env 映射 + `SKILLSPECTOR_MAX_LLM_CONCURRENCY` 透传 | 让 Tier1 正确调用 OpenAI 兼容网关的 SkillSpector，并限制并发 |
| `tier3/harbor/templates/eval.py` | 429 限流重试（解析 `reset_time`）+ judge 请求超时可配置 | 适配网关 20 RPM 限流与慢推理 |
| `tier3/harbor/installed_agents.py` | opencode EPIPE 退出码 1 容错 | 消除 `stdbuf -oL tee` 管道崩坏导致的误判失败 |
| `tier3/harbor/.../secure_copy.py` | 增加 `SKILLEVALUATOR_FORCE_PATH_COPY` 开关 | macOS VirtioFS 绑定挂载 readdir 不更新的兼容 |
| `provider_config.py` | `opencode` 默认模型改为 `openai/qwen3.8-flash` | 避免 Tier3 不传 `--model` 时 404 |

> 这些补丁直接存在于仓库 vendor 源码中，重新构建镜像即生效；如重新 clone 官方项目需重新应用上述改动。

---

## 9. 数据集构建流程

### 9.1 三个核心演示 Skill（随仓库提交）

| Skill | 路径 | 构建方式 | 结构 |
|---|---|---|---|
| **正向** calc-pro | `skill-dataset/positive/calc-pro/` | 自建：在官方 calculator 基础上扩展统计/财务 | `SKILL.md` + `scripts/{calc,stats,finance,cli}.py` + `evals/` |
| **冗余** calculator | `skill-dataset/official/calculator/` | 复制官方 reference skill | `SKILL.md` + `scripts/calc.py` + `evals/` |
| **安全靶场** custom-rules-range | `skill-dataset/security/custom-rules-range/` | 自建：植入规则 A 白名单外发样本 + 规则 B 明文凭证正/负样本 | `SKILL.md` + `exfil_helper.py` |

### 9.2 共享用例集（`shared/arithmetic`）

9 例基础算术 + 单位换算，**只取 calc-pro 与 calculator 的能力交集**，`neutral` 格式（不含 `expected_skill`，纯结果断言），保证横向对比公平：

```
(100 - 25) / 3 → 25      2 ** 10 → 1024        (3 + 5) ** 2 - 64 / 8 → 56
17 % 5 + 12 * 3 → 38      -(5 - 10) + 2 ** 3 → 13
7.5% of 480 → 36          100°C → 212°F        5 miles → 8.047 km
```

用例由 `pipeline --eval-source shared/arithmetic` 自动复制到双方（只拷 `evals.json`，保证 `dataset_digest` 一致 → 可比）。

### 9.3 完整 52 Skill 数据集（可选，不随仓库提交）

完整数据集（positive 15 / redundant 30 / security 7）从公司 Skill 库构建：

```bash
# ① 登录公司 skill 库（飞书扫码 SSO，一次登录后续可复用）
cskills login

# ② 搜索并拉取 skill 到本地
cskills find <关键词>          # 搜索
cskills info <name>            # 查看详情
cskills add <name> --local --agent claude-code   # 拉取到本地

# ③ 打标签（生成 manifest.json）
python scripts/gen_manifest.py
```

- 数据来源：公司 Skill 库 `https://skills.gz.cvte.cn/`（需 `cskills` CLI 登录态）
- 标签字段：`name` / `category`（positive/redundant/security）/ `group` / `expected.tier1_security` 等
- 冗余组按语义重叠组织（git 提交、代码审查、测试用例、需求分析等 8 组）

> 本仓库只提交 3 个核心演示 Skill；完整数据集为本地构建产物，答辩演示聚焦三个 Skill 即可覆盖三层评估与三项自研扩展的完整链路。

---

## 10. 常见问题排查

| 问题 | 原因 | 解决 |
|---|---|---|
| 镜像拉取失败 | Docker Hub 被墙 | Docker Desktop 配置 `registry-mirrors = https://docker.m.daocloud.io` |
| 构建镜像 pip 超时 | 容器内走默认 PyPI | Dockerfile 加 `PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/` |
| Tier2 无 embedding | 网关无 embedding 模型 | 用本地 Ollama `bge-m3`（§5.3） |
| 语义分析 incomplete / 429 | 网关 RPM 限制 | `.env` 设 `SKILLSPECTOR_MAX_LLM_CONCURRENCY=2` |
| judge 报 time budget exhausted | 网关慢推理 | `.env` 设 `SKILL_EVAL_LLM_JUDGE_BUDGET_SEC=900`、`SKILL_EVAL_LLM_JUDGE_REQUEST_TIMEOUT_SEC=600` |
| staging tree 报错 | macOS VirtioFS 绑定挂载 | `.env` 设 `SKILLEVALUATOR_FORCE_PATH_COPY=1` |
| baseline 臂超时 | 无 skill 辅助执行更慢 | `--timeout-multiplier 3` + `--tolerate-baseline-timeouts` |
| opencode 沙盒安装慢 | 每个沙盒重复下载 opencode 二进制 | 可选复用预构建沙盒镜像 `Dockerfile.eval-base-opencode`（见 §5.2，需先有 `skillevaluator-deps:3.12` 基础镜像） |
| 深推理导致耗时翻倍 | qwen 系列为 reasoning 模型 | baseline 臂深推理步耗时长，属正常，`--timeout-multiplier 3` 兜底 |

> 完整排障记录见 [`deliverables/03-现场演示与复盘/排障笔记.md`](deliverables/03-现场演示与复盘/排障笔记.md)。

---

## 11. 关键量化结论（复现验证点）

复现后应能看到（详细数据见 [`docs/收尾量化结论.md`](docs/收尾量化结论.md)）：

| 层 | 数据集 | 结论 |
|---|---|---|
| Tier1 安全 | security | 规则 B 补盲明文凭证（58→69 分、+1 finding，占位符零误报）；靶场 `custom-rules-range` 12 findings / HIGH / DO_NOT_INSTALL |
| Tier2 去重 | redundant | calc-pro ↔ calculator 相似度 **0.913 HIGH_SIMILARITY** |
| Tier3 增益 | positive | calc-pro 专项 **Lift +0.3185**（Overall 68.2%→100%）；冗余对共享任务 calculator 效率更优 |

---

## 12. 许可与致谢

- 基础框架：NVIDIA [SkillSpector](https://github.com/NVIDIA/SkillSpector) 与 [SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator)（Apache 2.0）
- 沙盒评估：Harbor（开源 agent 评估框架）
- 自研扩展：`skill-recommend/`、`custom-rules/`（本课题）
