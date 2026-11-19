# 开放端口

## 场景说明
对外暴露容器内部端口。开放是异步流程：`POST /ports` 立即返回 mapping ID，代理容器随后创建，`status` 由 `init` → `running`（成功）/ `failed`（失败）。

## 命令
- `ai-cli dev port open` — 开放端口
- `ai-cli dev port list` — 查询已开放端口
- `ai-cli dev port close` — 关闭端口

## open 参数
| flag | 说明 |
|------|------|
| `--cluster-id` / `--space-id` / `--container-id` | 必填 |
| `--container-port` | 容器内端口（≥80，必填） |
| `--wait` | 轮询到 running/failed |
| `--interval` | 轮询间隔秒（默认 10） |
| `--timeout` | 超时秒（默认 300，0=无限） |

## 状态流转
`init` → `running`（成功，读取 `node_port` 作为实际开放端口）/ `failed`（失败）→ `removed`。

## 流程
1. `OpenContainerPort` 触发开放，返回 mapping ID。
2. `--wait`：每 `--interval` 秒 `ListContainerPorts(--container-port)` 轮询，最多 `--timeout` 秒。
3. `running` → 打印 `节点端口 <node_port> -> 容器端口 <container_port>`；`failed` → 报错；超时 → 给 mapping ID，提示 `dev port list` 自查。

## list / close 参数
- list：`--container-port`（>0 时按端口过滤）/ `--json`。
- close：`--port-id`（必填，从 list 取）/ `-y --yes`。

## 示例
```bash
ai-cli dev port open --cluster-id ctrain --space-id <space> --container-id <id> --container-port 8000 --wait
ai-cli dev port list --cluster-id ctrain --space-id <space> --container-id <id> --container-port 8000
ai-cli dev port close --cluster-id ctrain --space-id <space> --container-id <id> --port-id <port-id>
```

## 注意事项
- 开放是异步流程；`--wait` 每 10s 轮询、5min 超时；`failed` 表示代理容器创建失败，需检查容器是否 running 与节点端口池；超时可用 `dev port list --container-port` 自查。
