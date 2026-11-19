---
name: cxx-style-review
description: C/C++ 编码规范审查技能。用于提交前检查，或按用户指定的文件、目录、patch 范围执行规范审查，并输出结构化 findings。
version: 1.1.2
author: guozilong
tags:
  - c++
  - code review
  - coding style
  - pre-commit
---

# C/C++ 提交前规范审查

## 目标

对当前变更，或用户显式指定的文件、目录、patch，做一次 C/C++ 编码规范审查。

该技能的重点是：
- 不污染主编码阶段的上下文。
- 只在明确要求规范审查时触发，不在中间迭代阶段自动触发。
- 只输出可执行的 findings，由主 agent 决定是否修复。

## 触发边界

在以下场景可触发：
- 用户明确表示准备提交、提交前检查、最终 review、pre-commit review、收尾检查。
- 用户明确要求检查某个 C/C++ 文件、目录或 patch 是否符合团队规范。

以下场景不要触发本技能：
- 日常编码、调试、重构过程中的中间轮次修改。
- 普通 C++ 知识问答、语法解释、性能分析。
- CMake、工程骨架、组件化设计问题。

如任务目标不是规范审查，而是实现、调试或工程设计，应交由更匹配的通用开发流程处理。

## 审查输入

优先使用最小必要输入：
- 默认：当前变更文件列表。
- 默认：当前 diff。
- 若用户显式指定文件、目录或补丁，则以用户指定范围为优先审查范围。
- 与 findings 直接相关的少量上下文代码。

范围优先级：
- 用户未指定范围时，默认审查当前 `git diff` 对应内容，并且只局限于改动内容，不能包括文件中未改动的历史代码，除非历史代码对本次变更有直接影响。
- 用户显式指定文件、目录或补丁时，默认优先审查用户指定范围。
- 若用户同时要求“检查指定文件 + 当前 diff”，则把两者合并为本次审查范围，并在输出中说明。

除非定位问题必须，不要通读整个仓库。

## 规范资料加载与分片选择

以下 `references/...` 路径均指当前 skill 目录下的相对路径，即相对于包含本 `SKILL.md` 的目录解析，而不是相对于当前工作目录解析。若平台提供 skill path 或 metadata，应优先据此定位当前 skill 目录。

- 运行时只允许读取 `references/cpp-style-spec/` 下的拆分版规范文件。
- 禁止把 `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md` 作为运行时审查输入；该原文仅用于规范维护、覆盖核对、后续版本迭代。
- 优先按变更类型选择最小文档集合；只有在无法判断时，才先读 `references/cpp-style-spec/INDEX.md`。

变更类型与优先加载分片映射如下：

| 变更类型 | 优先加载的规范分片 |
| --- | --- |
| 改命名、重命名、接口命名不统一 | `references/cpp-style-spec/style-naming.md` |
| 改空格、括号、换行、缩进 | `references/cpp-style-spec/style-formatting.md` |
| 改文件头、函数注释、行内注释 | `references/cpp-style-spec/style-comments.md` |
| 改头文件、自给自足、include 顺序 | `references/cpp-style-spec/practice-files.md` |
| 改宏、平台分支、条件编译 | `references/cpp-style-spec/practice-macros.md` |
| 改 `if` / `switch` / `for` / `while` | `references/cpp-style-spec/practice-control-flow.md` |
| 改函数长度、返回策略、线程创建、日志 | `references/cpp-style-spec/practice-functions-and-general.md` |
| 改命名空间、类、异常、智能指针、资源释放 | `references/cpp-style-spec/practice-cpp-specific.md` |
| 改整数类型、边界、内存、线程安全、随机数 | `references/cpp-style-spec/safety-types-and-data.md`、`references/cpp-style-spec/safety-resources.md`、`references/cpp-style-spec/safety-threading-and-build.md` |

如果一个变更同时涉及多个主题，可组合加载多个分片，但保持最小集合。

## 推荐工作流

### 1. 确认是否属于规范审查场景

如果用户尚未表达“准备提交”或明确指定 C/C++ 文件、目录、patch 做规范检查，不要主动拉起规范审查。

### 2. 收集最小审查范围

优先收集：
- 用户未指定范围时：`git diff --name-only`
- 用户未指定范围时：`git diff --stat`
- 必要时的逐文件 diff
- 用户显式指定文件、目录或 patch 时：优先按用户指定范围收集审查输入，并在输出中注明检查范围来源

如果变更与 C/C++ 无关，直接说明本技能不适用。

### 3. 选择规范分片

根据上面的“规范资料加载与分片选择”选择最小文档集合；如果变更横跨多个主题，可以组合加载多个分片，但不要为求保险而整套全读。

### 4. 使用高性价比 subagent 做审查

如果当前环境允许启动 subagent，优先选择当前平台中可用、成本较低且足以完成规范审查的模型。

选择原则：
- 优先遵从用户当前平台/供应商的可用模型生态，不绑定特定厂商或系列。
- 如果当前环境是 Codex 且 `gpt-5.2` 可用，则优先使用 `gpt-5.2`。
- 在保证审查质量前提下，优先选择高性价比模型。
- `reasoning_effort` 默认可设为 `high`；若平台无该概念，则选择等价的较高审查强度配置。

subagent 任务边界：
- 只做规范对照审查。
- 不直接做大规模代码修改。
- 不回滚他人改动。
- 输出 findings 列表，而不是长篇泛化解释。

如果当前环境不能使用 subagent，再由主 agent 本地完成同样流程。

### 5. 输出结构化 findings

每条 finding 尽量包含：
- severity: `high` / `medium` / `low`
- file: 文件路径与行号
- rule: 规则编号或规则主题
- issue: 问题描述
- suggestion: 修复建议

无问题时，明确写“未发现需要在提交前阻断的规范问题”，并说明检查范围。
最终输出应注明本次检查范围来源：`git diff`、用户指定范围，或两者组合。

## 审查原则

- 优先报告真实会影响可维护性、安全性、一致性的规范问题。
- 避免把纯个人风格偏好伪装成硬性规则。
- 如果原规范本身存在表述歧义，明确标注“按当前文档理解”。
- 同一问题不要重复报多次，可合并为同类问题。
- 对明显由历史代码遗留造成、且本次未触及的区域，不要扩大化审查。

## 与主 agent 的协作边界

本技能负责：
- 选择规范分片。
- 执行提交前审查。
- 输出 findings。

本技能不负责：
- 在未获授权时直接改代码。
- 替代主 agent 做完整实现。
- 在中途迭代阶段频繁打断开发流程。
