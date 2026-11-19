# 排查 CLI 按需安装与认证

规则来源：飞书《问题排查-README》：https://cvte.feishu.cn/wiki/Q51ewQuQliZ7tMkJ84pcbgdYnxf 。该文档是维护入口；安装命令变化时以当前原文和各 CLI 自带 `--help` 为准。

## 按需检查原则

不要在每次进入 skill 时同时检查两个 CLI。只有当前证据路径需要某个 CLI 时，才在首次调用前检查对应命令：

```bash
command -v <本次需要的CLI>
```

缺少时安装，再重新执行 `command -v` 和版本/帮助验证。命令存在时直接执行本次所需的第一个真实只读查询，由该查询同时验证认证和资源权限；不要额外运行无关业务探针。同一任务内真实查询成功后不重复检查。不要在每次排查时运行升级检查；只有命令缺失、客户端明确不支持所需能力，或用户要求升级时才处理版本。

## seewo-mgr

缺失时在 macOS/Linux 安装：

```bash
curl -sSL https://mom.seewo.com/cli/install | bash
```

安装脚本可能把二进制放到 `~/.local/bin` 并修改 shell 配置。当前进程找不到新命令时，刷新 PATH 或启动新的登录 shell，然后验证：

```bash
seewo-mgr --version
seewo-mgr auth status
```

优先直接执行本次所需的真实只读查询。查询提示未登录、token 失效/401 时，可用 `seewo-mgr auth status` 辅助确认，并需要用户提供自己的域账号，然后由 Agent 执行：

```bash
seewo-mgr auth login -u <用户域账号>
```

该命令会打开或输出确认页面；让用户在浏览器确认，登录成功后只重试原来的真实查询一次。不要回显完整 API Key。`auth status` 显示用户、脱敏 Key 和 SavedAt 只能证明本机存有凭据，不能代替真实调用。

## ccloud-cli

缺失时先确认 Node.js `>=19` 和 npm 可用，再安装：

```bash
npm install -g @cvte/ccloud-cli --@cvte:registry=https://artifactory.gz.cvte.cn/artifactory/api/npm/npm-local/
```

验证：

```bash
ccloud-cli --version
ccloud-cli --help
```

当前 CLI 没有 `auth status` 子命令，不能调用一个不存在的状态命令。直接用本次排查所需的第一个只读查询验证登录，不用固定应用名另跑探针。返回 `[AUTH_REQUIRED]` 或等价认证错误时，由 Agent 执行浏览器登录：

```bash
ccloud-cli auth login
```

让用户完成浏览器授权，再重试原来的真实只读查询一次。无浏览器环境且用户主动提供 API Key 时才使用 `ccloud-cli auth login --key <key>`；不要要求用户把 Key 写入 skill 或排查报告。登录成功但查不到目标可能是资源权限问题，不应反复登录；按返回结果提示联系对应应用负责人授权。

## 不可用时的处理

安装失败、浏览器授权未完成或重试后凭据仍失效时，明确指出卡在哪一步，仅暂停依赖该 CLI 的取证分支。继续知识检索和不依赖该 CLI 的分析，并说明哪些现场结论尚未验证；不要编造日志、数据库或审计结果。
