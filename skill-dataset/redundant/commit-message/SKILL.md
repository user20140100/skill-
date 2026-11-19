---
name: commit-message
description: >-
  Generates git commit messages following the structured format with keywords,
  [what][why][how] body, impact level, and testing scope. Use when the user asks
  for help writing commit messages, generating commit messages from code
  changes, or when committing code.
author: chenhaibing
version: 0.0.1
---

# 代码提交规范

Generates git commit messages in the specified structured format.

## 调用方式

**第一、第二、第三、第四关键字必须由用户输入。** 调用时请用户提供：

- **第一关键字**：bugfix | feature | config | merge | revert
- **第二关键字**：JIRA 号，格式如 `JIRA#VQC1006-13379` 或 `JIRA#`
- **第三关键字**：项目名，如果是针对某些项目的问题，填写项目名称，可以填写多个项目，不同项目明用|隔开。例如：ICS0705|ICS0707
- **第四关键字**：如果是平台问题，填写Y，填写后会自动触发通知，如果不是，填N即可

**调用示例：**
- `@commit-message 第一=feature 第二=JIRA# 第三=DisplayPlugin_ExampleApp 第四=Y 生成本次提交`
- `调用 commit-message skill：第一=bugfix 第二=JIRA#VQC1006-13379 第三=platform 第四=N`
- `commit-message 第一=merge 第二=JIRA#VQC1006-13379 第三=ICS0705 第四=Y`

若用户未提供任一关键字，**必须先询问用户**，不得自行推断。

## Commit Message Format

```
[第一关键字][第二关键字][第三关键字][第四关键字][可选关键字1][可选关键字2] 英文简单描述

[what]详细说明修改什么问题
[why]详细说明问题产生原因和（或）为什么做这个修改
[how]详细说明是怎么修改的
[影响等级]S、A、B、C、D
[建议测试范围]针对本次改动，建议测试的范围
```

**Rules:**
- Subject line: keywords in brackets, followed by a brief English description
- One blank line between subject and body
- Body sections: [what], [why], [how], [影响等级], [建议测试范围] — each on its own line

---

## 第一关键字（必选）

根据修改项类型选择其一。**bugfix 和 feature 必须按实际情况填写**，bugfix 会触发 JIRA 缺陷自动填写原因分析和解决方案。

| 关键字 | 说明 |
|--------|------|
| bugfix | 针对 BUG 的修改和完善 |
| feature | 功能和需求的修改和完善 |
| config | 客户配置和参数（不包括系统参数）的修改 |
| merge | 合并其他分支已解决的问题或功能 |
| revert | 还原已提交修改项 |

---

## 第二关键字（必选）

**格式：** `[JIRA#JIRA-KEY]`

- 填写 Jira 问题号
- 多个用 `|` 隔开，例如：`[JIRA#VQC1006-13379 | VQC1006-1234 | VQC1006-4321]`
- **bugfix 时必须填写对应缺陷的 ID**，系统会根据 ID 找到 JIRA 问题并触发 AI 自动填写原因分析和解决方案
- 需与第一关键字对应

---

## 第三关键字（必选）

**格式：** `[项目1|项目2|...]`

- **项目名称**：针对特定项目的问题，可填多个，用 `|` 隔开
- 示例：`[ICS0705|ICS0707]`

## 第四关键字（必选）

**格式：[Y]/[y]/[N][n]

---

## 可选关键字

| 关键字 | 说明 | 必选 |
|--------|------|------|
| 客户 | 提出问题、需求或订单的客户名称；公司自测或自提需求则写 **cviauto** | 可选 |
| [Part N/M] | N=该修改项的第几个上传，M=总上传数；用于一个修改项对应多仓库的情况 | 强烈推荐 |

---

## 影响等级

| 等级 | 说明 |
|------|------|
| S | 系统级/核心影响 |
| A | 重要功能影响 |
| B | 一般功能影响 |
| C | 局部影响 |
| D | 微小影响 |

---

## Workflow

1. **获取用户输入**：第一关键字、第二关键字、第三关键字、第四关键字（缺一不可，未提供则询问）
2. Analyze the code changes (git diff / staged files)
3. 若用户提供了可选关键字（客户、[Part N/M]），一并使用
4. 根据代码改动撰写 [what]、[why]、[how]、[影响等级]、[建议测试范围]
5. Write subject: `[第一][第二][第三][第四][可选1][可选2] 英文简单描述`
6. Write body with all five sections
7. Output the complete commit message（或直接执行 git commit）

---

## Example 1: bugfix

**User Input:** 第一=bugfix 第二=JIRA#VQC1006-13379 第三=platform 第四=N；代码改动：修复登录超时

**Output:**
```
[bugfix][JIRA#VQC1006-13379][ICS0705][N] Fix login timeout when token expires

[what]用户登录超时后无法自动刷新，导致会话中断
[why]token 过期后未正确触发刷新逻辑，JWT 校验失败后直接返回 401
[how]在 axios 拦截器中增加 token 过期检测，过期时调用 refresh 接口获取新 token 后重试请求
[影响等级]A
[建议测试范围]登录流程、token 刷新、长时间无操作后的会话保持
```

---

## Example 2: feature

**User Input:** 第一=feature 第二=JIRA#VQC1006-1500 第三=ICS0705 第四=N 客户=cviauto [Part 1/2]；代码改动：新增订单导出

**Output:**
```
[feature][JIRA#VQC1006-1500][ICS0705][N][cviauto][Part 1/2] Add order export to Excel

[what]订单模块缺少导出功能，无法批量导出订单数据
[why]业务需要将订单数据导出为 Excel 进行线下分析
[how]新增导出接口，支持按条件筛选后生成 Excel 文件并下载
[影响等级]B
[建议测试范围]导出功能、筛选条件、大数据量导出、文件格式校验
```

---

## Example 3: config

**User Input:** 第一=config 第二=JIRA#VQC1006-1600 第三=ICS0705|ICS0707 第四=N 客户=客户A；代码改动：调整 API 超时配置

**Output:**
```
[config][JIRA#VQC1006-1600][ICS0705|ICS0707][N][客户A] Update timeout threshold for API calls

[what]API 调用超时阈值需根据客户环境调整
[why]客户 A 网络环境较慢，默认 30 秒超时导致部分请求失败
[how]在客户配置中新增 api_timeout 参数，客户 A 设置为 60 秒
[影响等级]C
[建议测试范围]API 调用超时场景、配置生效验证
```

---

## Example 4: merge

**User Input:** 第一=merge 第二=JIRA#VQC1006-13379 第三=ICS0705 第四=Y；代码改动：合并登录超时修复

**Output:**
```
[merge][JIRA#VQC1006-13379][ICS0705][Y] Merge fix for login timeout from release branch

[what]合并 release 分支已修复的登录超时问题
[why]主分支需要同步该修复以保持代码一致
[how]合并 release/1.2 分支的 auth 模块相关提交
[影响等级]A
[建议测试范围]登录流程、token 刷新
```
