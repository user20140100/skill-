---
name: project-prd
description: >-
  从现有项目代码提炼、制定并初始化受保护的逐功能 PRD 基线。首次调用时全量分析项目，由主代理建立功能清单和证据任务包，再为每份细分功能 PRD
  委派全新的独立子代理生成，避免正文占满主代理上下文；同时安装
  project-prd-edit、project-prd-verify、project-prd-clear、project-prd-serve 四个项目级
  skill，并向 AGENTS.md 写入 PRD 保护规则。用于“生成项目 PRD”、“提炼全部功能需求”、“初始化
  project-prd”或建立代码修改与 Review 依据；已初始化时必须停止并提示使用 edit、verify、clear 或 serve。
version: 3.1.3
author: yangyuebin
triggers:
  - /project-prd
  - project-prd
  - 生成项目 PRD
  - 初始化 project-prd
  - 初始化项目 PRD
  - 提炼全部功能需求
  - 从代码生成 PRD
  - 建立 PRD 基线
  - 建立需求基线
  - 代码功能盘点并生成 PRD
requires:
  - python3
---

# Project PRD

从现有代码建立一次性、逐功能的 PRD 基线。PRD 采用内置、版本锁定的 `project-prd-writer` 模块/功能点结构：复杂功能先无损拆成多个 Feature Point，再为每个 FP 完整重复七章节，并保留源码追溯和测试证据。主代理只负责全局分析、任务包、调度和最终门禁；每份细分功能 PRD 必须委派给一个全新的独立子代理，主代理不得亲自撰写 PRD 正文。

## 入口

1. 将当前工作目录解析为单一项目根目录，并确认运行时具备子代理委派能力；不支持创建子代理或没有任何可用子代理槽位时返回 `BLOCKED`，禁止回退为主代理撰写正文。禁止对主目录、多个仓库的共同父目录或不明归属的路径执行。
2. 运行：

   ```bash
   python3 <本 skill 目录>/scripts/bootstrap.py status --project-root <项目根目录>
   ```

3. 状态为 `initialized` 时立即停止，提示项目已初始化；同步项目级 skill 和 runtime 使用 `bootstrap.py update`，修改 PRD 或 `.project-prd` 内普通资源使用 `project-prd-edit`，验证使用 `project-prd-verify`，重新初始化必须先调用 `project-prd-clear`。`update` 不负责发现、迁移或登记资源。
4. 状态为 `partial` 且 `resumable: true` 时，不再运行 `prepare`；读取 `.project-prd/.analysis/progress.json` 并按未完成任务续跑。进度文件缺失或损坏会得到 `resumable: false`，此时停止并要求先用 `project-prd-clear` 清理来源不明或损坏的残留。
5. 仅在状态为 `clean` 时进入初始化。

## 初始化流程

1. 完整阅读 [references/initialization-workflow.md](references/initialization-workflow.md)。
2. 运行 `bootstrap.py prepare`，先安装四个项目级 skill、`.project-prd` 工作区、完整性门禁和 AGENTS.md 受管规则。
3. 按 [references/feature-analysis.md](references/feature-analysis.md) 全量分析项目自身源码，先建立带 `category_domain/category_goal/category_contract` 的分类契约，并为每个成员记录至少两个 `category_fit` 源码证据，再建立一级功能分类和二级细分功能。单成员分类合法，不得按数量或技术邻近强行聚合。
4. 按 [references/prd-extraction.md](references/prd-extraction.md) 为每个细分功能建立行为清单和 `decomposition_candidates`，将独立触发、阶段、策略/拦截、交互矩阵、外部协作和恢复/清理无损拆成 Feature Point。
5. 主代理按 [references/initialization-workflow.md](references/initialization-workflow.md) 的委派契约，为每个细分功能生成 `.project-prd/.analysis/tasks/<task-id>.md`，并在 `.project-prd/.analysis/progress.json` 记录状态。任务包只包含该 PRD 的分类契约、行为、Feature Point、规则矩阵、证据和验证输入，不放入其他 PRD 正文。
6. 每份细分功能 PRD 必须委派给一个全新的独立子代理。子代理读取任务包和内部附属写作引擎 [assets/internal-skills/project-prd-writer/SKILL.md](assets/internal-skills/project-prd-writer/SKILL.md)，只写入 `.project-prd/<功能聚合分类>/<细分功能>.md` 这一唯一目标文件，并仅返回精简状态；不得写 INDEX、manifest、进度文件或其他 PRD。同一子代理不得处理第二份 PRD。
7. 主代理只根据子代理状态更新进度；失败项使用新的子代理按原任务包和精简错误重试，不把完整正文读回主上下文。全部任务完成后再创建 `.project-prd/INDEX.md` 草稿并执行全局校验。
8. 对每份 PRD 执行复杂度和覆盖门禁。每个 FP 必须完整套用 `prd-writer` 七章节；`complex` PRD 必须生成一张覆盖全部 FP 的 Mermaid 业务流程图；代码枚举、状态、优先级、文案和策略必须进入规则矩阵覆盖审计。
9. 运行：

   ```bash
   python3 <本 skill 目录>/scripts/bootstrap.py finalize --project-root <项目根目录>
   python3 <项目根目录>/.project-prd/tools/project_prd_guard.py integrity --project-root <项目根目录>
   ```

10. 仅在所有子代理任务为 `completed` 且两个命令都成功时宣告完成。报告功能分类数、PRD 数、Feature Point 数、交互步骤、正反向限制、异常项、行为覆盖数、复杂度分布、失败重试数、未归类文件和安装的门禁。结论报告必须单列功能覆盖率，使用 `covered / total × 100%`，同时展示已覆盖细分功能数、已识别细分功能总数和未覆盖功能清单；分子、分母以 `finalize` 输出的 `feature_coverage` 为准，不得自行估算或只写百分比。

## 强制约束

- `project-prd` 在同一项目只能成功执行一次，与 `project-spec` 互不影响。
- 初始化写作阶段严格执行“一份 PRD 一个独立子代理”；主代理不得为了赶进度直接补写正文，也不得让一个子代理连续处理多份 PRD。
- 子代理只拥有一个目标文件；主代理独占任务包、进度、INDEX、manifest 和 `finalize`，从而避免并发写冲突。
- 初始化完成后，任何 Agent 都不得直接增删改 `.project-prd`；只能调用 `project-prd-edit`。
- 所有代码修改、单元测试和 Code Review 必须遵守相关 PRD；所有 Review 必须调用 `project-prd-verify`。
- PRD 仅记录代码、测试、公开契约或项目文档能支撑的已有行为。无法从证据确认的用户痛点、业务价值、文案或产品意图必须标为待确认，禁止臆造。
- 对不存在页面、网络或权限概念的功能，在对应 PRD 项写明“不适用”及证据，不得虚构行为也不得省略该类别。
- 异常、超时、权限和展示方式必须逐行绑定到具体 Symbol 或行号范围；校验只读取该范围并排除注释，同文件其他函数不能代为背书。
- 不把第三方依赖、构建产物、部署脚本或纯实现细节当作用户功能。
- 初始化失败时保留现场并说明失败步骤；不得绕过校验写入完成标记。

## 清理

仅允许项目级 `project-prd-clear` 清理工作区。该操作会删除全部 PRD 与审计历史，必须先获得用户对当次清理的明确确认。
