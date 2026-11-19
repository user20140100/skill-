# 更新记录

## 1.1.0 — 2026-11-13

- 新增 `query` 命令，通过 Bytebase SQL Editor Query 接口执行查询并返回结果。
- 支持数据库简称、完整资源路径和 SQL Editor Sheet 链接；支持跨项目切换目标库。
- 支持直接 SQL、SQL 文件和 Worksheet 已保存 SQL，空 Worksheet 明确报错。
- 支持表格、JSON、CSV 输出及文件导出，行数限制、schema、数据源和超时参数。
- 保留重复列名、大整数、时间值及脱敏元数据；权限与 SQL 错误返回非零退出码。
- 修复项目列表缺少分页参数导致返回空列表的问题。
- 补充接口及结果解析测试；已在 PostgreSQL 和 Oracle 上验证实际查询。

## 1.0.0

- SQL 变更工单提交、查询权限申请和 SSO 登录。
