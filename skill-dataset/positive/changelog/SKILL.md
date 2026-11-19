---
name: changelog
description: 生成项目的变更日志，基于 Git 提交记录自动生成中文 changelog
version: 1.0.1
author: fujinxiang
---

# Changelog Generator

生成项目的变更日志，基于 Git 提交记录自动生成中文 changelog。

## 功能说明

- 读取 Git 提交历史
- 分析每个提交的 message 和 diff
- 过滤无意义的变更（如 MR、重命名、文件位置调整等）
- 以日期为小标题组织 changelog
- 记录最后处理的 commit hash，支持增量更新
- 生成中文描述的变更日志，每条变更附带对应的 commit hash（前8位）

## 使用方法

在项目根目录执行：
```
/changelog
```

## 实现逻辑

当用户调用此 SKILL 时，请按以下步骤执行：

### 步骤 1: 检查现有 CHANGELOG.md

使用 Read 工具检查项目根目录是否存在 CHANGELOG.md 文件。

- 如果存在，查找文件开头的注释 `<!-- Last processed commit: <hash> -->`
- 提取 commit hash 作为起始点
- 如果不存在该注释或文件不存在，则从头开始处理所有提交

### 步骤 2: 获取 Git 提交历史

使用 Bash 工具执行以下命令：

```bash
# 如果有起始 commit hash
git log <last-commit-hash>..HEAD --pretty=format:"%H|%ad|%s" --date=short

# 如果没有起始 commit hash（首次运行）
git log --pretty=format:"%H|%ad|%s" --date=short
```

这将返回格式为 `commit-hash|date|message` 的提交列表。

**重要：首次运行时的分段处理**

如果是首次生成 changelog（不存在 CHANGELOG.md 或没有 last processed commit），需要先统计提交总数：

```bash
git rev-list --count HEAD
```

- 如果提交数量超过 100 个，应该分段处理，建议按月分段
- 可以使用以下命令获取最近 N 个月的提交：
  ```bash
  # 获取最近 1 个月的提交
  git log --since="1 month ago" --pretty=format:"%H|%ad|%s" --date=short

  # 获取最近 3 个月的提交
  git log --since="3 months ago" --pretty=format:"%H|%ad|%s" --date=short
  ```
- 询问用户希望处理多长时间范围的提交（例如：最近 1 个月、3 个月、6 个月、全部）
- 对于大型项目，建议从最近 3 个月开始，后续可以逐步补充历史记录

### 步骤 3: 分析每个提交

对于每个提交，执行以下操作：

1. 使用 Bash 工具获取提交的详细信息：
   ```bash
   git show <commit-hash> --stat --pretty=format:"%H|%ad|%s|%b" --date=short
   ```

2. 分析提交内容，判断是否应该包含在 changelog 中：
   - **排除**以下类型的提交：
     - Merge 提交（message 包含 "Merge" 或 "merge"）
     - 仅重命名文件（diff 只包含 rename）
     - 仅移动文件（diff 只包含 moved）
     - 格式化提交（message 包含 "format"、"lint"、"style" 等）
     - 文档更新（message 只包含 "docs:"、"doc:" 等，且只修改 .md 文件）
     - 版本号更新（message 只包含 "version"、"bump" 等）

   - **包含**以下类型的提交：
     - 新功能（feat:、feature:、add、新增等）
     - Bug 修复（fix:、bugfix:、修复等）
     - 性能优化（perf:、optimize:、优化等）
     - 重构（refactor:、重构等，但要有实际业务逻辑变更）
     - 其他有实际业务价值的变更

3. 对于有意义的提交，生成中文描述：
   - **优先分析 commit message**：大多数情况下，commit message 已经足够清晰
   - **必要时结合 diff 分析**：当 commit message 过于简单或不清晰时（如 "update"、"fix"、"优化" 等），必须查看 diff 来理解实际变更内容
   - 总结变更的业务价值
   - 用简洁的中文描述变更内容
   - 格式：`- [类型] 描述内容 (commit-hash前8位)`
     - 类型可以是：新增、修复、优化、重构、更新等
     - commit hash 取前8位字符，用括号括起来
   - **严格使用纯中文描述**：
     - 避免中英文混杂（错误示例：`[新增] 增强 notification system`）
     - 正确示例：`[新增] 增强通知系统功能`
     - 例外情况：文件名（如 `README.md`）和技术术语（如 `API`、`DOM`、`JSON`）可以保留英文
     - 对于英文 commit message，需要翻译成通顺的中文描述

### 步骤 4: 按日期分组

将所有有意义的提交按日期分组，格式如下：

```markdown
## YYYY-MM-DD

- [新增] 功能描述 (12345678)
- [修复] Bug 描述 (abcdef12)
- [优化] 性能优化描述 (9876fedc)
```

### 步骤 5: 生成或更新 CHANGELOG.md

1. 获取最新的 commit hash（第一个处理的提交）
2. 生成新的 changelog 内容：
   ```markdown
   <!-- Last processed commit: <latest-commit-hash> -->

   [新的变更内容按日期分组]
   ```
3. 如果 CHANGELOG.md 已存在：
   - 读取现有内容
   - 删除旧的 `<!-- Last processed commit: ... -->` 注释
   - 将新内容插入到文件开头
   - 保留旧的 changelog 内容
4. 如果 CHANGELOG.md 不存在：
   - 创建新文件
   - 添加标题 `# Changelog`
   - 添加新内容

### 步骤 6: 输出结果

告知用户：
- 处理了多少个提交
- 生成了多少条有意义的变更记录
- CHANGELOG.md 文件的位置
- 最新处理的 commit hash

## 输出格式

```markdown
<!-- Last processed commit: <commit-hash> -->

# Changelog

## 2026-02-05

- [新增] 支持 demand 为空的情况处理 (24f8bba0)
- [优化] 测试脚本性能提升 (ff87ab80)

## 2026-02-04

- [新增] 添加物流天数处理和 CRD/ESD 日期逻辑 (7263acc0)
- [修复] 强制添加上个月数据到表格参与计算 (4f6bf9e0)
- [更新] 更新项目文档 (dc61064a)

...
```

## 注意事项

1. **首次运行**：如果项目中没有 CHANGELOG.md，将处理所有历史提交。对于提交数量超过 100 的项目，建议分段处理（按月），避免一次性处理过多提交
2. **增量更新**：后续运行只处理上次记录的 commit 之后的新提交
3. **过滤规则**：自动过滤 Merge、重命名、格式化等无业务价值的提交
4. **中文描述**：所有变更描述使用中文，简洁明了。严格避免中英文混杂，除了文件名和技术术语
5. **日期分组**：按提交日期自动分组，便于查看历史变更
6. **Git Hash**：每条变更记录末尾显示对应的 commit hash 前8位，用括号括起来，便于追溯
7. **Diff 分析**：当 commit message 过于简单时，必须结合 diff 来生成准确的中文描述

## 示例

### 基本示例

假设项目有以下提交：
- `feat: add user login` (commit: 93bee3de) - 会被包含，描述为 "[新增] 用户登录功能 (93bee3de)"
- `Merge branch 'main'` - 会被过滤
- `fix: resolve null pointer` (commit: a1b2c3d4) - 会被包含，描述为 "[修复] 解决空指针异常 (a1b2c3d4)"
- `docs: update README` - 如果只修改 .md 文件，会被过滤
- `refactor: optimize database query` (commit: ef567890) - 会被包含，描述为 "[优化] 数据库查询性能 (ef567890)"

### 纯中文描述示例

**错误示例（中英文混杂）**：
- `[新增] 增强 notification system to use shadow DOM for 渲染 (008ba56c)`
- `[修复] fix the bug in 用户登录 module (a1b2c3d4)`
- `[优化] improve performance of API 调用 (ef567890)`

**正确示例（纯中文）**：
- `[新增] 增强通知系统，使用 Shadow DOM 进行渲染 (008ba56c)`
- `[修复] 修复用户登录模块的错误 (a1b2c3d4)`
- `[优化] 提升 API 调用性能 (ef567890)`

**允许的例外（文件名和技术术语）**：
- `[更新] 更新 README.md 文档 (12345678)` - 文件名可以保留
- `[新增] 添加 JSON 数据导出功能 (abcdef12)` - 技术术语可以保留
- `[优化] 改进 DOM 操作性能 (9876fedc)` - 技术术语可以保留
