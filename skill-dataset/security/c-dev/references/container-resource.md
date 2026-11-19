# 容器资源查询

## 场景说明
查询开发容器的列表与详情：规格（CPU/内存/shm）、节点 IP、SSH 端口、镜像、Git、磁盘占用。只读，不触碰容器生命周期。

## 命令
- `ai-cli dev container list` — 列表（支持过滤）
- `ai-cli dev container get` — 详情（需 `--container-id`）

## list 参数

| flag | 说明 |
|------|------|
| `--cluster-id` / `--space-id` | 必填，集群/空间 |
| `--status` | 按状态过滤（如 running） |
| `--name` | 容器名模糊匹配 |
| `--node-ip` | 节点 IP 模糊匹配 |
| `--username` | 按用户名过滤 |
| `--mode` | all / my |
| `--page` / `--page-size` | 分页（默认 1 / 20） |
| `--json` | 输出完整 JSON |

## get 参数
`--cluster-id` / `--space-id` / `--container-id`（必填）/ `--json`。

## Container 字段（--json 输出）
| json tag | 说明 |
|----------|------|
| `id` | 容器 ID |
| `name` | 容器名（SSH 别名来源） |
| `image` | 镜像 |
| `node_ip` | 节点 IP（public_ip 空时回退为 SSH HostName） |
| `public_ip` | 公网 IP（优先 HostName） |
| `ssh_port` | SSH 端口 |
| `status` | 容器状态 |
| `resource` | `{memory, cpu, is_vgpu, shm_size}` |
| `size` | `{size, total_size, size_time}`，字节 |
| `git_url` / `git_branch` | 代码仓库 |
| `created_by` / `created_at` | 创建信息 |

## 示例
```bash
ai-cli dev container list --cluster-id ctrain --space-id <space> --status running
ai-cli dev container get --cluster-id ctrain --space-id <space> --container-id <id> --json
```
