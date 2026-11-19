# 官方示例 Skill 全链路评估 —— 输入与环境

## 1. 评估对象（全部来自官方仓库）

来源：`skill-evaluation-pipelines/SkillEvaluator`

| Skill | 来源路径 | 用途 |
| --- | --- | --- |
| text-analyzer | `src/skillevaluator/tier3/reference_skills/text-analyzer` | Quickstart 官方示例；Tier1 / Tier3 |
| calculator | `src/skillevaluator/tier3/reference_skills/calculator` | Tier3 官方参考 Skill；Tier1 / Tier2 / Tier3 |
| task-list | `src/skillevaluator/tier3/reference_skills/task-list` | Tier2 集合去重 |
| api-caller | `src/skillevaluator/tier3/reference_skills/api-caller` | Tier2 集合去重 |
| create-custom-grader | `src/skillevaluator/tier3/reference_skills/create-custom-grader` | Tier2 集合去重 |
| skillevaluator | `skills/skillevaluator` | 官方自带的 SkillEvaluator 使用技能；Tier2 集合去重 |

运行时副本位于 `skill-dataset/official/`，容器内挂载为 `/skills/official/`。

## 2. 环境

- Docker Desktop（Apple Silicon / macOS 12），Docker Desktop engine
- 镜像：`skillspector:local`、`skillevaluator:tier3`
- **Tier3 基础镜像**：`skillevaluator-deps:3.12`（预装 apt 依赖 + RAGAS/openai/anthropic/boto3 判官依赖，跳过沙盒构建期 pip；构建期网络缓慢，见分析报告第 8 节）
- LLM：token.cvte.com OpenAI 兼容网关，`qwen3.8-flash`（免额、支持强制 tool_choice）
- Embedding：本地 Ollama `bge-m3`（1024 维），容器内 `http://ollama:11434/v1`
- 关键兼容变量：`SKILLEVALUATOR_FORCE_PATH_COPY=1`（macOS 绑定挂载 readdir 问题）、`SKILLEVALUATOR_BASE_IMAGE=skillevaluator-deps:3.12`（Tier3 复用基础镜像）

## 3. 运行命令

见 `00-logs/` 下各步骤日志；报告目录结构：

```text
reports/official-eval-20261117/
├── 00-inputs/          输入清单与说明
├── 00-logs/            各步骤原始终端日志（含失败轮次）
├── 01-tier1/           SkillEvaluator Tier1 + SkillSpector 报告
├── 02-tier2/           Tier2 intra-skill / inter-skill 报告与 catalog
├── 03-tier3/           Docker 沙盒 with/without 对照结果
│   └── calculator/
│       ├── 20261117_234710_1_fe25371abd9e/  成功的 A/B 运行
│       └── _failed-runs/                   前 6 次构建失败的原始产物（备查）
└── 分析报告.md         三层报告汇总分析
```

## 4. 复现命令

> Tier3 前置条件：本地存在 `skillevaluator-deps:3.12` 镜像（`docker run` 运行时安装判官依赖后 commit），
> 且 `.env` 设置 `SKILLEVALUATOR_BASE_IMAGE=skillevaluator-deps:3.12`。
> calculator 的 `evals/config.yml` 已加 `harbor.base_image_mode: reuse`。

```bash
# Tier1（text-analyzer，含 SkillSpector 静态 + LLM 语义）
docker compose run --rm skillevaluator tier1 /skills/official/text-analyzer \
  -r cli,json,html,markdown -o /app/reports/official-eval-20261117/01-tier1/text-analyzer

# Tier2 集合级语义去重（建立 catalog）
docker compose run --rm skillevaluator similarity-check /skills/official \
  --save-catalog /app/reports/official-eval-20261117/02-tier2/inter-skill/official-catalog.json \
  -r cli,json,html,markdown -o /app/reports/official-eval-20261117/02-tier2/inter-skill

# Tier2 单技能内部冗余
docker compose run --rm skillevaluator context-optimization-check /skills/official/skillevaluator \
  -r cli,json,html,markdown -o /app/reports/official-eval-20261117/02-tier2/intra-skill-skillevaluator

# Tier3 沙盒 A/B（worker + judge 均 qwen3.8-flash）
docker compose run --rm skillevaluator tier3 /skills/official/calculator \
  --agents opencode --model openai/qwen3.8-flash --timeout-multiplier 3 --max-cases 1 \
  --results-dir /app/reports/official-eval-20261117/03-tier3/calculator
```
