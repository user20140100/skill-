# ccloud-cli 共享只读能力

本文件只定义应用部署版本、日志与数据库资源的只读发现、ID 传递和结果判断。它不负责安装、登录、账号环境准备或配置修复。只有当前流程确实需要 ccloud 证据时才读取。

所有示例中的 `ccloud-cli` 都表示 profile 已确认的绝对可执行文件路径。参数必须作为独立 argv 传递，不能把用户文本拼成 shell 命令。

## 1. 二进制来源

### managed-agent-v1

使用可信宿主注入的 `envConfig.ccloud.binPath`。路径不可用时返回 `CCLOUD_CLI_NOT_FOUND` 或 `CCLOUD_CLI_INVALID`，不得切换到 PATH 搜索。

### managed-chat-v1

使用可信宿主按配置或 PATH 解析并提供的绝对路径，首次有 ccloud 证据目标时用 `--help` 核验；不安装、登录或修改 CLI 配置。只读资源 SQL 使用宿主 `query_ccloud_resource` 工具，不通过 Bash 执行任意 raw-command。工具缺失只关闭该证据渠道，保留已确认材料和缺口。

### personal-local-v1

按以下顺序选择：

1. 用户本次提供的绝对路径。
2. `command -v ccloud-cli` 或宿主的等价 PATH 查询结果。
3. 都没有时，请用户提供绝对路径；不得扫描文件系统或自动安装。

候选只检查：绝对路径、普通文件、可执行，以及 `<absolute-path> --help` 成功。账号状态不属于 Skill 的二进制门禁。

## 2. 先确定对象位置

对象位置决定初始输入、搜索方式和数据库资源路由，三条链路不能混用：

| 对象位置 | 应用日志初始输入 | 数据库初始输入 | 当前观测接口资源路由 |
|---|---|---|---|
| 内网 / FAT | CCloud 页面 URL 或精确 `appId` | 主机、端口、库名 | `clusterId=50`、`psdcloudId=50`、实际资源类型 |
| 阿里云 / PRO | CCloud 页面 URL 或精确 `appId` | 主机、端口、库名 | `clusterId=101`、`psdcloudId=101`、实际资源类型 |
| 本地化 / 边缘 / 私有云 | `clusterName`（机构码）+ `appName`（应用标识） | `clusterName` + 主机、端口、库名 | `clusterId=101`、`psdcloudId=101`、`EdgeMySQL` |

资源路由是观测接口对接层按对象位置维护的入口，不是业务应用的 clusterId。上表是当前飞书文档和 2026-09-04 实测使用值；如果平台文档调整，必须同步更新，不能通过试探其他数字来发现。

## 3. CCloud 页面 URL 只提供 appId

线上页面 URL 形如：

```text
https://<ccloud-host>/project/apps/app-detail/container?tid=...&pid=...&mid=...&env=...&appid=...
```

查询日志时只从 `appid` 取得搜索关键字：

- `appid`：应用 ID，可用于 `search app --key-word`。
- `tid`、`pid`、`mid`：团队、项目、主项目标识，不能作为 `clusterId`。
- `env=fat|pro`：用于校验对象位置，不能替代搜索结果。

最终的 `appId`、`clusterId`、`psdcloudId` 必须以 `search app` 实际命中为准，不能仅从 URL 主机名或 `env` 拼出。

## 4. 应用日志

### 4.1 内网或阿里云

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

5. 使用这些 ID 查询日志：

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

### 4.2 本地化、边缘或私有云

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

在返回结果中精确匹配：

```text
result.appName == <appName>
```

不得省略 `--cluster-name`、传入未经小写转换的机构码后遍历跨机构结果，也不得在多候选时直接取第一条。无精确命中或存在多个精确命中时，停止并说明缺口。

命中后，从同一结果取得 `result.appId` 和边缘业务 `result.clusterId`，从外层 page 取得 `page.psdcloudId`：

```bash
ccloud-cli observe logs \
  --app-id <result.appId> \
  --cluster-id <result.clusterId> \
  --psdcloud-id <page.psdcloudId> \
  --start-time '<RFC3339-start>' \
  --end-time '<RFC3339-end>' \
  --size <1-5000>
```

这里的边缘业务 `clusterId` 只用于该应用的运行态和日志，不能用于 EdgeMySQL。

### 4.3 日志过滤语法

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

### 4.4 应用搜索输入

`search app --key-word` 必须有非空的 appId 或 appName，不能传 `--key-word ""` 来列举集群应用。名称只能来自用户输入、项目运行资产或已验证结果，仓库名不能直接充当应用名。缺少报错服务标识时，记录消费方证据缺口；继续已有明确目标的调查，必要时请用户补充服务名称，不遍历集群猜测。

### 4.4 部署详情与代码版本

部署相关代码查询先复用 4.1/4.2 的应用发现步骤取得同一命中的 appId 与业务 clusterId，无需先查询日志：

```bash
ccloud-cli app detail --app-id <result.appId> --cluster-id <result.clusterId>
```

此命令使用应用所属的业务集群 ID，不能使用数据库资源路由替代。参数以当前 CLI help 为准，不把 psdcloudId 或 URL 的 mid 当 clusterId。

校验命令成功、业务响应成功以及目标一致性；读取实际运行版本的版本号、分支及可用的 commit/tag、镜像、scenario、trafficWeight、replicaNum、availableReplicas、unavailableReplicas（只记录实际返回字段，不假定固定 JSON 层级）。灰度或多版本运行时按故障请求/Pod 证据匹配，不能取第一条、仅按版本号排序或将零可用副本自动排除为非故障目标。不存在部署记录、字段不足或无权限时报告缺口，不把默认配置当现场事实。

实测 `app detail` 响应以 `data.appId/clusterId` 标识目标，运行版本位于 `data.versions[]`，镜像版本取同一项的 `imageTag/fullImage`；`versionName`（如 v2）与 `versionNum` 是应用版本标识，不是 Git 版本。响应可能只有镜像 tag 而没有 branch/commit。本平台已确认 `<分支名>-<短 commit>-<构建时间>` 命名规则，此时按 `references/shared/code-mcp.md` 的映射步骤从右侧拆分 imageTag，使用短 commit 查询；不符合规则时才记录映射缺口。`app images` 只列最近镜像候选，未包含当前部署 tag 不代表当前部署不存在。

`references/shared/code-mcp.md` 定义部署版本与 Git ref 的映射规则；部署版本号或镜像 tag 未经映射不能直接传给代码工具。本步骤不授予部署、发布或切流权限。

## 5. 数据库资源

`search resource` 必须预先提供资源路由，所以它不能发现自己的 `clusterId`。资源路由按第 2 节的对象位置映射选择；应用搜索返回的业务 clusterId 不参与边缘数据库路由。

### 5.1 内网资源

```bash
ccloud-cli search resource \
  --cluster-id 50 \
  --psdcloud-id 50 \
  --type <MySQL-or-actual-type> \
  --keyword <host-or-database> \
  --from 0 \
  --size 100
```

### 5.2 阿里云资源

```bash
ccloud-cli search resource \
  --cluster-id 101 \
  --psdcloud-id 101 \
  --type <PolarDB-or-actual-type> \
  --keyword <host-or-database> \
  --from 0 \
  --size 100
```

### 5.3 本地化 EdgeMySQL

```bash
ccloud-cli search resource \
  --cluster-id 101 \
  --psdcloud-id 101 \
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

实际 CLI 的资源结果可能只返回 `resourceId`，不重复返回本次调用的 `clusterId/psdcloudId`。因此后续查询必须原样复用搜索时的路由，并使用精确命中的 `result.resourceId`：

```bash
ccloud-cli resource query \
  --cluster-id <search-route-clusterId> \
  --psdcloud-id <search-route-psdcloudId> \
  --resource-id <result.resourceId> \
  --raw-command '<bounded-read-only-command>'
```

进程退出码为 0 仍不等于业务成功；只有响应 `data.querySuccess == true` 才能记录数据库查询成功。

## 6. 只读与结果边界

- SQL 类资源只允许一条 `SELECT`、`SHOW`、`DESCRIBE`、`EXPLAIN`，或最终为 SELECT 的 `WITH ... SELECT`；禁止 DML、DDL、存储过程、多语句和跨库访问。
- `observe logs --query` 只允许受限条件表达式，不使用函数、子查询、`UNION` 或多语句。
- `observe logs` 的 `data` 是 LiteLog 返回并反序列化后的 JSON 值，可能是对象或数组；不要假定固定记录形状。
- 未授权应用不会出现在搜索结果中；直接查询可能返回无权限。资源搜索可见不代表拥有资源查询权限。
- 多候选、字段缺失、分页未覆盖或 ID 链不完整时停止并说明缺口，不猜测、不盲试。
- `repositoryId` 不得作为日志目标，也不能充当日志 `appId` 或任何 `clusterId`；机构码和 URL 中的 `mid` 同样不能作为任何 `clusterId`。

## 7. 已跑通的回归样例

以下值用于验证命令链路，不是其他业务对象的默认值。

| 场景 | 搜索输入 | 实测命中 | 日志结果 |
|---|---|---|---|
| 本地化 233i | `appName=uc-one-for-all`、`--cluster-name 233i` | `psdcloudId=101`、`appId=2e5820bc044c4ded809a8edd`、`clusterId=11048` | `stream=edge_app` |
| 内网 FAT | `appId=168ee7be66ae368d7645772cedf786b6f277d834` | `psdcloudId=50`、`clusterId=50`、`appName=帐号关系测试环境` | `stream=inner_app` |
| 阿里云 PRO | `appId=cf9916e7691acec301f8a1f95718146359fd5465` | `psdcloudId=101`、`clusterId=101`、`appName=UC服务生产` | `stream=ali_app` |

本地化 EdgeMySQL 回归：使用资源路由 `101/101`，按 `clusterName=233i` 搜索并精确匹配 `identity=seewo_class`、`masterHost=233i#mysql.seewo-edge-base`，得到 `resourceId=4797`；执行单条 `select 1` 时 `querySuccess=true`。
