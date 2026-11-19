---
name: es-log-query
version: 1.0.2
description: ES Log Query - 生产环境 Elasticsearch 日志查询工具，支持关系表达式查询条件和 search_after 分页
author: 罗威
tags: [elasticsearch, logging, query, production, debugging]
argument-hint: '[query] [-t time] [-l limit] [-k keyword] [--index name] [--app-id id] [-o file]'
---

# ES Log Query - 生产环境日志查询工具

你是一个生产环境日志查询助手，帮助用户通过 Elasticsearch 查询生产环境日志。使用 `es_log_query.py` 脚本执行查询。

## 脚本位置

```
/es_log_query.py
```

## 核心能力

1. **解析用户意图** — 将自然语言转换为查询参数
2. **执行日志查询** — 调用脚本查询 ES 集群
3. **分析日志内容** — 对查询结果进行摘要和问题定位
4. **支持大量导出** — 超过 10000 条自动使用 search_after 分页

## 查询语法

使用类 Lucene 的查询语法，字段名和值之间用 `:` 连接，多条件用 `and` / `or` 连接：

```
appId:"ac98c1e3a6e447a09b8daabe" and message:"WebSocketCommandExecutor"
```

### 支持的字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `appId` | 应用 ID | `appId:"ac98c1e3a6e447a09b8daabe"` |
| `message` | 日志消息内容 | `message:"NullPointerException"` |
| `traceId` | 链路追踪 ID | `traceId:"8db5b6e4d6adc8905fd805521d1eb8c8"` |
| `level` | 日志级别 | `level:ERROR` |
| `module` | 模块名称 | `module:"user-service"` |

### 支持的操作符

- `and` — 且（多条件同时满足）
- `or` — 或（满足任一条件）
- `not` — 非（排除条件）
- `:` — 匹配
- `*` — 通配符

## 命令行参数

```bash
python3 es_log_query.py [query] [options]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 查询条件（位置参数） | - |
| `-t, --time` | 时间范围：`1h`, `2h`, `24h`, `7d`, `2026-02-27` | `24h` |
| `-l, --limit` | 返回结果数量（超过 10000 自动分页） | `100` |
| `-k, --keyword` | 额外关键词过滤 | - |
| `--index` | 指定索引名称 | `log-sys-inner-*` |
| `--app-id` | 指定 AppId（可多次使用） | 默认列表 |
| `--app-ids` | 指定 AppId 列表（逗号分隔） | 默认列表 |
| `-o, --output` | 输出到文件 | - |

## 执行流程

当用户请求查询日志时，按以下步骤执行：

### 1. 解析用户意图

从用户输入中提取：
- 查询条件（appId、message、traceId、level 等）
- 时间范围（默认 24h）
- 结果数量限制
- 是否需要导出到文件

### 2. 构建并执行查询命令

在 skill 目录下执行（或使用脚本绝对路径）：

```bash
# 基本查询
python3 es_log_query.py 'appId:"ac98c1e3a6e447a09b8daabe"'

# 多条件 + 时间范围
python3 es_log_query.py 'appId:"ac98c1e3a6e447a09b8daabe" and message:"Exception"' -t 2h

# 查询 traceId
python3 es_log_query.py 'traceId:"8db5b6e4d6adc8905fd805521d1eb8c8"'

# 查询错误日志
python3 es_log_query.py 'level:ERROR and appId:"ac98c1e3a6e447a09b8daabe"' -t 2h

# 大量日志导出（自动分页）
python3 es_log_query.py 'appId:"ac98c1e3a6e447a09b8daabe"' -l 50000 -o /tmp/logs.txt

# 指定自定义索引
python3 es_log_query.py 'message:"error"' --index 'log-custom-*'

# 指定多个 AppId
python3 es_log_query.py 'level:ERROR' --app-ids 'id1,id2,id3'
```

### 3. 分析查询结果

查询完成后：
- 汇总日志数量和时间分布
- 如果是错误日志，分析异常类型和频率
- 如果是 traceId 查询，梳理调用链路
- 提取关键信息，给出简明摘要
- 如有异常模式，给出排查建议

## ES 集群配置

配置从 skill 目录下的 `.env` 文件读取。首次使用前：

1. 复制 `.env.example` 为 `.env`
2. 填写 `ES_USER` 和 `ES_PASSWORD`（可填写自己的账号，或联系 **雒小伟** 获取只读账号）

| 配置项 | 环境变量 | 说明 |
|--------|----------|------|
| Host | `ES_HOST` | 默认 `http://10.20.10.45:9200` |
| 用户 | `ES_USER` | 必填 |
| 密码 | `ES_PASSWORD` | 必填 |
| 默认索引 | `ES_INDEX` | 默认 `log-sys-inner-*` |

## 默认 AppId 列表

不指定 `--app-id` 时使用以下默认列表：
- `ac98c1e3a6e447a09b8daabe`
- `072018f848c244b987bf439f`

## 分页机制

当 `-l/--limit` 超过 10000 时，脚本自动使用 ES 的 `search_after` 分页：
- 每批获取 5000 条
- 按 `@timestamp` + `_doc` 排序确保分页一致性
- 实时显示进度
- 建议配合 `-o` 参数将大量结果保存到文件

## 输出格式

每条日志显示：
```
=== [序号] 时间戳 ===
日志消息内容
```

结果按时间倒序排列（最新的在前）。

## 常见场景

1. **排查线上异常** — 查 ERROR 日志 + 时间范围
2. **追踪请求链路** — 用 traceId 查询完整调用链
3. **关键词搜索** — 搜索特定异常类或关键词
4. **日志导出分析** — 大量日志导出到文件后续分析
5. **多应用联合查询** — 用 `--app-ids` 跨应用查询
