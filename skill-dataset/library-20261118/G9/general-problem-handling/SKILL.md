---
name: general-problem-handling
description: >-
  仅显式调用的问题排障流程 Skill。中心托管 Agent 在输入包含 execution_profile:
  managed-agent-v1，或同时存在后端 run_id、 受控工作目录和运行时守卫时可以自动使用。个人 Claude Code 或 Codex
  只有在用户明确点名 general-problem-handling、 $general-problem-handling、“通用问题排查
  Skill”或“标准排障流程”并要求使用时才可使用；普通的排查问题、定位 Bug、分析日志、 查看源码或诊断请求不得触发本
  Skill。用于证据化问题排查、根因定位和独立复审。
version: 1.5.1
author: luobin12754
---

# General Problem Handling

## 定位

这是问题排查的唯一入口和 profile 路由器。入口只负责选择一个执行契约并路由可选的共享业务语境，不内联任何 profile 的执行正文，以避免个人宿主误读中心模式规则。

## 显式调用门禁

本节是第一道门禁，必须在 profile 选择、personal 远端版本检查、业务语境询问、MCP/CSkills/obs-cli 调用或文件操作之前执行。

1. 当前输入显式包含 `execution_profile: managed-agent-v1`，或同时存在后端生成的 `run_id`、受控工作目录和运行时守卫约束时，视为托管宿主已经显式选择本 Skill，允许继续。
2. 其他情况均视为 personal 候选。只有当前用户请求明确要求使用以下任一入口时才允许继续：
   - `general-problem-handling` 或 `$general-problem-handling`；
   - “使用/调用通用问题排查 Skill”等明确指令；
   - “按标准排障流程处理”等明确指令；
   - 对本 Skill 无歧义的“继续使用这个 Skill”等上下文指代。
3. 仅出现“排查问题”“定位 Bug”“分析日志”“查看源码”“诊断原因”或其他普通排障意图，不算显式调用。
4. personal 未通过门禁时，立即停止执行本 Skill，不执行后续任何门禁、工具调用、提问或文件写入；改由宿主按默认能力处理当前请求。

## 先选择执行 profile

开始任何路由、采集或文件写入前，按以下优先级只选择一个 profile：

1. 输入显式包含 `execution_profile: managed-agent-v1`：选择 `managed-agent-v1`。
2. 未显式指定，但同时存在后端生成的 `run_id`、受控工作目录和运行时守卫约束：兼容选择 `managed-agent-v1`。
3. 其他由个人 Claude Code/Codex 直接发起的调用：选择 `personal-local-v1`。

两个 profile 必须执行同一个 `references/troubleshooting-core.md`，共用分类、业务 Skill 路由、obs-cli 语法、Git 代码来源、证据、推断、复审、失败收口和结论降级规则。profile 只定义运行环境与输出差异：personal 在当前会话完成并直接输出；managed 保留受控 run、强制多 Agent 角色门禁和结构化最终结果。

## 确认业务语境

该共享路由的执行时机由 profile 决定：managed 在进入其 reference 前执行；personal 必须先进入 `references/personal-local-v1.md` 并通过“必需工具硬门禁”，再按该 reference 的指令执行本节。personal 门禁通过前禁止询问业务语境。

确认问题是否属于“本地化 / 边缘 / 高职教”业务。这三个名称表示同一个业务语境：

1. 问题描述明确包含“本地化”“边缘”或“高职教”任一名称时，直接确认且不重复询问。
2. 问题描述未明确时，询问用户是否属于本地化/边缘/高职教业务。
3. 用户确认时，完整读取 `references/localized-business-conventions.md`，把其中内容作为有明确来源的默认上下文；两个 profile 共用同一份 reference，不得把内容复制进 profile reference。
4. 用户否认时跳过该 reference，继续执行已选 profile。

该业务语境路由不得替代现有 `get_trouble_categories` 分类、CSkills 名称解析或业务 Skill 加载。默认知识与用户明确输入或工具实际观测冲突时，以当前证据为准并记录冲突。

## 路由执行

- 选择 `personal-local-v1`：立即完整读取 `references/personal-local-v1.md`；其第 0 节远端版本检查和第 1 节工具门禁均通过后，才执行上方共享业务语境路由，并按该 reference 加载共享核心。
- 选择 `managed-agent-v1`：先执行上方共享业务语境路由，再完整读取 `references/managed-agent-v1.md`，并按该 reference 先只加载共享核心。

两个 profile reference 互斥，不得读取或混用未选 profile；`troubleshooting-core.md` 是两者唯一共享的执行正文。

## Reference 渐进加载红线

- 禁止对本 Skill 的 `references/` 执行 Glob、find、ls、目录遍历或“读取全部 reference”。
- 只能读取入口、所选 profile 或共享核心在当前步骤明确点名的精确相对路径。
- 不得把后续可能需要的 reference 提前并行加载；必须等触发条件实际成立后再读取。
- 已在本次会话完整读取的 reference 不重复读取。
