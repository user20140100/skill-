# 边缘数据库只读查询（ccloud-cli）

本 Skill 用 `ccloud-cli` 查询目标机构的现有配置，为 SQL 生成提供证据。`resource query` 只允许只读命令；生成的 INSERT、UPDATE、DELETE 只作为业务应用包交付，不通过 CLI 执行。

## 1. 确定目标与 CLI

- 取得完整机构码（边缘 `clusterName`），去除首尾空白并转小写。机构码不是 `clusterId`；不能按前缀匹配或从应用集群 ID 推导数据库资源路由。只有机构码而没有应用名时可直接查数据库，不必先搜索应用。
- 当前仓库的 `mofangyun-local-application/src/main/resources/application.properties` 指向 `mysql.seewo-edge-base:3306/mofang_local`。它是 `mofang_local` 的库名与主机线索；若目标机构有已验证的专属配置，以目标配置为准。
- 个人本地会话优先使用用户给出的绝对可执行路径，否则用 `command -v ccloud-cli`。只检查候选文件可执行且 `<path> --help` 成功；不自动安装。受控宿主若提供可信 `envConfig.ccloud.binPath`，只用该路径，不回退到 PATH。
- 只读查询遇到 `AUTH_REQUIRED` 时按 CLI 登录流程处理后重试；无资源查询权限时报告权限缺口。不能把进程退出码为 0、搜索可见或用户声称可用视为查询成功。

## 2. 发现 EdgeMySQL 资源

本平台的 CVTE 阿里云鲸云 EdgeMySQL 管理路由为 `resourceClusterId=101`、`resourcePsdcloudId=101`；来源为[观测系统开放接口](https://cvte.feishu.cn/wiki/UVtgwBF9nil2E5khJVJct8fdn5g)及参考排障路由 Skill 的边缘资源契约，2026-09-16 已核对。该映射只适用于此平台的 **资源搜索与查询**，不能用于应用日志，也不是任何机构的 `resourceId`。若目标专属可信配置给出其他资源路由，先核对冲突；不猜测或试探数字。若当前平台不受该映射覆盖且无法核实资源路由，报告平台接入配置缺口，不要求业务方提供内部 ID。

用规范化机构码搜索；示例中的路由是上述平台映射，`<clusterName>` 必须取本次目标：

```bash
ccloud-cli search resource \
  --cluster-id 101 \
  --psdcloud-id 101 \
  --type EdgeMySQL \
  --keyword <clusterName> \
  --from 0 \
  --size 100
```

读取 `data.totalCount` 和 `data.result[]`，保持相同条件分页直到覆盖全部结果。对 `mofang_local` 至少核对：

```text
result.resourceType == EdgeMySQL
result.identity == mofang_local
result.masterHost == <clusterName>#mysql.seewo-edge-base
```

`masterHost` 中的机构码按去空白、忽略大小写比较，主机名按已验证配置核对；同时检查 `desc` 及可用的端口、库名信息。仅在精确匹配唯一时使用该命中的 `result.resourceId`。零命中、多命中、分页未覆盖或字段冲突时停止查询并说明缺口，不取第一条。`masterHost` 的 `#` 组合仅用于匹配资源，不能自行拆出或拼接隧道路由。

若需要核对 `seewo_class.tb_service_open`，用同一路由和机构码再搜索 `identity=seewo_class` 的 EdgeMySQL，按该库已验证的主机配置与返回字段唯一匹配；不能把 `mofang_local` 的 `resourceId` 复用给 `seewo_class`。

## 3. 执行只读查询

优先使用搜索响应中的 `clusterId/psdcloudId`，并与本次搜索路由核对；若响应未重复返回，才原样使用已验证的搜索路由。发现冲突时停止。将路由和**同一命中**的 `resourceId` 传给查询；业务应用的 `clusterId`、应用搜索页的 `psdcloudId` 都不能代替它们：

```bash
ccloud-cli resource query \
  --cluster-id <resourceClusterId> \
  --psdcloud-id <resourcePsdcloudId> \
  --resource-id <result.resourceId> \
  --raw-command '<single-read-only-SQL>'
```

命令参数必须作为独立 argv 传递，不能把用户文本直接拼进 shell。优先用进程 API 将 SQL 作为单独参数传入；若必须经过 shell，正确转义整个参数。SQL 中由用户提供的字符串要按 SQL 字面量规则转义；每次只发一条有明确范围的 `SELECT`、`SHOW`、`DESCRIBE`、`EXPLAIN` 或最终为 SELECT 的 `WITH ... SELECT`。禁止 DML、DDL、存储过程、多语句和跨库访问。不要用 `resource query` 验证生成的写入 SQL。

仅当命令执行成功且响应 `data.querySuccess == true` 时，才能使用 `data.result` 作为数据库证据；`querySuccess=false` 应读取 `data.message` 并标记查询失败。SQL 类资源的 `data.result` 可能是文本表格，不要假设是 JSON 行数组。

## 4. 本 Skill 需要的查询

先以单条 `SELECT 1 AS connectivity_check` 验证目标库可查询，再按诉求查现有配置。下列语句在**已定位的 `mofang_local` 资源**上执行，不带跨库前缀：

```sql
-- 用户未指定现有服务时，完整分页获取候选
SELECT DISTINCT c_service_code
FROM t_app_role_power_config
WHERE c_delete_time = 0
ORDER BY c_service_code
LIMIT 200 OFFSET 0;

-- 已知服务的默认角色；将值安全转义为 SQL 字面量
SELECT DISTINCT c_role_code, c_role_name, c_role_level
FROM t_app_role_power_config
WHERE c_service_code = '<service_code>' AND c_delete_time = 0
ORDER BY c_role_code, c_role_name, c_role_level
LIMIT 200 OFFSET 0;

-- 需要确认权限点或父权限时，按已知编码定向查询
SELECT c_code, c_name, c_parent_code, c_order
FROM t_power_config
WHERE c_code = '<power_code>' AND c_delete_time = 0
LIMIT 2;
```

这些是分别执行的查询，不是一个多语句命令。需要完整角色或服务集合时，保持稳定排序，逐页增加 `OFFSET` 直到最后一页；不要把首批 200 行当作全部。目标表或字段与模板不一致时先用 `SHOW COLUMNS FROM <known-table>` 核对，只对本 Skill 涉及的已知表执行，不凭模板臆造结果。
