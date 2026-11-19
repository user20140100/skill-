# 门禁模型

## PRD 完整性门禁

初始化期间，全部单文件任务必须在 `.project-prd/.analysis/progress.json` 中处于 `completed`，任务目标与磁盘 PRD 一一对应，历史 attempt 均已终止，且所有 attempt 使用互不重复的子代理，才能由主代理进入跨 PRD 校验、INDEX 生成、`finalize` 与 `integrity`。任务包必须通过完整 frontmatter schema、PRD 身份、writer/template 固定路径和项目内 `source_scope` 门禁；PRD、任务目录、任务包及源码范围的路径链均不得包含符号链接。`prepare` 记录受管 runtime、writer、项目级 skills、AGENTS 规则块和 GitHub workflow 的 SHA-256；续跑与 finalize 前任一资产指纹失配都必须拒绝。子代理不得执行这些全局操作，单文件成功也不能替代全局门禁。

`.project-prd/manifest.json` 保存所有 PRD、普通资源文件和索引文件的 SHA-256。资源可位于任意相对目录、使用任意文件类型，并按原始字节哈希。`project-prd-verify` 与 GitHub Action 首先检查：

- 哈希不一致且没有 edit 审计记录 → FAIL。
- PRD 缺失、新增或移动但清单未更新 → FAIL。
- PRD 缺少文档级结构，或任一 Feature Point 未按固定顺序完整包含 `prd-writer` 七章节 → FAIL。
- 一级分类成员的 domain/goal/contract 不一致、共同有证据的 fit 维度少于两个，或使用无业务语义兜底分类 → FAIL。
- 复杂度与交互、限制、行为覆盖的完整度显著不匹配 → FAIL。
- `decomposition_candidates` 不连续、一个 FP 合并多个独立锚点、候选证据不在同 FP Behavior 中，或 `decomposition_basis` 与 FP 未一一对应 → FAIL。
- complex PRD 没有唯一 Mermaid flowchart、一个节点压入多个 FP、FP 节点未参与/未连通，或 decision 没有两条带标签分支 → FAIL。
- 规则矩阵代码项不在证据范围、漏掉源码 enum/case/规则集合、与 PRD 项不一致、该有矩阵却写 MX-NONE，或异常/矩阵证据未被同 FP Behavior 覆盖 → FAIL。
- 同一 kind 与源码范围被重复声明为多个锚点候选 → FAIL。
- 异常条件或展示方式在所引 Symbol/行号范围中没有实现信号，FP 没有完整主路径和边界 Behavior，Behavior 引用未知 FP，或 `source_entries` 与行为证据集合不一致 → FAIL。
- INDEX 不是由当前 PRD 元数据规范生成，或 manifest 统计不一致 → FAIL。
- owner、运行时工具、审计记录哈希异常，或 generation/前后哈希链不连续 → FAIL。

## 受控编辑门禁

`project-prd-edit` 不允许 Agent 直接写目标 PRD 或资源。Agent 在 `.project-prd` 外准备完整草稿，再调用 `apply_prd_change.py`。脚本负责：

- 将恰好两级的 Markdown 路径识别为 PRD；将控制面之外的其他普通文件识别为资源，并保留资源原始字节。
- 校验 `prd-writer` 逐 FP 完整结构、分类契约、复杂度与行为覆盖。
- 单文件变更原子替换；分类契约、跨分类移动及 PRD/资源联动使用一次多文件事务，任一项失败时整体回滚。
- 重建 INDEX 和哈希清单，并为整组事务写入一条 `.project-prd/.history/` 审计记录。

`bootstrap.py update` 只同步项目级 skill 和 runtime，不扫描、迁移、登记或输出资源。既有未登记资源由 `project-prd-edit` 的明确目标单独接管，不能靠修改 manifest 或运行 update 获得授权。

审计记录用于发现普通 Agent 绕过和形成 Review 证据，不是安全签名。

## Code Review 语义门禁

哈希只能保护 PRD 文件，不能证明代码语义。每次 Review 必须由 `project-prd-verify`：

1. 找出代码和测试差异。
2. 通过 INDEX、`source_entries` 和 Behavior ID 选择受影响 PRD。
3. 检查功能描述、交互、跳转、限制、异常或闭环是否改变。
4. 检查单元测试是否覆盖 PRD，且未被削弱。
5. 运行受影响的最小可靠测试集。
6. 输出 PASS、FAIL 或 BLOCKED；证据不足不得输出 PASS。

## GitHub 门禁

对 GitHub 仓库，初始化脚本安装受管 `pull_request_target` workflow。它以只读权限检出 PR head，但从 base commit 提取可信的 guard 和 library 执行校验，不执行项目代码。

已初始化项目的普通 PR 不得修改 project-prd runtime、项目级 skills 或 workflow。每个 PRD 变更必须有 target 匹配的 `authorized-prd-edit` 记录。要防止绕过合并，需在 GitHub Ruleset 中将该 check 设为 required。首次引入 workflow 的 PR 仍需人工 Review，因为 base 分支尚不存在该 workflow。
