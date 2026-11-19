# ccloud-cli：本地化、边缘与私有云

仅在 [能力入口](../ccloud-cli-tools.md) 已确认当前证据目标位于本地化 / 边缘 / 私有云时读取。按目标只读应用或数据库章节，不加载其他环境文件。

## 1. 应用发现：机构码 + 应用

`search app --key-word` 必须有非空的 appId 或 appName，不能传 `--key-word ""` 来列举集群应用。名称只能来自用户输入、项目运行资产或已验证结果，仓库名不能直接充当应用名。缺少报错服务标识时，记录消费方证据缺口；继续已有明确目标的调查，必要时请用户补充服务名称，不遍历集群猜测。

业务必须提供 `clusterName` 和 `appName`。机构码通常是 `clusterName`，但机构码本身不能直接当 `clusterId`。

调用前必须将 `clusterName` 去除首尾空白并转换为小写，再通过 `--cluster-name` 传入，由服务端限定目标集群。后续不得使用用户输入的原始大小写值替代这个规范化结果：

```bash
ccloud-cli search app \
  --key-word <appName> \
  --cluster-name <lowercaseClusterName> \
  --search-type 2 \
  --from 0 \
  --size 20
```

在 `data.pages[].result[]` 中同时核对应用与集群（返回集群名保留原始大小写，比较时 trim 后忽略大小写）：

```text
result.appName == <appName>
lowercase(trim(result.clusterName)) == <lowercaseClusterName>
```

不得省略 `--cluster-name`，也不得在集群未找到、重名或无权限时去掉该条件重试全局搜索。机构码必须是完整集群名，不能按前缀匹配（例如 `tvfn` 不等于 `tvfn-1`）。

读取 `data.totalCount` 与各页 `count/from/size` 判断覆盖范围；未覆盖时保持原查询条件继续分页，不能把首批零命中当成应用不存在，也不能把首批单条精确命中当成全量唯一。应用搜索按每套 psdcloud 分别分页。覆盖完整后仍无精确命中或有多个候选时，说明缺口或请求选择，不取第一条。

例如用户提供机构码 `TVFN`、应用 `mofangyun-local` 时：

```bash
ccloud-cli search app \
  --key-word mofangyun-local \
  --cluster-name tvfn \
  --search-type 2 \
  --from 0 \
  --size 20
```

这里只固定本次输入，不预填任何应用或集群 ID。

唯一命中后，从同一结果取得 `result.appId/result.clusterId`，从所在页取得 `page.psdcloudId`。业务 clusterId 与 psdcloudId 不能互换。

查日志读取 [common.md 第 1 节](common.md#1-查询应用日志)，需要过滤时追加第 2 节；查部署版本读取 [common.md 第 3 节](common.md#3-部署详情与代码版本)。边缘业务 clusterId 只用于该应用的运行态与日志，不能用于 EdgeMySQL。

## 2. 数据库发现：EdgeMySQL

输入为机构码（完整 clusterName）和业务数据库线索。只查数据库不要求先搜索应用；已知机构码即可先搜索候选，库名与主机从业务知识、运行资产、日志或搜索结果核对，查询前必须唯一确认目标。搜索前读取 [common.md 第 4 节](common.md#4-数据库路由匹配与只读查询)。

应用搜索只能证明业务集群与承载它的 psdcloud，不能据此推导 EdgeMySQL 的资源 clusterId。禁止将应用业务 clusterId 或 page.psdcloudId 自动填入资源 clusterId；以下资源入口来自独立的平台映射。机构码去除首尾空白并转换为小写；返回 `masterHost` 中的机构码部分忽略大小写核对，但数据库主机仍按已验证地址核对。

当前平台资源入口：`resourceClusterId=101`、`resourcePsdcloudId=101`。适用范围仅为**CVTE 阿里云鲸云管理的 EdgeMySQL 资源**，不是所有同类环境的通用默认值，也不能用于应用日志。依据为本平台[观测系统开放接口](https://cvte.feishu.cn/wiki/UVtgwBF9nil2E5khJVJct8fdn5g)及仓库现有 `troubleshooting-ccloud-cli` 资源路由契约；2026-09-16 已核对。若可信宿主或目标配置明确给出其他管理路由，以目标专属映射为准；存在冲突先核对平台配置，不试探数字。没有覆盖当前平台的映射时按 common.md 的路由缺口规则处理。

下列占位符使用上述已确认的管理路由，不等待用户补资源页面链接：

```bash
ccloud-cli search resource \
  --cluster-id <resourceClusterId> \
  --psdcloud-id <resourcePsdcloudId> \
  --type EdgeMySQL \
  --keyword <clusterName> \
  --from 0 \
  --size 100
```

资源搜索读取 `data.totalCount` 和 `data.result[]`。根据资源类型至少核对 `resourceType`、`identity`、`masterHost`、`desc` 和业务给出的端口/库名。本地化数据库必须同时满足：

```text
result.identity == <databaseName>
result.masterHost == <clusterName>#<databaseHost>
```

上式的 clusterName 比较按前述机构码规范化处理。`masterHost` 的组合形式仅用于匹配返回资源，不用于构造隧道路由参数；隧道路由由服务端从资源实例配置解析。唯一命中后按 common.md 第 4 节保留资源路由执行查询并检查 `querySuccess`。

## 3. 查询样例与历史回归（非默认值）

以下历史值仅用于说明 ID 传递，不能作为运行时配置或替代本次搜索。2026-09-16 实测 `mofangyun-local + --cluster-name tvfn` 唯一命中 `appId=5e858ff1a9e54ce0970ca31e`、业务 `clusterId=10323`、`page.psdcloudId=101`，再次说明业务 clusterId 与 psdcloudId 不相同。此次仅验证应用发现，未查询日志或数据库。

| 场景 | 搜索输入 | 实测命中 | 日志结果 |
|---|---|---|---|
| 本地化 233i | `appName=uc-one-for-all`、`--cluster-name 233i` | `psdcloudId=101`、`appId=2e5820bc044c4ded809a8edd`、`clusterId=11048` | `stream=edge_app` |

本地化 EdgeMySQL 回归：使用资源路由 `101/101`，按 `clusterName=233i` 搜索并精确匹配 `identity=seewo_class`、`masterHost=233i#mysql.seewo-edge-base`，得到 `resourceId=4797`；执行单条 `select 1` 时 `querySuccess=true`。

2026-09-16 资源链路回归：按上述平台管理路由搜索 `eedh`，返回 7 个 EdgeMySQL 候选；按机构码、`identity` 和主机分别唯一定位 `seewo_class`（resourceId=12478）与 `mofang_local`（resourceId=15611），两者执行单条 `SELECT 1 AS connectivity_check` 均为 `querySuccess=true`。这些 resourceId 仅为回归证据，实际排障必须重新发现。
