---
name: code-review
description: >-
  Perform Bytello C++ code reviews with findings-first output. ALWAYS use this
  skill when users ask for 代码评审/CR/review/check changes in C/C++ projects, and
  MUST fully read coding-rules/for-human/cpp/README.md and
  coding-rules/for-human/project/README.md before producing any findings.
version: 1.0.3
author: zhangfan3427
---

# Bytello C++ 代码评审 Skill

用于 Bytello C++ 项目的代码评审，关注功能正确性、工程规范一致性和可维护性。

## 触发时机

- 用户提及“代码评审 / 评审一下 / CR / review changes / 看下这次改动”
- 用户提供 PR、MR、diff、提交记录并要求质量检查
- 用户希望在合并前确认是否符合团队规范
- 当前仓库为 C/C++ 项目，且评审目标受 Bytello 编码/工程规范约束

非目标场景：纯前端/Python/Go 等非 C/C++ 项目默认不触发本 skill。

混合语言仓库：仅评审本次改动中与 C/C++ 工程相关的文件；若改动包含 Python/CMake 文件，则仅对这些文件执行对应格式化/工程检查。

## 评审前置要求（强制）

在任何评审输出前，若未经过人工审查，须完整阅读以下两份规范（从首行到 EOF）：

1. `coding-rules/for-human/cpp/README.md`（编码规范）
2. `coding-rules/for-human/project/README.md`（工程规范）

执行要求：

- 若之前有进行过人工审查，则跳过该步骤，不再读取这两份文件。
- 必须是完整阅读，不允许只看目录或抽样片段
- 若读取工具有行数上限，必须分段读取直到文件结束
- 两份规范未完整读取前，禁止输出评审结论，且禁止开始差异分析

### 规范路径解析（强制）

按以下顺序解析规范路径：

1. 当前工作区相对路径：
   - `coding-rules/for-human/cpp/README.md`
   - `coding-rules/for-human/project/README.md`
2. 若第 1 步不存在，则尝试当前仓库相对路径：
   - `for-human/cpp/README.md`
   - `for-human/project/README.md`
3. 若第 1/2 步仍无法定位，则直接在当前项目同级目录克隆规范仓库：

```bash
git clone git@gitlab.gz.cvte.cn:OSCore/screenshare/base_library/coding-rules.git ../coding-rules
```

4. 克隆后从以下路径完整读取规范：
   - `../coding-rules/for-human/cpp/README.md`
   - `../coding-rules/for-human/project/README.md`

5. 若克隆失败，输出失败原因并停止评审

在规范路径未确认前，不得产出任何评审 findings。

## 评审流程

1. 收集评审范围（PR/MR diff、变更文件、关联上下文；若存在明确 PR/MR diff，则以该范围为准，否则以本地 staged + unstaged 变更集合为准）
2. 先执行格式化检查（仅检查本次改动的对应文件，不做自动修复）
3. 再做正确性审查：崩溃/越界/空指针/资源泄露/并发问题/行为回归
4. 再做工程规范审查：构建、依赖、目录结构、Git 与质量工具规范
5. 再做编码规范审查：命名、作用域、注释、流程控制、C++惯用法
6. 检查测试覆盖与验证证据（是否有对应单测/验证步骤）
7. 形成 findings-first 输出（高到低严重级别）

### 格式化检查步骤（强制）

按改动文件类型执行对应检查（check-only）：

1. C/C++ 文件（`*.c`/`*.cc`/`*.cpp`/`*.h`/`*.hpp`/`*.mm`）

```bash
clang-format --dry-run --Werror <changed_cpp_files>
```

2. Python 文件（`*.py`）

```bash
ruff format --check <changed_py_files>
```

3. CMake 文件（`CMakeLists.txt`、`*.cmake`）

```bash
cmake-format --check <changed_cmake_files>
```

执行规则：

- 只检查本次改动文件，不对全仓执行
- 仅对存在对应改动文件类型的命令执行；该类型无改动文件则跳过
- `clang-format` 找不到时，按以下顺序尝试恢复（仅 Windows）：
  1. 执行 `Import-VisualStudioVars 2022 -Architecture x64`，然后重试
  2. 若 `Import-VisualStudioVars` 不可用，先安装并导入模块后重试：
     ```powershell
     Install-Module -Name PSCX -AllowClobber -Scope CurrentUser
     Install-Module -Name VSSetup -AllowClobber -Scope CurrentUser
     Import-Module Pscx
     Import-Module VSSetup
     Import-VisualStudioVars 2022 -Architecture x64
     ```
  3. 仍然失败则记录为"环境缺失"，在评审结论中记为 High
- 非 Windows 环境下 `clang-format` 不存在时，直接记录为"环境缺失"并记为 High
- `ruff` / `cmake-format` 不存在时，仅在存在对应类型改动文件时记录为"环境缺失"并记为 Medium
- 评审阶段禁止自动格式化改文件，仅报告检查结果

## 重点检查清单

### A. 正确性与风险

- 是否存在潜在崩溃路径、未定义行为、线程安全问题
- 是否引入接口语义变化但缺少兼容处理
- 是否出现错误处理遗漏（异常、返回值、边界条件）

### B. 工程规范一致性（`project/README.md`）

- CMake 与 Conan 规则是否满足（版本、target 化、构建类型、依赖管理）
- 是否有违反“构建产物安装、目录结构、格式化范围、提交流程”等规则的改动
- 是否缺失必要的测试、质量门禁或构建脚本更新

### C. 编码规范一致性（`cpp/README.md`）

- 头文件、命名、类设计、函数接口、注释风格是否符合规范
- 是否违反“必须”项（例如流程控制括号、禁止裸 `printf` 留存、智能指针规范等）
- 是否存在明显可维护性问题（过深嵌套、魔数、可读性差表达式）

### D. 格式化一致性

- 是否对改动文件执行了对应的 `clang-format` / `ruff format --check` / `cmake-format --check`
- 是否存在格式化不通过但未在 findings 中标注的问题

## 输出格式（必须）

1. 先给 Findings（按严重级：High -> Medium -> Low）
2. 每条 Finding 必须带有序号（从 1 开始连续编号），格式示例：`[1] High | src/foo.cpp:42 | ...`
3. 每条包含：
   - 级别
   - 文件路径与行号
   - 问题描述
   - 违反的规范点（建议指向编码规范/工程规范，尽量精确到章节或条款标题，但不强求；对于逻辑缺陷、正确性风险等问题，无需关联规范点）
   - 建议修复方案
3. 若无问题，明确写“未发现阻塞性问题”，并给出剩余风险/测试缺口
4. 结论必须基于证据，不得臆测

## 评审边界

- 仅评审当前改动范围及其必要上下文
- 混合语言仓库中，仅对本次改动涉及的 C/C++/Python/CMake 文件执行对应检查，其他无关语言文件不扩展要求
- 不做无关重构要求
- 不把纯风格偏好当作阻塞问题
- 以“正确性与风险”优先于“风格偏好”
- 审查完成的结论必须经过用户确认后再修改，严禁未经确认自行修改

## 参考规范

- `coding-rules/for-human/cpp/README.md`
- `coding-rules/for-human/project/README.md`
- `coding-rules/AGENTS_BASE.md`
