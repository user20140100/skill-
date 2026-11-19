# 完整代码与测试靶场仓库

> 课题：AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统
> 本目录为交付物 #2 的说明文档，实际代码分布在仓库各目录，此处给出可复现说明。

## 一、交付物组成（对照课题要求）

| 课题要求 | 对应位置 | 状态 |
|---|---|---|
| 3 个自建测试 Skill（正向 / 冗余冲突 / 安全靶场） | `skill-dataset/`（positive / redundant / security） | ✅ 已就绪（48 个，含 3 类） |
| 自定义安全规则配置/代码（≥2 条） | `custom-rules/`（规则 A/B + `select.yaml` 灰度开关） | ✅ 已就绪 |
| 一键批处理脚本（Python） | 待建 `scripts/` | ⬜ 待补充 |
| 可复现 README | 本文档 + `skill-dataset/README.md` | ✅ 本文档 |

## 二、测试靶场 Skill 说明

数据集共 48 个 Skill，从公司内部 Skill 库 `https://skills.gz.cvte.cn/` 拉取并打标签，分类如下（详见 `skill-dataset/README.md` 与 `manifest.json`）：

| 分组 | 数量 | 用途 | 预期 |
|---|---|---|---|
| `positive/` | 11 | 正向业务 Skill | Tier1 pass / Tier2 pass / Tier3 增益 yes |
| `redundant/` | 30（8 组） | 冗余冲突 Skill，测试语义去重拦截 | Tier2 dup（应被拦截） |
| `security/` | 7 | 含敏感操作（SSH/凭证/SQL/日志） | Tier1 flag（触发安全关注） |

> 课题要求「3 个测试 Skill」，本项目为提升覆盖度扩展为 48 个，其中 3 类各取代表性 Skill 用于答辩演示。

## 三、环境与依赖

- **平台**：macOS Monterey 12.7.6
- **Docker**：Docker Desktop 4.37.1（DaoCloud 镜像源）
- **Python**：3.12+，使用 `uv` 管理
- **LLM**：token.cvte.com 网关（注意：该网关无 embedding 模型，Tier 2 需另配 embedding 来源）
- **扫描器**：SkillSpector（71 规则 / 17 类）+ Gitleaks + Semgrep（可选）
- **沙盒**：Harbor / Docker

## 四、运行方式

### Tier 1 静态安全扫描（SkillSpector）

```bash
skillspector scan ./skill-dataset/security/xxx --no-llm
skillspector scan ./skill-dataset/security/xxx --format json --output report.json
```

### 三层评估（SkillEvaluator）

```bash
uv run --python 3.13 --extra all skillevaluator doctor --env-mode docker
uv run --python 3.13 --extra all skillevaluator validate ./skill-dataset/positive/xxx
```

### 一键批处理（任务 B，待实现）

```
python scripts/batch_scan.py --dir ./skill-dataset --output reports/
```

## 五、待补充清单

- [x] 任务 A：在 SkillSpector 上实现 ≥2 条企业自定义规则（已落地 `custom-rules/`，验证见 `03-现场演示与复盘/规则A证实报告.md`、`规则B证实报告.md`）
  - 规则 A：域名白名单放行（抑制层 `allow_domain`，放行发往企业白名单域名的外发 finding，不新增告警）
  - 规则 B：禁止明文凭证内嵌命令行 / 连接串（`cvte_credential_inline.yar`）
- [ ] 任务 B：编写 `scripts/batch_scan.py` 一键批处理脚本
- [ ] 阶段四：Skill 问题自动修复（参考 SEG 闭环）

## 六、复现注意事项

- 本机导出架构图/图表需用系统 Chrome（见 `03-现场演示与复盘/排障笔记.md`）
- Tier 2 的 embedding 依赖需单独配置（网关无 embedding 模型）
- Tier 3 会产生 LLM API 费用，答辩前需控制用例规模
