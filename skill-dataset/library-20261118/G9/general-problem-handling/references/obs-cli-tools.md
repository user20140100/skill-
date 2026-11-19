# obs-cli 观测工具

`obs-cli` 是数据库和应用日志的固定只读查询工具，不是可替换 Provider。managed 模式由后端配置注入路径；personal 模式在本机解析路径。实际采集步骤必须使用已验证的绝对路径，不能依赖子 Agent 的 PATH。

> **调用时请使用平台配置中的实际路径**，下文示例统一用 `obs-cli` 代指。

## 路径解析

### managed-agent-v1

- 使用后端 prompt 从 `envConfig.obs.binPath` 注入的绝对路径。
- 主控把已验证的绝对路径和本文件中的准确命令规则直接传给负责该证据目标的 collect Agent，不创建 `agent_stepN.md`。
- 路径未配置时记录工具不可达，不进入个人模式的 PATH 查找或交互安装流程。

### personal-local-v1

按以下优先级只解析一个候选：

1. 用户在本次调用中显式提供的绝对路径，来源记为 `user_input`。
2. 否则使用 `command -v obs-cli` 或宿主等价能力从 PATH 查找，来源记为 `PATH`。
3. 仍未找到时请求用户提供绝对路径；不猜常见目录、不扫描文件系统、不下载安装。

调用业务查询前必须全部通过：

- 规范化后是绝对路径，目标存在、是普通文件且可执行。
- 二进制同目录存在 `obs-cli.json`；只检查存在性，禁止读取、复制或记录其中的 `token`/`ccloud-domain`。
- 执行 `<absolute-path> --help` 成功。若工具提供稳定版本命令，可额外记录版本。

将解析来源、绝对路径、探测结果和限制写入当前 run 的 `issue.md`，不修改全局配置。失败分别记录：

- 未找到：`OBS_CLI_NOT_FOUND`
- 路径或探测无效：`OBS_CLI_INVALID`
- 同目录配置缺失：`OBS_CLI_CONFIG_MISSING`

路径包含空格时必须作为单个可执行参数传递。拒绝包含换行、NUL 或试图改变命令结构的路径/参数；不要把未经校验的用户文本拼成 shell 命令。

## 公共参数

- `-type`：资产类型，`APP`（应用）或 `MYSQL`（数据库）
- `-target`：资产核心信息，应用名/ID 或数据库 DSN
- `-cluster`：集群信息，即问题中的**机构码**（如 `233i`）
- `-time-range`：时间范围，**必传**，ISO8601 格式 `start~end`，如 `'2026-06-10T06:30:00+08:00~2026-06-10T09:30:00+08:00'`

## 查询数据库（只读）

```bash
<verified-absolute-path> db -cluster <机构码> -target mysql.seewo-edge-base:3306/<数据库名> -sql "<只读SQL>" -limit 100
```

- `-cluster`：机构码，从 issue 中获取
- `-target`：固定前缀 `mysql.seewo-edge-base:3306/`，后面拼接具体数据库名
- `-sql`：只读 SQL（不支持写操作）。**SQL 中的表名禁止携带库名前缀**（如 `mofang_local.t_index_app_config`），必须直接写表名（如 `t_index_app_config`）；库由 `-target` 指定，obs-cli 不允许跨库查询
- `-limit`：返回行数上限，默认 100

示例：
```bash
obs-cli db -cluster 233i -target mysql.seewo-edge-base:3306/seewo_class -sql "select * from t_user" -limit 10
```

## 搜索应用日志

```bash
<verified-absolute-path> logs -type APP -cluster <机构码> -target <应用ID> -time-range '<start>~<end>' -query "<条件>" -size 1000
```

- `-cluster`：机构码，从 issue 中获取
- `-target`：目标应用 ID/名称，从 `get_trouble_categories` MCP 返回的 `appId` 或业务 Skill 中获取；`repositoryId` 只标识代码仓库，不得作为日志目标
- `-time-range`：**必传**，ISO8601 格式，带时区，如 `'2026-06-10T06:30:00+08:00~2026-06-10T09:30:00+08:00'`
- `-query`：日志过滤条件，参考 litelog SQL 语法（只包含 WHERE 条件，不含 SELECT），如 `level = 'ERROR'` 或 `message like '%timeout%'`
- `-size`：返回条数，默认 1000

示例：
```bash
obs-cli logs -type APP -cluster 233i -target mofangyun-local -time-range '2026-06-10T06:30:00+08:00~2026-06-10T09:30:00+08:00' -query "message like '%ERROR%'"
```
