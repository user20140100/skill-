---
name: project-prd-writer
description: project-prd 内部附属写作引擎。把已经完成分类、行为清单和 Feature Point 拆解的代码基线，转换成逐 FP 的完整版产品需求文档；每个 FP 独立包含功能描述、交互、跳转、过程、正向限制、反向限制和异常提示。仅由 project-prd 初始化或 project-prd-edit 调用，不作为项目工作区管理入口。
---

# Project PRD Writer

将输入行为模型写成 `feature-points-v3` PRD。不要重新决定一级分类，也不要把无关用户目标合入同一文件。

## 必须读取

1. 完整阅读 [references/full-template-contract.md](references/full-template-contract.md)。
2. 使用随本 writer 固化的 [references/prd-template.md](references/prd-template.md) 作为唯一文档骨架。

## 输入契约

开始写作前必须已经具备：

- 产品、版本、代码基线和作者；
- `category`、共同的 `category_domain/category_goal/category_contract`，以及当前功能至少两项 `category_fit` 源码证据；
- 完整行为清单及源码证据；
- `complexity/complexity_reasons`；
- 连续编号的 `decomposition_candidates`、FP 清单，以及与 FP 一一对应的 `decomposition_basis`；每个 FP 恰好映射一个独立锚点候选；
- 每个 FP 的角色、触发、前置状态、动作、系统响应、正反向限制、异常、外部协作和清理；
- 现有测试或明确的自动化验证缺口。

输入缺项时返回给 `project-prd` 的分析阶段补齐，不得靠写作猜测。

## 初始化委派模式

由 `project-prd` 初始化子代理调用时：

- 只读取当前任务包、本文要求的模板契约，以及任务包 `source_scope` 精确授权的当前功能源码证据；不得读取其他任务包；不得读取其他 PRD 正文，也不得重新进行全项目分类。
- 只写入任务包指定的唯一目标文件；不得修改 INDEX、manifest、`.history/`、进度文件、其他任务包或其他 PRD，不得运行 `finalize` 或 `integrity`。
- 保持任务包给定的分类、FP 身份、Behavior、证据和目标路径；输入不完整时返回缺失字段，不得扩展读取范围或任务范围。
- 完成后只返回任务 ID、目标路径、状态、门禁摘要和缺失字段，不粘贴 PRD 正文。

通过 `project-prd-edit` 调用时继续遵循其受控草稿与原子替换流程，不使用上述初始化任务包路径。

## 写作流程

1. 写文档目的、产品定位、功能概览和术语表；概览与 FP 一一对应。
2. 按模块排列 FP，不改变 FP 身份和顺序。
3. 为每个 FP 独立、按固定顺序写完整七章节；不共享章节，不使用“同上”。
4. 将枚举映射、文案矩阵、拦截顺序、倒计时、异步等待、取消恢复和清理写到对应 FP，保留代码能证明的具体数值和系统表现。
5. 写整体闭环；`complex` PRD 每个 FP 使用独立 Mermaid 节点，全部节点参与同一连通流程，decision 至少有两条带标签出边。
6. 审计枚举映射、状态、优先级、文案、策略和权限矩阵；代码项使用证据范围中的真实 token/表达式并覆盖 enum/case/命名规则集合，状态/优先级/策略保持顺序。
7. 为每个 Behavior 标注 FP、源码证据、用户可感知行为和章节；`source_entries` 等于源码证据去重集合。
8. 逐 Behavior 映射真实测试；没有测试时写清缺失范围。
9. 把源码 TODO、未实现策略和待产品确认项集中写入“已知缺口与待确认项”，不得写成已实现需求。

## 完成门禁

- 每个独立触发、阶段、策略、交互矩阵、外部协作和清理闭环都有 FP；达到最低数量不代表拆解完成。
- 每个 FP 恰好承接一个锚点候选；候选、异常和规则矩阵证据均由同一 FP 的 Behavior 覆盖。
- 相同 kind 与相同源码范围不得改名后重复拆成多个 FP。
- `complex` PRD 恰好有一张覆盖所有 FP 的 Mermaid 流程图。
- 每个 FP 的七章节按顺序恰好一次，交互及三类表格均非空。
- 全文覆盖空态、操作失败、网络异常、权限不足和边界超限；不适用时给出证据。
- 每个 FP 至少有一个 Behavior；standard/complex 的每个 FP 同时具有主路径与限制/异常 Behavior；每个 Behavior 有验证依据。
- 仅写证据支持的现有行为；保持产品语言，不复制实现代码。
