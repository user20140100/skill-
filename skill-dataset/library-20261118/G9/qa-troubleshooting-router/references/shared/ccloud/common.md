# ccloud-cli 公共操作

遵守 [能力入口](../ccloud-cli-tools.md) 的 profile、argv 和只读边界。本文件不选择环境、不提供默认 ID。只读取当前环境文件指定的操作章节，不因文件被引用而全量加载。

## 1. 查询应用日志

前置：已按当前环境文件唯一定位应用，并保留同一命中的 `result.appId/result.clusterId/page.psdcloudId`。

```bash
ccloud-cli observe logs \
  --app-id <result.appId> \
  --cluster-id <result.clusterId> \
  --psdcloud-id <page.psdcloudId> \
  --start-time '<RFC3339-start>' \
  --end-time '<RFC3339-end>' \
  --size <1-5000>
```

起止时间必须同时提供或同时省略；省略时服务端使用最近 30 分钟。`--query` 仅在问题有明确过滤条件时传入。

`observe logs` 的 `data` 是 LiteLog 返回并反序列化后的 JSON 值，可能是对象或数组；不要假定固定记录形状。校验命令与业务响应成功、目标一致后再记录证据；无权限或字段不足时报告缺口。

## 2. 日志过滤语法

`observe logs --query` 使用标准 MySQL `WHERE` 条件写法，只传条件部分，不写 `SELECT`、`FROM` 或 `WHERE`。接口支持的是条件子集，不代表允许完整 MySQL 语句或全部函数：

| 目的 | 写法 |
|---|---|
| 字段比较 | `message = '完整日志内容'`、`namespace <> 'default'` |
| 包含关键词 | `message LIKE '%Auth4AToUc%'` |
| 多个关键词任一命中 | `message LIKE '%Auth4AToUc%' OR message LIKE '%no provider%'` |
| 组合条件 | `namespace = 'default' AND (message LIKE '%ERROR%' OR message LIKE '%Exception%')` |
| 集合、范围、空值 | `namespace IN ('a', 'b')`、`_timestamp BETWEEN <起始值> AND <结束值>`、`message IS NOT NULL` |

日志正文使用 `message` 字段；其他字段名和类型以实际返回或工具帮助为准。字符串使用单引号，字符串内单引号按 SQL 规则写成两个单引号；`LIKE` 中 `%` 匹配任意长度，`_` 匹配单个字符，注意它们不是字面量。查询值与字段类型保持一致。

完整命令示例（双引号用于 shell 包裹整个参数，内部单引号属于 SQL）：

```bash
ccloud-cli observe logs \
  --app-id <result.appId> \
  --cluster-id <result.clusterId> \
  --psdcloud-id <page.psdcloudId> \
  --size 50 \
  --query "message LIKE '%Auth4AToUc%' OR message LIKE '%no provider%' OR message LIKE '%No provider%'"
```

不能写成裸关键词 `Auth4AToUc OR 'no provider'`，也不能使用 `message =~ 'Auth4AToUc'`；前者会把关键词解析成字段，后者不是受支持的 MySQL 条件运算符。不使用函数、子查询、UNION、多语句或未声明支持的正则运算符。

遇到语法错误时，依据具体报错与本节修正；不要继续猜另一种查询语言。查询成功但零命中，只表示当前应用、时间窗口和条件下没有结果。

## 3. 部署详情与代码版本

部署相关代码查询先完成当前环境文件中的应用发现步骤取得同一命中的 appId 与业务 clusterId，无需先查询日志：

```bash
ccloud-cli app detail --app-id <result.appId> --cluster-id <result.clusterId>
```

此命令使用应用所属的业务集群 ID，不能使用数据库资源路由替代。参数以当前 CLI help 为准，不把 psdcloudId 或 URL 的 mid 当 clusterId。

校验命令成功、业务响应成功以及目标一致性；读取实际运行版本的版本号、分支及可用的 commit/tag、镜像、scenario、trafficWeight、replicaNum、availableReplicas、unavailableReplicas（只记录实际返回字段，不假定固定 JSON 层级）。灰度或多版本运行时按故障请求/Pod 证据匹配，不能取第一条、仅按版本号排序或将零可用副本自动排除为非故障目标。不存在部署记录、字段不足或无权限时报告缺口，不把默认配置当现场事实。

实测 `app detail` 响应以 `data.appId/clusterId` 标识目标，运行版本位于 `data.versions[]`，镜像版本取同一项的 `imageTag/fullImage`；`versionName`（如 v2）与 `versionNum` 是应用版本标识，不是 Git 版本。响应可能只有镜像 tag 而没有 branch/commit。本平台已确认 `<分支名>-<短 commit>-<构建时间>` 命名规则，此时按 `references/shared/code-mcp.md` 的映射步骤从右侧拆分 imageTag，使用短 commit 查询；不符合规则时才记录映射缺口。`app images` 只列最近镜像候选，未包含当前部署 tag 不代表当前部署不存在。

`references/shared/code-mcp.md` 定义部署版本与 Git ref 的映射规则；部署版本号或镜像 tag 未经映射不能直接传给代码工具。本步骤不授予部署、发布或切流权限。

## 4. 数据库路由、匹配与只读查询

`search resource` 必须预先提供资源路由，不能发现自己的搜索入口 `clusterId`。资源入口由平台接入层提供，不能要求业务用户理解内部 ID。按以下顺序取得 `resourceClusterId/resourcePsdcloudId`：

1. 当前目标的明确路由、可信宿主配置或已验证资源发现结果；确认其是管理/资源集群，不是应用业务集群。
2. 没有目标专属路由时，使用当前环境文件中**适用本平台**且有来源的管理资源映射。不要把维护的平台映射误判为禁止使用的历史实例 ID；不因用户没提供链接就停止。
3. 映射确实不覆盖当前平台或与可信配置冲突时，核对对应平台文档/配置。仍无法取得入口才停止数据库分支，记录 `platform_limit`（平台接入配置缺口），而非要求用户补内部 ID。仅当机构、目标环境或业务对象无法消歧时记录 `input_insufficient`，询问最小业务信息。

禁止从应用 clusterId、psdcloudId 相等关系或其他机构的 resourceId 推导资源入口；禁止遍历数字试探路由。平台映射变更需更新环境文件，不能静默尝试其他集群。

已知边缘机构码时，允许先以机构码搜索 EdgeMySQL 候选，再结合业务知识、资源返回、配置或日志核对库名和主机。尚未唯一匹配时不能执行 SQL，但不应将完整连接串当作资源搜索前置条件。

数据库渠道受阻只影响该证据目标；继续已有明确目标的其他已授权只读证据（例如按机构码 + UC 应用名发现应用并查日志），不绕过数据优先门禁进入代码推断。准确区分“尚未搜索”“搜索成功但零命中”“已发现但无查询权限”和“查询失败”；资源搜索可见不等于查询可用。

资源搜索读取 `data.totalCount` 和 `data.result[]`。根据资源类型至少核对 `resourceType`、`identity`、`masterHost`、`desc` 和业务给出的端口/库名，并遵守当前环境文件的额外匹配条件。保持查询条件完成分页后再判断唯一性；多候选不取第一条，无结果不代表资源不存在或已有查询权限。

优先从资源搜索响应读取 `clusterId/psdcloudId`，与本次已确认的搜索路由核对，再与精确命中的 `result.resourceId` 一起传给查询。若当前 CLI 未重复返回路由字段，才原样复用搜索时的已验证路由；字段冲突时停止，不覆盖或拼接不同命中的 ID：

```bash
ccloud-cli resource query \
  --cluster-id <search-route-clusterId> \
  --psdcloud-id <search-route-psdcloudId> \
  --resource-id <result.resourceId> \
  --raw-command '<bounded-read-only-command>'
```

进程退出码为 0 仍不等于业务成功；只有响应 `data.querySuccess == true` 才能记录数据库查询成功。
