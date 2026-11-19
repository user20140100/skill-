# 取证与工具

## 目标与时间

记录仓库路径/HEAD、服务与环境、appId、clusterId、psdcloudId（跨鲸云路由）、版本、实例/Pod、运行时、数据源、绝对起止时间和时区。ID 来自用户、config show 或真实搜索结果；不复用其他审计的 ID。共享库里的 SQL 需要定位调用应用，不能全归因到当前服务。实例级指标保留实例维度，不用集群平均掩盖单副本异常。

先 `ccloud-cli config show`；缺失时按 ccloud-search 发现，不为只读审计强行 config init。多候选先缩小范围；目标仍不唯一时询问。代码扫描无需等待线上访问完成。

## CLI 能力发现

先读当前 `ccloud-cli --help`，按规则读取 `observe/app/resource/search --help` 及具体 action help；相关 action 不存在时再按 CLI 技能刷新 metadata。不假设所有版本均支持同一能力。以下为已核实的查询方式，执行时以实际 help 为准。尖括号是待替换参数，不是可执行默认值。

## 规则与 CLI 能力矩阵

以下于 2026-10-26 对照本机 CLI help 核查；它描述命令能力，不代表目标服务已有相应指标或本次调用成功。后续扫描按当前 help 复核，不把此表当永久能力上限。

| 规则/取证 | CLI 优先路径 | 能力边界与补证 |
|---|---|---|
| 目标、资源、负责人 | `config show`、`search app/resource`、`app contact` | 使用真实返回的稳定 ID 与跨鲸云路由；不输出敏感配置 |
| 慢 SQL 表结构与执行计划 | `resource query` 执行 `SHOW CREATE TABLE`、`SHOW INDEX`、普通 `EXPLAIN` | 尚未发现历史慢 SQL 专用 action；历史记录继续使用指定看板，不把普通 EXPLAIN 当实际耗时。仅只读、有界查询 |
| 告警策略 | 当前未发现专用 action | computer-use 核查新旧实际规则、继承、绑定及通知；不能用指标或联系人查询代替有效告警验证 |
| GC | `observe metrics-list` → `metrics`；`observe logs`；`app pods/detail` | **必须 CLI 取证**；目录、原始序列或已采集日志缺失时未完成，不用浏览器替代 |
| STW/运行期插桩 | `observe logs/logs-count`、目录中真实存在的暂停指标、`app pods/detail/comprehensive` | 没有专用 STW action；只有已采集的 safepoint/agent 日志或相应指标才支持判断。应用日志无命中不代表无暂停 |
| 高频慢接口 | `observe transactions` → `transaction-metrics`，`traces` → `trace-detail`；`access-logs` 补充入口 | 排名、时序、样本含义不同；Trace 非全量，接口指标 ID 来自 transactionMetrics |
| 线程池/连接池 | `observe metrics-list` → `metrics`、`logs/logs-count`；配置与源码 | 没有专用“池打满”命令；仅查询目录暴露的池指标，缺失时不能判正常 |
| 容量、实例和发布 | `app detail/pods/comprehensive`、目录中的容量指标、`app logs --previous` | Pod 快照不覆盖已删除实例；previous 仅上一个终止容器；配置不代表历史运行效果 |
| 依赖、重试与异步 | `observe dependencies`、Trace、指标/日志；`search resource` → `resource query` | 资源类型/允许命令按 ccloud-resource-query 与 help 确认；无专用 MQ 全量观测承诺，不重放消息 |

对每项分别记录：① CLI 支持且取得有效数据；② CLI 支持但接口/鉴权/超时错误；③ 查询成功但指标未暴露或日志未采集；④ 当前 CLI 未提供。只有第四类才能写“CLI 暂不支持”。错误文本含“用户无权限”时保留原文，但不能单凭文本断定根因是账号权限，可能是 CLI/服务端 bug；已知 bug 标为平台工具阻塞，不能直接生成“给用户加权限”的确定性修复结论。

CLI 支持的能力先查询并保留命令、返回摘要和实际覆盖。失败后检查参数、身份及路由；已知 bug 不反复重试或自动升级，修复后再验证。GC 按强制 CLI 规则保持未完成；其他规则确需页面补证时明确失败原因、替代来源与覆盖限制。扫描报告注明各项实际来源，不把 help 核查写成线上验证成功。

### 查询示例

```bash
ccloud-cli observe metrics-list --app-id <appId> --cluster-id <clusterId> --start-time <RFC3339开始> --end-time <RFC3339结束>
ccloud-cli observe metrics --app-id <appId> --cluster-id <clusterId> --metrics-item-id <目录返回的ID> --start-time <开始> --end-time <结束>
ccloud-cli observe transactions --app-id <appId> --cluster-id <clusterId> --sort-by p99 --limit 100 --start-time <开始> --end-time <结束>
ccloud-cli observe traces --app-id <appId> --cluster-id <clusterId> --transaction-name <接口原名> --min-duration-ms <服务阈值> --limit 100 --start-time <开始> --end-time <结束>
ccloud-cli observe trace-detail --app-id <appId> --cluster-id <clusterId> --trace-id <真实traceId> --start-time <开始> --end-time <结束>
```

- 跨鲸云 observe 查询保留搜索返回的 `--psdcloud-id`，不能与 clusterId 混用。
- metrics-list 返回什么才查询什么；GC/线程/连接池指标的 ID、单位、counter/gauge/rate 含义都不能猜。查看 units、timeUnit、warnings。当前指标、接口和 Trace 能力不支持边缘集群；不可用时标明缺口。其他规则可按各自要求使用已有监控/日志补证；GC 必须经 ccloud-cli 获取，失败时不得用浏览器/APM 页面替代。
- 当前指标与 Trace 相关查询窗口至多 24h；更长基线拆分查询。`transactions` 的 p99/errorRate/tpm 排名分别查看，前 N 名不是完整接口清单。
- `transaction-metrics` 用 metrics-list 返回的 transactionMetrics ID 和 transactions 返回的接口原名；不能把全应用指标 ID 直接代入。
- `observe logs`、`logs-count`、`access-logs`、`dependencies` 用于日志/入口/依赖补证。LiteLog 与 ES 的过滤语法不同，以 help 和返回存储类型为准，不捏造 SQL 聚合能力。logs-count 是匹配日志数量，只有一条日志确实对应一个事件时才可作事件数。
- 检查 effective window、partial、failedShards、timedOut、warnings 和 size/limit。ES partial 时计数仅是下界，包括零；Trace 是慢请求样本，无分页，不能计算全量慢请求比例。
- 只读数据库走 ccloud-resource-query；app detail/pods/logs 等走 ccloud-runtime-debug。当前/previous 日志是快照，不代表全天日志完整。

## 统一证据对象

每项证据编号 E001…，保存来源链接或相对文件位置、查询条件、实际窗口、采集时间、实例/版本、指标名和单位、结果摘要、采样/截断情况。源码给出路径、行号、方法和触发条件；配置值区分默认与线上生效值。报告只保留必要的脱敏信息，不复制 token、密码、用户明细或全部 Trace 入参。

数据缺失时把“补齐某项指标/访问权限/有效窗口”列为观测待办；仅当明确需要用户提供且影响目标选择时提问，不反复重试相同权限失败。
