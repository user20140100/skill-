---
name: mofang-local-auth-sql
description: >-
  把业务方的自然语言诉求转成 mofang-local 权限配置
  SQL。覆盖新增服务接入、补充/调整角色、权限点、首页卡片、删除权限点、变更权限点顺序，以及为新服务补做默认开通。直接产出
  `tb_service_open`、`t_power_config`、`t_app_role_power_config`、`t_index_app_config`
  SQL，业务方无需理解 UC/RBAC 背景。
version: 2.0.3
author: luobin12754
tags:
  - 本地化权限
  - 魔方权限
---

# 魔方本地权限 SQL 生成

把业务诉求直接转换成 mofang-local 配置 SQL，业务方无需理解底层实现。

## 数据核验（ccloud-cli）

生成最终 SQL 前，按 [边缘数据库只读查询](references/edge-db-read.md) 使用 `ccloud-cli` 定位目标机构的 EdgeMySQL 资源，并实际查询 `mofang_local`。不要求本地 MySQL MCP，也不通过 `resource query` 执行本 Skill 生成的写入 SQL。

- 从用户输入或已验证的运行资产取得完整机构码（`clusterName`）；缺少时先整理已知诉求，再询问机构码。业务方无需提供内部 `clusterId`、`psdcloudId` 或 `resourceId`。
- `ccloud-cli` 不可用、资源未唯一定位、无查询权限或查询失败时，说明准确的阻塞点和所需最小信息；不得把未经查询的现存角色、权限或服务清单当成事实，也不输出未经目标库核验的最终 SQL。
- `tb_service_open` 属于 `seewo_class`；确需核对其现状时，按同一参考文件单独定位该库，不在 `mofang_local` 资源上跨库查询。

## 权限模型速览（AI 生成 SQL 必须的最小集）

四张配置表 + 四类业务实体：

| 实体 | 表 | 作用 |
|---|---|---|
| 服务开通 | `tb_service_open` | 决定本地化权限点是否生效；新服务需默认开通时才写 |
| 权限点 | `t_power_config` | 权限定义，全局唯一 `c_code` |
| 角色授权 | `t_app_role_power_config` | `(service_code, role_code, power_code)` 三元关系 |
| 首页卡片 | `t_index_app_config` | 平台入口；`c_app_key` = 服务编码 |

关键口径：
- **角色层级**：校级 = `1`，院级 = `2`。对外用业务语言确认，不直接问 `role_level`。
- **超管角色**：`manager`，必须显式补齐本服务下全部本次新增权限的授权。
- **默认角色 vs 手动角色**：
  - 默认角色 / 系统默认角色 = 目标 `service_code` 下 `t_app_role_power_config` 已配置过的所有角色
  - 手动创建角色 = 用户在界面上自行新增、当前未在该表预置授权关系的角色
  - 涉及"默认角色""所有角色""系统预置角色"时，先通过 `ccloud-cli` 查询目标机构的 `t_app_role_power_config`，查不到再追问。
- **权限层级**：用户未说层级时，默认一级权限，`c_parent_code = ''`。
- **现有服务清单**：当用户说"挂到现有服务"但未指定服务名时，通过 `ccloud-cli` 查询 `t_app_role_power_config.c_service_code` 的 distinct 值，完整分页后列出来让用户选，不做开放式追问。

## 应用包维护知识

所有 SQL **只能维护到业务自己的应用包中**，**不要**维护到魔方或 UC 的应用包，也不能作为临时脚本一次性执行。业务应用包按两个交付区块组织：

| 区块 | 用途 | 归类规则 |
|---|---|---|
| 初始化 SQL | 应用包开通时执行 | 仅 `mofang_local` 库 SQL 进入 |
| 升级策略 SQL | A→B 版本升级时执行 | **所有** SQL 都进入（含 `mofang_local`） |

所以：
- `mofang_local` 库 SQL → 初始化 SQL 和升级策略 SQL **各一份**
- 其他库（如 `seewo_class`）SQL → 仅升级策略 SQL

一次诉求若同时涉及多个库，按库分别归类，不一刀切。

**生效机制**：魔方有定时任务，每 60 秒从 `mofang_local` 拉取并刷新权限配置缓存。业务包 SQL 落库后无需重启魔方，最多等待 60 秒即可生效。输出时必须告知使用者这一点。

## AI 工作流

### 1. 拆解需求

阅读 [SQL 生成规则](references/sql-rules.md)，从用户诉求中提取：
- 服务：`service_code`、是否全新服务、存量学校是否默认开通
- 操作类型：新增/修改权限、角色授权、删除权限点、变更权限点顺序、首页卡片
- 权限点：`code`、`name`、`parent_code`、`order`
- 角色：`role_code`、`role_name`、校级/院级、关联权限编码
- 卡片（仅当用户明确要）：`app_id`、`app_key`、`name`、`desc`、`order`、`url`、`color`、`icon`、`powers`

### 2. 用户补充 + 确认需求

**先用 `ccloud-cli` 查询现有配置，再追问。** 只追问真正阻塞 SQL 生成的字段。

阻塞项（确认前不生成 SQL）：
- `service_code` 不明确，或不确定是否全新服务、是否默认开通
- 父权限编码、新权限编码、`c_order` 不能稳定确定
- "默认角色""所有角色"等范围不明确，且目标库查不到
- 角色 `role_code` / `role_name` / 层级不能稳定确定
- 删除/变更顺序时 `powerCode`（及新 `c_order`）不明确
- 无法判断诉求落到"权限定义""角色授权""服务默认开通""首页卡片"哪一类

输出 **《需求理解结果》** 用业务语言复述，不暴露底层表名；如仍有歧义，继续追问。

### 3. 输出 SQL 及维护规范

按以下顺序生成 SQL：`tb_service_open` → `t_power_config` → `t_app_role_power_config` → `t_index_app_config`。

幂等写法：
- `t_power_config` 必须用 `INSERT ... ON DUPLICATE KEY UPDATE`
- 其他表用 `INSERT ... SELECT ... WHERE NOT EXISTS`
- 删除权限点时只清理 `t_power_config` 和 `t_app_role_power_config`，不动 `t_index_app_config.c_powers`
- 变更权限点顺序只更新 `t_power_config.c_order`

每段 SQL 前用一句中文说明对应哪条业务诉求。

### 4. 启动子 Agent 校验（强制）

在把结果交付给用户**之前**，必须启动一个子 Agent 做独立校验，不允许跳过。

启动方式：调用 `Agent` 工具，`subagent_type` 选 `general-purpose`，传入以下完整上下文：
- 本轮对话中**用户的全部原始输入**（逐条原文，不做总结）
- 本轮即将输出的**完整 5 段内容**（需求理解结果 / 初始化 SQL / 升级策略 SQL / 需求-SQL 对照清单 / 未覆盖项）
- 校验目标清单（见下）

子 Agent 校验目标：
1. **诉求覆盖**：用户每条原始诉求是否都被 SQL 或"明确不生成"承接，有无遗漏
2. **SQL 可执行性**：必填字段是否齐全（参考 `references/sql-rules.md`）；幂等写法是否正确；库名/表名/字段名是否拼写正确
3. **业务正确性**：
   - `service_code` 是否一致（`t_app_role_power_config.c_service_code` 与 `t_index_app_config.c_app_key`）
   - 角色权限关系是否引用了已生成或已存在的权限编码
   - 超管 `manager` 是否补齐
   - 校级/院级 `c_role_level` 是否符合用户描述
   - `c_parent_code` 引用是否有效
4. **应用包归类**：`mofang_local` 库是否同时进入初始化 SQL 与升级策略 SQL；其他库是否仅在升级策略 SQL
5. **数据库查询结果一致性**：默认角色名单、`role_code` 等是否与本次 `ccloud-cli` 只读查询结果一致（必要时让子 Agent 复查同一目标资源）
6. **红线**：是否带有"假设"、是否暴露底层术语、是否凭空生成卡片或默认开通

子 Agent 必须返回结构化结果：
- `通过 / 不通过`
- 若不通过，逐条列出问题及对应 SQL 行
- 修复建议

主 Agent 收到子 Agent 反馈后：
- 通过 → 在最终输出末尾追加 **《校验结果》** 段，附"已通过子 Agent 独立校验"一句
- 不通过 → 按反馈修复 SQL，重新校验，直到通过；若修复涉及用户诉求歧义，回到第 2 步追问，不要硬改

## 输出模板

固定 5 段，顺序不变。所有自然语言均使用中文。

````text
以下 SQL 只能维护到**业务自己的应用包**中（不要放到魔方或 UC 的应用包），请按"初始化 SQL""升级策略 SQL"分别落库。
落库后无需重启魔方，魔方有定时任务每 60 秒刷新一次权限配置缓存，最多等待 60 秒即可生效。

需求理解结果
- 用业务语言逐条复述用户诉求（服务 / 权限 / 角色 / 默认开通 / 首页卡片）
- 不直接暴露底层表名

初始化 SQL
```sql
-- 仅 mofang_local 库 SQL；无则写 -- 无
-- 这段 SQL 对应"XXX 业务诉求"
INSERT INTO ...
```

升级策略 SQL
```sql
-- 本次涉及的所有库 SQL（含 mofang_local 重复一份）
-- 这段 SQL 对应"XXX 业务诉求"
INSERT INTO ...
```

需求-SQL 对照清单
- 新增权限：已落实到 `t_power_config`
- 角色授权：已落实到 `t_app_role_power_config`
- 默认开通服务：本次未生成，对应诉求为"不需要"
- 首页卡片：本次未生成，对应诉求为"不需要"

未覆盖项 / 未确认项
- 无（或逐条列出未承接的用户原话）

校验结果
- 已通过子 Agent 独立校验（诉求覆盖 / SQL 可执行性 / 业务正确性 / 应用包归类 / 红线均无问题）
````

## 红线（不允许）

- 不允许跳过《需求理解结果》直接输出 SQL
- 不允许带"假设"输出 SQL；任何不确定信息先确认
- 不允许 `ccloud-cli` 查询不可用时改为读业务代码推断目标机构的现存角色
- 不允许整批 SQL 无说明直接贴出
- 不允许向业务方暴露"洗数据""底层表名"等内部术语
- 不允许凭空生成首页卡片或默认开通

## 参考资料

- [SQL 生成规则](references/sql-rules.md)：四张表的字段、模板、删除/顺序变更 SQL
- [边缘数据库只读查询](references/edge-db-read.md)：机构码定位 EdgeMySQL、资源匹配、只读查询与失败处理
