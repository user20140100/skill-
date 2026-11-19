# ccloud-cli：阿里云

仅在 [能力入口](../ccloud-cli-tools.md) 已确认当前证据目标位于阿里云时读取。按目标只读应用或数据库章节，不加载其他环境文件。

## 1. 应用发现

线上页面 URL 形如：

```text
https://<ccloud-host>/project/apps/app-detail/container?tid=...&pid=...&mid=...&env=...&appid=...
```

查询日志时只从 `appid` 取得搜索关键字：

- `appid`：应用 ID，可用于 `search app --key-word`。
- `tid`、`pid`、`mid`：团队、项目、主项目标识，不能作为 `clusterId`。
- `env=fat|pro`：用于校验对象位置，不能替代搜索结果。

最终的 `appId`、`clusterId`、`psdcloudId` 必须以 `search app` 实际命中为准，不能仅从 URL 主机名或 `env` 拼出。

`search app --key-word` 必须有非空的 appId 或 appName，不能传 `--key-word ""` 来列举集群应用。名称只能来自用户输入、项目运行资产或已验证结果，仓库名不能直接充当应用名。缺少报错服务标识时，记录消费方证据缺口；继续已有明确目标的调查，必要时请用户补充服务名称，不遍历集群猜测。

1. 从业务输入或页面 URL 取得精确 `appId`。

2. 搜索应用：

```bash
ccloud-cli search app --key-word <appId> --search-type 2 --from 0 --size 20
```

3. 在 `data.pages[].result[]` 中精确匹配 `result.appId == <appId>`。
4. 从同一条命中链取得：

```text
page.psdcloudId
result.appId
result.clusterId
result.appName
result.clusterName
```

读取 `data.totalCount` 和各页 `count/from/size`，按各 psdcloud 的分页覆盖范围保持原条件继续查询。覆盖完整后唯一精确命中才继续；无命中、多候选或分页无法覆盖时报告缺口，不取第一条，不混用不同页与不同结果的 ID。

唯一命中后，查日志读取 [common.md 第 1 节](common.md#1-查询应用日志)，需要过滤时追加第 2 节；查部署版本读取 [common.md 第 3 节](common.md#3-部署详情与代码版本)。

## 2. 数据库发现

输入为主机、端口与库名。搜索前读取 [common.md 第 4 节](common.md#4-数据库路由匹配与只读查询)，使用下述已维护的平台入口搜索；用户无需提供内部资源路由 ID。

当前平台资源入口：`resourceClusterId=101`、`resourcePsdcloudId=101`。适用范围仅为**CVTE 阿里云鲸云管理的数据库资源**，不是所有同类环境的通用默认值，也不能用于应用日志。依据为本平台[观测系统开放接口](https://cvte.feishu.cn/wiki/UVtgwBF9nil2E5khJVJct8fdn5g)及仓库现有 `troubleshooting-ccloud-cli` 资源路由契约；2026-09-16 已核对。若可信宿主或目标配置明确给出其他管理路由，以目标专属映射为准；存在冲突先核对平台配置，不试探数字。没有覆盖当前平台的映射时按 common.md 的路由缺口规则处理。

下列占位符使用上述已确认的管理路由，不等待用户补资源页面链接：

```bash
ccloud-cli search resource \
  --cluster-id <resourceClusterId> \
  --psdcloud-id <resourcePsdcloudId> \
  --type <PolarDB-or-actual-type> \
  --keyword <host-or-database> \
  --from 0 \
  --size 100
```

按主机、端口、库名和资源类型核对唯一候选；同一主机多个库时，不能只匹配主机。随后按 common.md 第 4 节保留资源路由执行只读查询并检查 `querySuccess`。

## 3. 历史样例（非默认值）

以下仅保留历史验证证据，不能作为本次查询输入或替代重新搜索。

| 场景 | 搜索输入 | 实测命中 | 日志结果 |
|---|---|---|---|
| 阿里云 PRO | `appId=cf9916e7691acec301f8a1f95718146359fd5465` | `psdcloudId=101`、`clusterId=101`、`appName=UC服务生产` | `stream=ali_app` |
