# 共享代码 MCP 查询规则

本文件供 QA 与 TROUBLESHOOTING 共同使用，定义代码来源、工具调用和版本证据。复用当前请求已经确认的目录和项目详情，不重新分类或另建目录请求；代码工具是否携带 `requestId` 以当前工具 schema 为准，不根据个人本地运行模式推断认证通道。

## 何时读取

- QA 完成共享三层知识加载后，需要核验接口签名、参数、废弃状态、实现或处理资料冲突时读取；managed 使用 `qa:shared:code-mcp`。责任路由、越界、未知类型和纯配置值查询不执行代码查询。
- TROUBLESHOOTING 仅在排障 Core 的数据优先门禁允许、已建立代码证据目标时读取。共享工具规则不改变根因资格或独立复审。
- 代码是按需核验渠道，不是每次必读的第四层知识；源码结论只适用于实际返回的代码版本。

## 选择规则

1. 从当前 `projects[]` 唯一确定目标项目，记录 `effectiveCodeSource.mode=aiTroubleShot_mcp` 和 `effectiveCodeSource.projectUid`。
2. 四个只读工具 `list_code_files`、`search_code_files`、`read_code_file`、`get_file_outline` 使用 `projectUid` 选择项目主仓库 `repositories[0]`，使用 `ref` 指定 Git 版本。调用方不传 `repositoryId` 或 URL，不通过修改项目配置切换分支。
3. 排障代码目标必须先按下节查询部署详情并传 `ref`，不得把项目 `defaultRef` 当部署版本。只有不涉及具体部署的 QA 源码参考查询，才可省略首次 `ref` 使用配置版本，并明确其参考性质；QA 若需要核对某环境实际运行版本，也须有可信部署记录；当前 QA 宿主不提供 ccloud 能力或不允许读取共享 ccloud 规则时，记录部署证据缺口，不绕过模式门禁或切换排障通道。
4. 多仓库项目当前只查询主仓库；核对应用对应的代码是否在主仓库。其他仓库不通过猜测 projectUid 或覆盖仓库参数访问；目标不在主仓库时记录能力缺口。
5. `app_env` 描述宿主运行环境，不替代问题环境或项目身份。`ccloudInfo[].appId` 只用于运行资产，不是 projectUid。项目或主仓库 URL 缺失时记录配置缺口，不借用其他环境同名项目。显式 ref 查询不依赖 defaultRef。

## 从目标部署取得 ref

1. 首次建立部署相关代码目标时读取 `references/shared/ccloud-cli-tools.md`，遵循当前 Profile 的 CLI 能力门禁。从问题输入和选中项目的 `ccloudInfo[]` 确认目标应用与业务集群，按共享应用发现规则取得精确 `appId/clusterId`，调用 `app detail --app-id <appId> --cluster-id <clusterId>`。部署查询失败、目标不唯一或工具不可用时停止该代码目标，保留其他证据，不自动改用项目配置分支。
2. 以实际响应的运行版本记录为准，保留 appId、clusterId、查询时间、版本号、分支、可用的 commit/tag、镜像、流量与副本状态。字段缺失不得补造；不把待发布版本、构建列表最新版本或版本列表第一条认定为实际运行版本。多版本并存时，按故障 Pod/请求证据定位；无法消歧时记录缺口，需要分别调查时为各版本建立独立来源。
3. `effectiveCodeSource.requestedRef` 优先使用部署记录关联的 commit SHA，其次是有可信构建/发布映射的 Git tag。版本号、appVersionId 或镜像 tag 本身不等于 Git ref；不能猜测转换规则，也不能仅因某个同名 Git tag 存在就认定关联。只有部署分支时可以查询该实际分支，但标记“部署分支参考，尚未匹配部署 commit”，不能声称读到的就是已部署源码。没有可用部署 ref 时停止代码目标。
4. 故障发生在历史时段时，以该时段的可信部署记录为准；当前详情仅证明查询时状态。明确指定其他版本的分析可遵从用户目标，但须标记与现场部署的差异。
5. 将部署证据、版本匹配状态和 projectUid/requestedRef 一并记录到 `effectiveCodeSource`，随代码调查任务交接，不能只交接配置分支。

### 已确认的 CCloud 镜像 tag 映射

本平台已确认镜像 tag 命名为 `<分支名>-<短 commit>-<构建时间>`。当 `data.versions[]` 的已选部署记录只有 imageTag 时，按此规则取得 Git 版本，无需再次要求独立 branch/commit 字段：

- 从右侧拆分最后两个 `-`：最后一段为构建时间，中间段为短 commit，其余全部为分支名。分支名允许包含 `-`，不能按固定左侧下标取值。
- 三部分均不能为空，短 commit 必须是 7–40 位十六进制字符；不符合规则时报告映射缺口，不使用项目默认分支。构建时间保留原值，不据此推算完整年份或故障时部署状态。
- 将解析来源记为“已确认的 CCloud 镜像命名规则”，保留原始 imageTag、分支、短 commit 和构建时间。分支只作版本背景，实际 `ref` 使用解析出的 commit，不传完整 imageTag 或分支最新 HEAD。
- 示例：`version2603B-4322d1ec-03271927` → 分支 `version2603B`、`ref=4322d1ec`、构建时间 `03271927`。首次响应的完整 resolvedCommit 必须以该短 SHA 开头（忽略大小写）；后续固定完整 commit。
- 若响应同时提供独立 commit，必须与 tag 解析结果一致；不一致、短 SHA 有歧义或无法解析时停止并报告，不换分支重试。其他来源且命名规则未经确认的镜像不能套用此规则。

## MCP 调用与版本核对

先核对当前工具 schema 包含 ref；部署查询不支持 ref 时记录工具版本缺口，不能删去 ref 重试。再按以下范围调用：列文件使用 `relativePath/filePattern/maxFiles`，搜索使用 `keyword/relativePath/filePattern/caseSensitive/contextLines/maxMatches`，读取使用 `relativePath/startLine/endLine`，大纲使用 `relativePath`。先以问题相关的符号或文件模式缩小范围，再读取必要片段，保留截断、分页和缓存状态。

四个只读代码工具均按当前工具 schema 传参，QA 与 TROUBLESHOOTING 使用同一规则：

- schema 声明 `requestId` 时，复用当前 `get_project_route_catalog` 返回的值，不自行生成或借用其他请求的值。
- schema 未声明 `requestId` 时，不添加该字段，正常调用；不能仅因缺少该字段就认定工具过旧、阻断查询或要求重新连接 MCP。
- managed QA 由宿主绑定请求上下文，不向模型工具自行添加宿主控制的字段。

身份由当前宿主建立，不切换令牌或调用另一条通道绕过限制。建立部署快照的首次调用传 `refresh=true`，避免未过 TTL 的仓库缓存缺少新部署 ref；后续固定 commit 并省略 refresh，不以反复刷新代替证据核验。

搜索示例（当前工具 schema 未声明 `requestId` 时）：

```json
{"projectUid":"<当前目录中目标项目的 projectUid>","ref":"<部署记录对应的 Git commit/tag/分支>","refresh":true,"keyword":"Auth4AToUc","contextLines":3}
```

若 schema 声明 `requestId`，在上述示例中增加当前目录返回的 `requestId`，其他代码工具同样处理。

若实际调用返回 `VALIDATION_FAILED`，优先检查 `error.data.field` 与 `error.data.message`。明确提示缺少 `requestId` 且 schema 已声明该字段时，补齐当前目录返回值后重试一次；只有实际错误明确要求该字段、而 schema 又未声明它时，才报告契约不一致并建议刷新工具定义。没有具体字段提示时保留原始错误和缺口，不猜测校验原因，也不把查询失败当作业务能力不存在。

1. 读取文件时额外传仓库内 `relativePath` 及所需行号；不传绝对路径、`..` 或从本地目录推导的路径。
2. 每次成功响应都核对 `projectUid` 与请求一致、`requestedRef` 与显式传入 ref 一致，并记录 `repositoryId`、`requestedRef`、40 位 `resolvedCommit`、`fetchedAt` 和 `stale`。缺少身份或版本信息时停止该代码目标并记录工具协议缺口。
3. 首次成功后记录 repositoryId/resolvedCommit，后续调用传相同 projectUid 和 `ref=resolvedCommit`，不再传分支名或刷新。已有部署 SHA 时核对返回 commit（短 SHA 必须由后端唯一解析且匹配返回前缀）。仓库身份或 commit 不一致时停止该代码目标，不能合并为同一快照事实。
4. `stale=true` 表示远端刷新失败后使用已有缓存，事实必须记录其状态和 fetchedAt；不要为了消除提示连续刷新或改查其他项目。

## 源码读取通道硬门禁

1. 所有源码搜索、文件读取、符号定位和调用链调查都必须通过 `aiTroubleShot` MCP 完成。即使宿主本地存在同名仓库或挂载路径，也禁止使用 `rg`、`grep`、`find`、`sed`、`cat`、宿主文件读取工具或其他本地方式访问源码。
2. 代码 MCP 不可用、调用失败且按工具契约无法修正，或返回结果不能支撑代码调查时，停止该代码目标、记录缺口并由当前模式 Core 评估其他已授权证据；不得切换到本地源码兜底。

## 部署版本与证据适用性

显式 ref 解析失败不会回退 defaultRef。固定 commit 只保证读取一致，不证明已经匹配部署；只有部署分支、版本映射缺失、历史时段不一致或缓存陈旧时，明确证据限制，不能将当前分支解释直接等同现场根因。需要切换分析版本时建立新的独立快照并保留旧证据来源。

## 引用与交回当前模式

- managed QA 只引用宿主登记的 `PROJECT_CODE` 材料，使用工具返回的 `materialId`；宿主保留项目、文件/查询范围、commit、fetchedAt 和 stale。personal QA 记录同样的实际来源锚点，不伪造 materialId。
- 多次查询返回不同 commit 时分别记录，不合并为同一版本事实；`stale=true` 或无法匹配用户所用版本时明确限制。调用时间不等于缓存刷新时间。
- QA 按材料回答接口与实现问题；工具不可用时保留已有知识和具体缺口，不用本地源码替代。排障将代码作为解释和验证因果链的证据，不能凭源码可能性宣称本案根因。

托管 QA 在返回前校验完整代码响应；`QA_CODE_RESULT_TOO_LARGE` 表示结果超过引用材料容量，未返回该批正文。此时缩小目录、命中数、上下文或行范围后定向读取，不把未返回内容当作证据。发现敏感内容时保留受限状态，不回显原文。
