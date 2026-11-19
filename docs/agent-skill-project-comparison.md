# AI Agent Skill 审查与评估项目对比

> Star、Fork 数为 2026-11-16 查询时的数据，可能变化。  
> “缺失”指项目文档中未见明确内置该功能，不代表无法自行集成。

## 表 1：Skill 审查与评估框架

| 推荐顺序 | 项目 / 重要信息 | 已覆盖的课题需求 | 相比课题要求的缺失部分 | 超出课题要求的功能 |
|---:|---|---|---|---|
| 1 | [NVIDIA/SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) · 2,241★ / 295 Fork · Python · Apache-2.0 | 覆盖三项：Tier 1 质量与安全检查；Tier 2 语义重复/重叠检测；Tier 3 使用 Agent 和 Docker 沙盒评估 Skill 对 Agent 行为的影响。配套使用 SkillSpector 和 Harbor。 | 未见内置联网搜索并推荐替代 Skill；未见自动修复。Tier 2 跨 Skill 比较需要准备 Skill catalog；Tier 3 需配置 Agent、模型和沙盒，可能产生 API 费用。 | 质量评分、评估样例/数据集生成、CLI 和 CI 集成、报告及性能比较。 |
| 2 | [SkillLens-AI/skilllens](https://github.com/SkillLens-AI/skilllens) · 3★ / 0 Fork · Python · Apache-2.0 | 覆盖安全与效果评估：生成效用和安全测试，在 Harbor/Docker 沙盒中执行；以有 Skill/无 Skill 对照评估 `pass_rate_gain`，并判断对抗场景下的安全表现。 | 未见内置 Skill 间语义去重；未见完整通用的企业自定义扫描规则机制；未见在线替代推荐或自动修复。需要配置 Docker、Agent 和模型 API。 | 同时评估效用、安全和效率；可生成测试任务、记录 Agent 轨迹、重审判定结果，并提供浏览器扩展和已评估 Skill 报告查询。 |
| 3 | [metahub-ai/assay](https://github.com/metahub-ai/assay) · 12★ / 1 Fork · TypeScript · Apache-2.0 | 覆盖静态检查和沙盒行为评估：模型驱动 Skill 测试、独立 judge 评判，并生成可复核报告。 | 未见内置 Skill 间语义去重；未见明确的有 Skill/无 Skill 任务完成率增益对照；未见在线替代推荐或自动修复。面向多类 AI artifact，并非专用 Skill 三层评估框架。 | 报告签名/验证、覆盖率和证据记录、检查规则扩展、CI/SARIF 集成，以及依赖风险检查。 |
| 4 | [Luce-Florian/proctor](https://github.com/Luce-Florian/proctor) · 0★ / 0 Fork · TypeScript · MIT | 主要覆盖效果评估：可编写测试套件，在独立沙盒中运行 Agent/Skill，使用确定性断言或 LLM judge，并进行 baseline ablation。 | 未见内置 Skill 安全扫描和跨 Skill 语义去重；未见在线替代推荐或自动修复。需要自行补充安全扫描和去重环节。 | xUnit 风格试验生命周期、CTRF/Markdown/HTML 报告、测试变体和 Agent 无关的评估 harness。 |

## 表 2：Agent Skill 安全扫描器

> 安全扫描器通常不负责完整的 Skill 去重和任务效果增益评估，不能单独替代表 1 的流水线框架。

| 推荐顺序 | 项目 / 重要信息 | 已覆盖的安全审计需求 | 相比课题完整审查方案的缺失部分 | 超出课题安全扫描要求的功能 |
|---:|---|---|---|---|
| 1 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) · 26,351★ / 2,338 Fork · Python · Apache-2.0 | 面向 Agent Skills 的专用扫描器，支持静态分析和可选 LLM 语义分析；覆盖提示注入、数据外泄、凭证访问、越权、供应链风险和脚本行为等；支持 JSON、Markdown、SARIF 和目录批量扫描。也是 SkillEvaluator Tier 1 配套扫描器。 | 本身不负责 Skill 效果增益评估；跨 Skill 去重应交给框架或其他组件；未见内置联网替代推荐或自动修复。域名白名单、敏感路径等企业规则需按其扩展机制验证和实现。 | LLM 深度分析、风险评分、误报基线/抑制、MCP 扫描接口及 OpenCode 等集成、多种审计报告格式。 |
| 2 | [Cisco AI Defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) · 2,734★ / 347 Fork · Python · README 标注 Apache-2.0（GitHub API 的 license 字段显示为 Other，采用前建议核对仓库 LICENSE） | 多引擎安全扫描：规则/YARA、AST/数据流和可选 LLM 语义分析；支持自定义策略/规则、HTML/SARIF 报告和批量扫描。另有 `scan-all --check-overlap`，可检查 Skill 描述重叠。 | 重叠检查不等同于完整语义冲突判定；未见沙盒下的 Skill 有/无对照和任务完成率增益评估；未见联网替代推荐或自动修复。与 SkillEvaluator 的集成需自行实现。 | 多种扫描策略和规则包、CI 与 pre-commit 集成、HTML 交互报告，并可组合 VirusTotal、OSV 或云端分析能力。 |
| 3 | [NMitchem/SkillScan](https://github.com/NMitchem/SkillScan) · 9★ / 1 Fork · Python · MIT | 三阶段安全检测：静态规则扫描、LLM 行为预测、Docker Sandbox 实际执行；使用蜜罐凭证检测读取/外传行为；支持 YAML 规则和 JSON/SARIF 输出。 | 沙盒测试是安全行为检测，不等同于任务效果增益评估；未见跨 Skill 语义去重、联网替代推荐和自动修复。其沙盒测试要求 Docker Desktop 4.58+ 和 Sandbox 插件，需在目标 Mac 上确认。 | 延迟触发/多步骤风险预测、macOS 特定风险检测、蜜罐凭证和沙盒运行时监测。 |

## 综合选型建议

- **主框架：NVIDIA SkillEvaluator**，最直接覆盖课题要求的三层流程，并配套 SkillSpector。
- **安全扫描器：NVIDIA SkillSpector**，与主框架搭配的集成成本最低；可将 Cisco Skill Scanner 用作扫描能力对照。
- **效果评估参考：SkillLens**，借鉴有/无 Skill 对照和 `pass_rate_gain`，说明 Skill 是否提升任务表现。
- **动态安全检测参考：SkillScan**，其沙盒和蜜罐设计可补充安全靶场演示，但不能把安全测试结果当成任务完成率提升证据。

安全扫描、语义去重和效果增益是不同结论，建议在报告中分别记录，不合并成单一分数。沙盒评估也只能说明已覆盖测试中的行为，不能证明 Skill 在所有条件下安全。