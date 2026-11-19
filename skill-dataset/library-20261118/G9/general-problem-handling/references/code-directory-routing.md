# Code Source Routing

本文件定义 `get_trouble_categories` 返回的 Git 代码来源如何映射到代码 MCP。分类响应提供：

- `repositoryId`：`aiTroubleShot` MCP 预配置的 Git 仓库标识。
- `defaultRef`：该仓库的默认分支、标签或 commit；调用方没有显式目标版本时使用。
- `appId`：运行时应用标识，只用于日志等运行资产定位，不得当作代码仓库标识。

选择完成后在当前会话中记录唯一的 `effectiveCodeSource`，并将它传给需要代码调查的 Agent。

## 选择规则

1. `personal-local-v1` 与 `managed-agent-v1` 都固定设置 `effectiveCodeSource.mode=aiTroubleShot_mcp`、`effectiveCodeSource.repositoryId=repositoryId` 和 `effectiveCodeSource.requestedRef=defaultRef`。
2. `app_env` 只描述宿主运行环境，不参与代码来源选择。
3. 缺少 `repositoryId/defaultRef` 时，以 `platform_limit` 结束代码调查并指出缺失字段。

禁止根据 MCP 部署环境、问题环境、`app_env`、仓库名外观、分类名或历史记录猜测仓库标识和版本。

## MCP 快照固定规则

1. 第一次调用 `list_code_files`、`search_code_files`、`read_code_file` 或 `get_file_outline` 时，传入当前 `effectiveCodeSource.repositoryId`、`effectiveCodeSource.requestedRef` 和所需的仓库内 `relativePath`。
2. 第一次成功响应后，必须校验并记录返回的 `repositoryId`、`requestedRef`、`resolvedCommit`、`fetchedAt` 和 `stale`。返回仓库与请求不一致、缺少 40 位 `resolvedCommit` 或版本元数据非法时，以 `platform_limit` 结束代码调查。
3. 同一次排查后续所有代码工具调用都把已记录的 `resolvedCommit` 作为 `ref`；不得重新使用分支名，也不得在过程中设置 `refresh=true`。
4. `stale=true` 不等于结果不可用，但事实中必须记录缓存陈旧状态和 `fetchedAt`；只有用户明确要求切换版本或刷新代码时才建立新的代码快照，旧快照证据不得与新快照混为同一版本事实。
5. `relativePath` 始终是仓库内相对路径；不得传绝对路径、`..` 或从本地目录推导的路径。

## 源码读取通道硬门禁

1. 所有源码搜索、文件读取、符号定位和调用链调查都必须通过 `aiTroubleShot` MCP 完成。即使宿主本地存在同名仓库或挂载路径，也禁止使用 `rg`、`grep`、`find`、`sed`、`cat`、宿主文件读取工具或其他本地方式访问源码。
2. 代码 MCP 不可用、调用失败且按工具契约无法修正，或返回结果不能支撑代码调查时，以 `platform_limit` 收口；不得切换到本地源码兜底。
