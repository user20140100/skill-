---
name: bytebase-submit
description: >-
  提交SQL变更到Bytebase、执行SQL
  Editor数据库查询，或申请数据库查询权限。触发条件：用户说"提交SQL到bytebase"、"bytebase提交"、"执行查询SQL"、"Bytebase查询"、提供Bytebase
  SQL Editor链接、"申请查询权限"或类似表达时使用。
version: 1.1.0
author: tangbin12615
---

# Bytebase SQL 查询与变更

通过 CLI 工具提交 SQL 变更、执行数据库查询，或申请查询权限。

## 执行查询 SQL

查询使用独立的 `query` 子命令，通过 SQL Editor 的普通 Query 接口返回结果。
不要把 SELECT 当作 DML 变更提交；本节查询不创建变更工单。
数据库访问、SQL 类型校验和数据脱敏沿用 Bytebase 当前登录用户的权限，不调用 AdminExecute。
执行用户指定的查询即可，无需套用下方“变更工单提交确认”流程。

### 参数解析

- SQL：`--sql` 或 `--sql-file`，两者互斥。
- 数据库：`--database` 支持完整资源路径；简称必须配合 `--project`，按项目实时解析，存在同名库时要求指定完整路径。
- Sheet 链接：`--sheet-url` 读取已保存 Worksheet 的数据库和 SQL；页面路径虽然叫 sheets，实际资源是 `/v1/worksheets/{id}`。
- 可以用 `--sql` 或 `--sql-file` 覆盖 Sheet SQL。未保存的编辑器内容不在 Worksheet API 返回值中；空 Sheet 会明确报错。
- 查询不默认选择生产 biz 库，必须提供数据库或绑定数据库的 Sheet 链接。
- 默认最多返回 1000 行，`--limit` 可调整。达到限制时提示结果可能不完整。
- `--schema` 指定 schema；默认优先选择 READ_ONLY 数据源，没有时使用现有 ADMIN 数据源，但仍仅调用普通 Query 接口，服务器继续执行权限校验。多个候选数据源时需提供 `--data-source-id`。
- 默认请求超时 30 秒，可通过 `--timeout` 调整；超时不自动重试。
- `--format table|json|csv`，默认 table；`--output` 保存结果。CSV 仅支持一个结果集。
- JSON 保留列名、列类型、行数、脱敏元数据等；行值转为普通 JSON 值，整数保持精度，bytes 保留 Base64，带时区和精度的时间值保留元数据。重复列名通过列名数组和行数组保留。
- 登录过期时运行 `python3 cli.py login`，由用户完成 SSO；不自动申请新权限。

### 示例

命令均在本 Skill 的 `cli/` 目录执行：

```bash
# 指定项目和数据库查询
python3 cli.py query -p sqpf -d pgdb_csp --sql 'SELECT 1 AS ok' --limit 10

# 读取 Sheet 的数据库，执行指定查询
python3 cli.py query \
  --sheet-url 'https://bytebase.gz.cvte.cn/sql-editor/projects/sqpf/sheets/8664' \
  --sql 'SELECT 1 AS ok'

# 执行 Sheet 中已保存的 SQL
python3 cli.py query --sheet-url 'https://bytebase.gz.cvte.cn/sql-editor/projects/sqpf/sheets/8664'

# 查询结果导出
python3 cli.py query -p sqpf -d pgdb_csp -f query.sql --format csv -o result.csv
```

验证命令：`python3 -m unittest discover -s tests -v`。

---

以下章节为变更工单和查询权限申请流程。

## 工具路径

CLI 工具在本 SKILL.md 同级的 `cli/` 子目录下。执行命令时 cd 到 `cli/` 目录。

## 前置条件

### 首次安装

```bash
cd "$(dirname "${SKILL_FILE}")/cli"
pip install -r requirements.txt
playwright install chromium
```

### 登录

如果 session 过期或不存在（token 有效期 4 小时），执行登录：

```bash
cd "$(dirname "${SKILL_FILE}")/cli" && python3 cli.py login
```

登录需要用户在浏览器中完成 SSO 扫码。

## 执行步骤

### 1. 解析用户意图

从用户消息中提取：
- **SQL 内容**：SQL 文件路径 或 直接的 SQL 语句
- **目标数据库**：用户指定的数据库，或使用默认值
- **项目**：默认 `qpbiz`
- **变更类型**：DDL 或 DML（根据 SQL 内容自动判断）
- **标签**：默认 `数据变更`

### 2. 数据库映射

用户可以用简称指定数据库，按以下映射转换为完整路径：

| 简称 | 完整路径 |
|------|----------|
| pgdb_biz / biz / 生产biz | `instances/postgres004ugzucvteucn/databases/pgdb_biz` |
| pgdb_dms / dms / 生产dms | `instances/postgres004ugzucvteucn/databases/pgdb_dms` |
| pgdb_cba / cba / 生产cba | `instances/postgres004ugzucvteucn/databases/pgdb_cba` |
| pgdb_gbiz / gbiz / 生产gbiz | `instances/postgres004ugzucvteucn/databases/pgdb_gbiz` |
| pgdb_openagent / openagent | `instances/p-openagent-pg001ugzucvteucn/databases/pgdb_openagent` |
| pguat_biz / 测试biz | `instances/pguat002ugzucvteucn/databases/pguat_biz` |
| pguat_dms / 测试dms | `instances/pguat002ugzucvteucn/databases/pguat_dms` |
| pgsit_biz / sit_biz | `instances/t-postgres002-d-001/databases/pgsit_biz` |
| pgsit_cba / sit_cba | `instances/t-postgres002-d-001/databases/pgsit_cba` |
| pgsit_dms / sit_dms | `instances/t-postgres002-d-001/databases/pgsit_dms` |

如果用户未指定数据库，默认使用 `pgdb_biz`（生产 biz 库）。

如果用户指定的数据库不在映射表中，直接使用用户输入的值（可能是完整路径）。

### 3. 自动判断变更类型

- SQL 包含 `CREATE`、`ALTER`、`DROP`、`TRUNCATE` → DDL
- 其他（`INSERT`、`UPDATE`、`DELETE`、`SELECT`）→ DML
- 默认 DDL

### 4. 确认提交（必须）

在实际提交前，必须向用户展示以下信息并获得确认：

```
即将提交到 Bytebase:
  项目:   {project}
  数据库: {database_full_path}
  类型:   {DDL|DML}
  标签:   {label}
  标题:   {title}
  SQL 预览（前 5 行）:
    {sql_preview}
  SQL 总行数: {line_count}
```

使用 AskUserQuestion 确认：
- A) 确认提交
- B) 取消

只有用户确认后才执行提交。

### 5. 提交

```bash
cd "$(dirname "${SKILL_FILE}")/cli" && python3 cli.py submit \
  -p {project} \
  -d {database_full_path} \
  -f {sql_file} \
  --type {DDL|DML} \
  -l "{label}" \
  -t "{title}"
```

或直接传 SQL：

```bash
cd "$(dirname "${SKILL_FILE}")/cli" && python3 cli.py submit \
  -p {project} \
  -d {database_full_path} \
  --sql "{sql_content}" \
  --type {DDL|DML} \
  -l "{label}" \
  -t "{title}"
```

### 5. 返回结果

提交成功后显示 Issue URL 给用户。

## 使用示例

- "把这个SQL提交到bytebase" → 使用默认 pgdb_biz
- "提交到测试biz" → 使用 pguat_biz
- "提交到 pgdb_dms" → 使用 pgdb_dms
- "提交到 instances/xxx/databases/yyy" → 直接使用完整路径
- "申请查询 pgdb_biz 的权限" → 创建查询权限工单

## 申请查询权限

当用户需要申请数据库查询权限时，使用 `request-query` 子命令。

### 解析用户意图

从用户消息中提取：
- **目标数据库**：使用上面的数据库映射表
- **项目**：默认 `qpbiz`
- **过期天数**：默认 7 天
- **申请原因**：可选

### 确认提交（必须）

```
即将申请查询权限:
  项目:   {project}
  数据库: {database_full_path}
  过期:   {expire_days} 天
  原因:   {reason}
```

使用 AskUserQuestion 确认。

### 提交

```bash
cd "$(dirname "${SKILL_FILE}")/cli" && python3 cli.py request-query \
  -p {project} \
  -d {database_full_path} \
  -e {expire_days} \
  -t "{title}" \
  -r "{reason}"
```

提交成功后显示 Issue URL 给用户。
