---
name: c-dev
version: 1.0.1
description: >-
  AI 开发平台开发环境 skill：开发容器资源查看、SSH 密码/免密登录配置、开放容器端口。 在用户查看开发环境容器资源、配置 SSH
  登录或开放容器端口时使用。
tags:
  - AI 平台
author: liuguibin
---

# AI平台开发环境管理(c-dev)

## 调用方式

开发环境操作统一通过 `ai-cli dev` 命令完成（`ai-cli` 是 AI 开发平台的命令行工具）。

认证与上下文通过 flag 显式传入：

```
ai-cli dev <子命令> \
  --token <X-AI-Token>      # 认证 Token
  --cluster-id <cluster_id>   # 集群 ID
  --space-id <space_id>       # 空间 ID
  --container-id <container_id>       # 容器 ID（涉及容器资源的命令必填）
```

### 必要参数的读取
`token` / `cluster_id` / `space_id` / `container_id` 按以下方式顺序读取：
1. 从配置文件 `.ai.json` 读取，通过 `--xx` flag 显式传入。
2. 若1不存在，则从环境变量中读取，`ai-cli dev` 会自动读取，无须手动传入。
```bash
# 环境变量名：
AI_TOKEN=认证Token
AI_CLUSTER_ID=集群ID
AI_SPACE_ID=空间ID
AI_CONTAINER_ID=容器ID
```
3. 若1/2都不存在，获取与保存方式见 `c-ai` skill，本 skill 不实现。

### 调用说明
- `references/` 文档中的操作流程均以 `ai-cli dev` 命令给出，必要参数根据上面的读取，文档中故省略这几个参数。
- API 地址默认采用 SDK 内置地址，一般无需设置；如需覆盖用 `--url` 或环境变量 `AI_URL`。
- 遇 403/404 时，可以调用 `c-ai` skill 检查集群/空间/容器的权限。

## 能力范围

- 开发容器资源查看（列表、详情）
- SSH 密码 / 免密登录（写 `~/.ssh/config` + 容器内设密码 / 下发公钥）
- 开放端口（开放、列表、关闭；开放后轮询到 running/failed）

## 触发条件

当用户问题涉及以下场景或关键词时，使用本 skill：

- 查看开发容器（容器列表、详情、规格、SSH 端口、节点 IP）
- 配置/设置容器密码 
- 配置 SSH 登录（免密公钥下发、设置 root 密码、写 `~/.ssh/config`）
- 开放 / 关闭容器端口、查询已开放端口
- 关键词：「开发环境」「容器」「SSH」「免密」「登录」「开放端口」「端口转发」「node_port」

## 执行前检查

1. ai-cli 版本(ai-cli -v) >= 0.1.0 
  - 若无安装，先进行ai-cli安装
  - 版本过低，先进行ai-cli升级
2. 设密码 / 下发公钥 / 开放端口前，容器需为 `running` 状态，否则提示先启动容器。
3. `dev ssh setup` 默认免密模式：自动读取本地 `~/.ssh/id_ed25519.pub` → `id_rsa.pub` → 首个 `*.pub`；缺失则提示 `ssh-keygen -t ed25519` 生成。
4. 开放端口是异步流程：`--wait` 时每 10s 轮询、最多 5min，到 `running` 打印实际 `node_port`，`failed` 提示排查。

## 安全提示

- .ai.json 包含 token，必须加入 .gitignore
- 若当前仓库根 `.gitignore` 尚未覆盖该文件，首次生成时请追加
- 终端输出中不暴露完整 token

## 参考资料

按需加载 `references/` 下的文档，不在初始上下文中载入：

| 文件 | 何时读取 |
|------|----------|
| `references/container-resource.md` | 查询容器列表 / 详情时 |
| `references/ssh-login.md` | 配置 SSH 免密 / 密码登录、`~/.ssh/config` 写入时 |
| `references/port-forward.md` | 开放 / 列表 / 关闭端口时 |
| `references/api-reference.md` | 需要查阅完整 API 接口定义时 |

## 脚本

开发环境操作通过 `ai-cli dev ...` 完成（命令树见各 `references/` 文档）；`scripts/` 目录当前为占位，无额外辅助脚本。
