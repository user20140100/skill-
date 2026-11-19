---
name: windbg-dump-analysis
description: >-
  Windows dump 与快照分析技能 — 基于
  mcp-windbg/CDB，覆盖崩溃（访问违规/堆栈破坏/未捕获异常/并发时序）与死锁挂起（锁死锁/资源耗尽/阻塞/死循环）。环境自检、版本对齐、分级定位根因。任何
  Windows C/C++ 进程崩溃或卡死时使用。
metadata:
  author: huangzixuan
  version: 2.0.0
triggers:
  - 崩溃
  - crash
  - dump
  - deadlock
  - 死锁
  - hang
  - 挂起
  - 卡死
  - 无响应
  - windbg
  - cdb
  - analyze -v
  - access violation
  - 访问违规
  - terminate
  - abort
author: huangzixuan
version: 2.0.0
---

# WinDbg Dump Analysis 技能

> **核心哲学**：现场能直接告诉我们的往往很少。不要看栈就猜——先定问题类型（崩溃 vs 挂起），再用反向推理让现象与代码结构揭示根因。

## 何时使用

- 进程崩溃 / `std::terminate` → `abort`，有 dump（minidump / full dump）
- 访问违规、堆破坏、栈溢出、纯虚调用、CRT assert
- 偶发崩溃（依赖时序的 UB），开发机不现、低配 / 高负载 / 退出时序抖动时命中
- **死锁 / 挂起 / 卡死 / 无响应**（进程还在但不工作）
- 已拿到 dump，或需要对活进程取快照

## 何时不使用

- 构建错误 → 看编译日志
- 配置问题 → 查应用配置 / 日志
- 运行时逻辑错误但无崩溃 / 卡死 → 用动态插桩（日志 / 埋点）
- 纯性能问题（帧率低、卡顿但非死锁）→ 看应用的性能分析链路

## Hard Rules

1. **先定问题类型再分析** — 崩溃和挂起的现场、入口命令、推理路径都不同（见下表）。错配类型 = 走错路。
2. **先对齐版本再分析** — dump / 快照对应历史版本二进制，栈帧行号必须对上源码。跳过版本定位 = 看错代码。
3. **接住异常 ≠ 修好根因** — 缺边界 `try/catch` 只是把"可恢复异常"放大成"进程崩溃"的放大器。
4. **改好 ≠ 修好** — 时序 / 并发问题"跑几遍没崩 / 不卡"不能证明修复成立；必须从代码层面讲清根因。
5. **不在生产环境加 Sleep 调试** — 音视频实时性要求高。
6. **每个打开的 dump / remote 会话必须 close** — `close_windbg_dump` / `close_windbg_remote`，避免 CDB 进程残留。

## Step 0：环境自检

检测 mcp-windbg / CDB / Python / 符号路径。缺失则自动安装。决定走 MCP 工具还是 CDB CLI 兜底。

→ 详见 [`references/environment-setup.md`](references/environment-setup.md)

## Step 1：取得现场

两类问题的现场获取方式不同：

- **崩溃**：已有死亡 dump，或崩溃时自动生成的 minidump → 直接 `open_windbg_dump`
- **挂起**：活进程无现成 dump → 主动打断取快照（`open_windbg_remote` + `send_ctrl_break`，或 procdump / Task Manager）

→ 详见 [`references/windbg-tooling.md`](references/windbg-tooling.md)

## Step 2：版本定位（不可跳过）

从 dump / 快照模块信息反查代码版本，checkout 到该版本对齐符号 / 源码。分析不出版本 → 让用户确认，不擅自假设。

→ 详见 [`references/version-pinning.md`](references/version-pinning.md)

## Step 3：定问题类型 + 定级分析

### 问题类型快速判定

| 特征 | 崩溃 Crash | 挂起 Hang |
|------|-----------|-----------|
| 进程状态 | 已退出 | 还在 |
| 异常码 | 有（0xC0000005 等） | 无 |
| 现场 | 死亡 dump | 活进程快照 |
| 入口命令 | `!analyze -v` | `~*k` + `!locks` |
| 推理方向 | 从崩溃点反向 | 从所有线程状态找等待关系 |

### 分级判定（适用两类）

| 档位 | 判定 | 动作 |
|------|------|------|
| 简单 | 现场直接指向问题（栈指业务帧 + 明确非法访问 / 死锁环一目了然） | 直接定位 → 修复 |
| 中等 | 部分线索，需多步命令（`.ecxr` / `!heap` / `~*k` / `!locks` 构等待图） | 系统化分析 → 修复 |
| 复杂 | 现场信息少（无业务帧 / 泛型异常 / 等待关系不明显） | 走反向推理链 → 给分析思路 + 假设 + 验证方案，**不直接修** |

→ 详见 [`references/analysis-playbook.md`](references/analysis-playbook.md) + [`references/crash-deadlock-patterns.md`](references/crash-deadlock-patterns.md) + [`references/windbg-tooling.md`](references/windbg-tooling.md)

## Step 4：修复与验证

- 简单 / 中等：实施修复，运行测试 / 复现验证
- 复杂：输出分析思路 + 假设 + 验证方案，等用户确认方向后再修
- 验证标准：能从代码层面讲清根因，而非"跑几遍没崩 / 不卡"

## Step 5：工作流配合

本 skill 是通用的 dump / 快照分析能力，不假设目标项目环境。遇到以下情况，结合项目自身工具：

| 场景 | 建议 |
|------|------|
| 需要目标项目的领域知识（日志路径、模块结构、并发模式） | 查项目自带的调试文档 / skill |
| 时序 / 并发问题现场看不全 | 用动态插桩（日志 / 埋点）补运行时证据 |
| 修复涉及架构 / 契约变更 | 走项目的变更管理流程（若有） |
| 版本定位需要 checkout 历史版本 | 用 `git worktree` 建独立工作区，不污染主分支 |
| 修复后提交 | 遵循项目自身的提交规范 |

## 进度输出格式

证据先行，方便后续工程师接续：

````markdown
## Dump Analysis: [问题摘要]

### 1. 问题类型与现场
- 类型：崩溃 / 挂起
- 版本：X.Y.Z（git tag / commit，或"用户确认"）
- 现场关键：异常码 / 崩溃栈，或 挂起线程状态 / 等待关系

### 2. 分级与证据
- 定级：简单 / 中等 / 复杂
- 关键命令输出（`!analyze -v` / `~*k` / `!locks` 等）样本
- 证据证实 / 否定了什么

### 3. 根因（复杂档为"推理链 + 假设"）
- 一句话根因 / 最可能的 1-3 个假设
- 反向推理链（现象 → 前提 → 代码结构 → 验证）

### 4. 修复 / 分析思路
- 简单 / 中等：修复了什么 + 验证结果
- 复杂：假设 + 验证方案 + 建议修复方向（不直接改）

### 5. 清理
- [ ] 已 close 所有 dump / remote 会话
````

## 反模式

- **看栈就猜**：现场信息少时不要硬猜，走反向推理链
- **错配问题类型**：用崩溃路径分析挂起，或反之
- **跳过版本对齐**：用当前代码看历史 dump 的行号 = 看错代码
- **接住异常就当修好**：加 `try/catch` 只是止血，根因未治
- **死锁只看一个线程**：死锁是关系问题，必须 `~*k` 看全部线程 + `!locks` 构等待图找环
- **残留 CDB 会话**：忘记 `close_windbg_dump` / `close_windbg_remote`
- **把"理论上可行"说成"已验证"**：时序 / 并发问题必须讲清根因
