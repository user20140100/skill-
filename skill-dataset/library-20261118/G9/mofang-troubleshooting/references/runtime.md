# 现场资源发现与工具调用方法

## 从 Wise 获取当前资源定义

不在 skill 内维护应用 ID、数据库资源 ID、集群路由、服务依赖、库表关系或仓库映射。这些资料统一在飞书维护，经 Wise 检索读取。

1. 先根据问题选择证据类型，再检索相应定义。当前静态属性通常需要库表与数据库资源；请求失败才需要应用与日志资源；配置问题才需要应用与 Apollo 路由。不要一次性发现所有 CCloud 资源。例如按需搜索 `<产品> <领域> 数据库 <环境>`、`<领域> 底层服务 日志`。
2. 使用命中的 knowledge_id/chunk_id 读取完整相关段落，必要时扩展上下文或按页读取文档。Top 5 不是完整资源目录，不因一次没命中就认定资源未登记。
3. 只建立当前证据路径所需的对应关系。数据库查询需要实际库名、资源类型、clusterId、resourceId 和必要路由；日志查询才需要入口/底层服务职责、appId、clusterId 和 psdcloudId。记录定义的来源链接和同步时间，不跨环境混用，不拿业务 project_id 代替平台项目 ID。
4. 已有清晰且时效可接受的资源定义时，可用本次真实只读操作验证；目标缺失、模糊、冲突或查询失败时再用 CCloud 搜索核对存在性、环境和路由。仓库地图只用于代码定位，不能替代所需的跨层资源定义。文档与现场不一致时保留差异并消歧；不盲试资源 ID，不回退到历史 skill 清单。
5. 定义缺失或冲突时，继续能做的知识分析和已明确目标的调查，说明缺少哪些资源字段，并建议在飞书补齐。补齐后应等待/确认 Wise 同步，再重新检索；不能把文档修订自动当成 Wise 已更新。

## 命令入口

首次实际使用某个 CLI 时按 [cli-setup.md](cli-setup.md) 做对应的按需检查；不要求另一个无关 CLI 同时就绪。执行现场查询时按需读取对应命令 `--help`；出现认证失效时登录并只重试原查询一次，不继续猜测。现有 CCloud 和 seewo-mgr skills 可补充当前 CLI 用法。以下是已核验命令形状，尖括号需替换为已确认的值：

```bash
ccloud-cli search app --key-word <appId或应用名> --search-type 2 --from 0 --size 20
ccloud-cli app comprehensive --help
ccloud-cli observe logs --app-id <appId> --cluster-id <clusterId> --psdcloud-id <psdcloudId> --start-time <RFC3339> --end-time <RFC3339> --size 50
ccloud-cli search resource --cluster-id <clusterId> --psdcloud-id <psdcloudId> --type <MySQL或PolarDB> --keyword <库名> --from 0 --size 100
ccloud-cli resource query --cluster-id <clusterId> --psdcloud-id <psdcloudId> --resource-id <resourceId> --raw-command <单条只读SQL>
```

应用搜索在 `data.pages[].result[]` 精确匹配，`psdcloudId` 来自同一外层 page，不取第一条模糊命中。资源搜索用 `data.result[]` 的 resourceId 和本次搜索路由；执行查询后必须检查 `data.querySuccess == true`。

日志 `--query` 使用条件表达式，例如 `message LIKE '%关键词%'`，不写 SELECT/FROM/WHERE。输入含单引号时正确转义，动态值使用独立 argv 传递，不拼成可执行 shell 文本。历史 IP 不能用当前容器搜索结果直接认定服务归属；CLI 需要 app-id 时不套用文档里未经核验的“省略 appid”方案。

## Apollo 动态发现

通过目标 CCloud 应用的 `app comprehensive` 获取 `.data.appOtherConfig.apolloAppId`；用当前 CLI help 确认所需 ID 参数。不可从仓库名猜 Apollo ID。

已验证的默认 namespace 查询模板：

```text
http://fat.conf.cvte.com/configfiles/json/{apolloAppId}/default/application
http://pro.conf.cvte.com/configfiles/json/{apolloAppId}/default/application
```

先固定环境及 appId，再按问题取相关键。不要输出整个配置；JDBC URL 内嵌密码等凭据需隐藏。没有 jdbc 键不表示没有数据库，其他 namespace/cluster/配置来源需有依据再查。发布配置和实例实际生效配置分开判断。

## 来源时效

以每次 Wise 返回的 source_url 和 source_updated_at 记录引用，不把原文文档 ID 固定在流程中。需要核对原文的新修订时使用本机可用的飞书读取能力；无飞书权限时保留 Wise 正文及同步时间，说明时效限制。不要宣称 Wise 内容一定等于实时飞书内容。

现场证据可以保存在当前任务的排查记录中，注明时间、环境和来源，但不能回填成 skill 的长期资源目录。
