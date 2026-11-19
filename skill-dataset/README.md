# CVTE Agent Skills 数据集

本目录是「AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统」实习课题的测试数据集，共 **52 个 Skill**，从公司内部 Skill 库 `https://skills.gz.cvte.cn/` 拉取并打标签，供 NVIDIA SkillSpector / SkillEvaluator 三层评估流水线使用。

## 目录结构

```
skill-dataset/
├── README.md          # 本说明
├── manifest.json      # 标签清单（ground truth）
├── positive/          # 正向业务 Skill（15 个）
├── redundant/         # 冗余冲突 Skill（30 个，8 个冗余组）
└── security/          # 安全关注 Skill（7 个，含敏感操作的真实业务）
```

## 三组分类说明

| 分组 | 数量 | 定义 | 预期表现（供三层评估对照） |
|---|---|---|---|
| **positive** | 15 | 功能单一、无安全风险的正向业务 Skill | Tier1 安全 `pass`，Tier2 去重 `pass`，Tier3 沙盒增益 `yes` |
| **redundant** | 30 | 高度相似/同名的 Skill，按 8 个冗余组组织 | Tier1 `pass`，Tier2 去重 `dup`（应被拦截） |
| **security** | 7 | 含敏感操作（SSH/凭证/SQL/日志）的真实业务 Skill | Tier1 预期 `flag`（触发安全审查关注） |

### 对标官方示例的重点正向 Skill

SkillEvaluator 自带参考 Skill 中，`text-analyzer`（确定性单脚本）与 `api-caller`（多外部 HTTP 调用 + OpenAPI 解析）最适合做 Tier3 增益对照。数据集从公司库中挑选了结构对标的两项：

| 官方参考 | 公司 Skill | 对标点 |
|---|---|---|
| `text-analyzer` | `json-format` | 确定性单脚本、无外部依赖、无网络 |
| `api-caller` | `apifox-api-artifact` | 脚本驱动真实 HTTP（GET 端点列表 + POST 导出 OpenAPI）+ OpenAPI 规范化 + 多步流程 + references |

### redundant 冗余组明细

| 组名 | 成员数 | Skill |
|---|---|---|
| git-commit | 6 | git-commit, git-commit-msg, commit-message, smart-git-commit, super-commit, git-add-commit |
| code-review | 6 | code-review, code-review-and-teach, cxx-style-review, embedded-code-review, local-code-review, mr-suggestion |
| daily-report | 2 | malong-daily-report, malong-daily-report-eus |
| jira-batch | 2 | jira-batch-create, jira-batch-create-bxc |
| patent | 3 | patent-assistant, patent-disclosure, patent-search |
| doc-to-md | 3 | feishu-doc-to-markdown, markitdown, feishu-doc-writer |
| requirement | 4 | requirements-analyst, project-prd, requirement-spec, grilling |
| testcase | 4 | auto-test, Create-testcases, requirement-test-generator, test-cases |

## 标签 Schema（manifest.json）

每个 skill 的标签字段：

| 字段 | 说明 |
|---|---|
| `name` | Skill 名 |
| `category` | `positive` / `redundant` / `security` |
| `group` | 冗余组名（仅 redundant 有效，其余为 null） |
| `description` | 功能描述 |
| `operations` | 涉及的工具调用 / 终端命令 |
| `has_scripts` | 是否含可执行脚本（scripts/ 或根目录脚本） |
| `expected.tier1_security` | 预期安全扫描结果：`pass` / `flag` |
| `expected.tier2_dedup` | 预期去重结果：`pass` / `dup` |
| `expected.tier3_sandbox_gain` | 是否适合沙盒增益评估：`yes` / `no` |

## 使用方法

1. **SkillSpector（Tier 1 安全扫描）**：对三个分组分别跑静态/LLM 扫描，验证 `positive` 是否全 `pass`、`security` 是否被 `flag`。
2. **SkillEvaluator Tier 2（语义去重）**：用 `redundant` 组验证跨 Skill 冗余拦截（注意：需先配置 embedding 来源，当前 `token.cvte.com` 网关无 embedding 模型）。
3. **SkillEvaluator Tier 3（沙盒增益）**：从 `positive` 组挑选 Skill 做带/不带 Skill 的 Docker 沙盒对照，量化行为增益。

## 数据来源与复现

- 来源：公司 Skill 库 `https://skills.gz.cvte.cn/`（需 `cskills login` 扫码登录）
- 拉取工具：`cskills` CLI v5.9.4（`cskills add <name> --local --agent claude-code`）
- 拉取日期：2026-11-17
- 标签清单由脚本 `gen_manifest.py` 生成（见 `/tmp/gen_manifest.py`，可迁入仓库 `scripts/`）
