# Apollo 项目配置只读查询与证据（共享）

本文件供 `QA` 与 `TROUBLESHOOTING` 在受控场景共同使用。当用户进行范围明确的 Apollo 配置只读查询，或已支持的问题/排查计划需要核验项目配置、开关或运行参数时，按本文件读取。它不授予配置修改、发布、生产状态变更、完整配置导出或无界数据查询权限。

## 1. 触发与身份

- `QA` 在 `CAPABILITY_DISCOVERY` 的配置查询分支中可直接读取用户明确指定的单一项目、单一 Apollo 环境中的配置键或有限配置项；普通的 `CAPABILITY_DISCOVERY`、`CAPABILITY_INTEGRATION` 和 `SCENARIO_FEASIBILITY` 仅在回答确实需要项目配置证据时读取；`RESPONSIBILITY_ROUTING`、`OUT_OF_SCOPE` 和 `UNKNOWN` 不得读取。
- `TROUBLESHOOTING` 只在调查计划实际建立 Apollo 配置证据目标时读取；不能因为出现项目名、配置关键词或用户要求“把配置发我”就自动读取。
- 只有当前模式可信路由、已加载业务 Skill，或用户明确提供且已与当前项目绑定的资料中存在非空 `apolloAppId`，才允许构造地址。QA 优先使用当前项目路由目录的 `apolloAppId`；排障不得用未绑定的文本补全。
- `apolloAppId` 是 Apollo 配置中心应用编号，必须与鲸云 `ccloudInfo.appId`、运行时日志 `appId`、代码 `repositoryId` 和代码仓库名称分开处理；不得互相替代。`seewo-green` 只是用户给出的具体 appId 示例，不是默认值。
- 构造地址前确认 `apolloAppId` 是单一、非空的 URL 路径段；拒绝 `/`、`\\`、`?`、`#`、控制字符和 `.`/`..` 路径段，也不得把完整 URL 当作 appId 拼接。相同 appId 对应多个项目且无法消歧时停止读取，保留项目不确定性。

## 2. 环境与固定地址

只查询问题明确指向的一个 Apollo 目标环境，不得为了“保险”同时读取测试和正式配置。QA 的 `LOCALIZED|CLOUD` 是业务部署环境标签，不等同于 Apollo 的 `fat|pro` 目标环境，不能互相推断。

| 目标环境 | Apollo 地址模板 |
|---|---|
| 测试环境（fat） | `http://fat.conf.cvte.com/configfiles/json/{apolloAppId}/default/application` |
| 正式环境（pro） | `http://pro.conf.cvte.com/configfiles/json/{apolloAppId}/default/application` |

当 `apolloAppId=seewo-green` 时，使用以下用户提供的具体地址：

- 测试环境：`http://fat.conf.cvte.com/configfiles/json/seewo-green/default/application`
- 正式环境：`http://pro.conf.cvte.com/configfiles/json/seewo-green/default/application`

环境未明确、同时指向两个环境或属于未声明环境时，不得猜测 cluster/namespace；请求补充目标环境，或按当前模式受限收口。固定 `cluster=default`、`namespace=application`，不得自行改写。

## 3. 只读读取与披露

1. 先固定 appId、目标环境、cluster、namespace 和观测时间，再生成唯一地址。
2. 配置查询只能读取用户明确指定的配置键或可由问题直接确定的有限配置项；不得为了寻找答案枚举 cluster、namespace、环境或完整配置。
3. 使用宿主可用的只读 HTTP 客户端（`curl`、`fetch` 或浏览器）执行 GET；禁止 POST、PUT、PATCH、DELETE、写入参数以及要求用户粘贴 Token、Cookie 或 Authorization。示例：`curl -fsS --max-time 20 -- <URL>`。不要把命令输出中的凭据写入日志或直接回显。
4. 校验响应状态和 JSON 可解析性后，返回用户请求的响应内容或具体配置键；除非用户明确要求，不输出无关配置。响应中出现密码、Token、Secret、Authorization、Cookie、私钥或嵌入式凭据时，先脱敏再返回。
5. 记录目标环境、配置键的脱敏值或存在性、环境/namespace 来源锚点和观测时间。密码、Token、Secret、私钥、Authorization、Cookie 等敏感键只记录“已发现并已脱敏”或存在性，禁止回显、复制、持久化、加入 Prompt、交接、日志或最终结果。

## 4. 失败与模式收口

- 缺少或无法确认 appId、目标环境或项目归属：QA 返回 `NEEDS_CONTEXT`，排障归为 `input_insufficient`；不得从 `ccloudInfo.appId`、`repositoryId`、目录名或历史记录补全。
- 没有可用只读 HTTP 客户端、地址不可达、超时、权限失败或响应无法安全解析：QA 在其他依据足够时返回 `DEGRADED`，否则 `FAILED`；排障归为 `platform_limit`。保留其他证据，不切换环境或盲目试探地址。
- 404、空配置或非 2xx 只能作为本次实际观测；只有已有 Apollo/业务规则能解释其含义时，才可判断为配置不存在或根因候选。配置异常不能单独形成 QA 支持结论或排障根因闭环。
