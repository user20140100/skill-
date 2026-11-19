# API 参考

> openapi 前缀 `/clusters/{cluster_id}/spaces/{space_id}/train/containers`；信封 `{status,msg,data}`，`status=0` 成功。

## 容器
| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/clusters/{cluster_id}/spaces/{space_id}/train/containers` | 列表（query: status/state/name/node_ip/username/mode/page/page_size） |
| GET | `/clusters/{cluster_id}/spaces/{space_id}/train/containers/{id}` | 详情，data=Container |

## 命令执行
| 方法 | 路径 | 请求 | 响应 |
|------|------|------|------|
| POST | `/clusters/{cluster_id}/spaces/{space_id}/train/containers/{id}/command` | `{"input":"<cmd>"}` | `data={"output":"..."}` |

## 端口
| 方法 | 路径 | 请求 | 响应 |
|------|------|------|------|
| GET | `/clusters/{cluster_id}/spaces/{space_id}/train/containers/{id}/ports` | query: `container_port` | `data={total,result:[PortMapping]}` |
| POST | `/clusters/{cluster_id}/spaces/{space_id}/train/containers/{id}/ports` | `{"container_port":N}`（N≥80） | `data=<mapping_id>` |
| DELETE | `/clusters/{cluster_id}/spaces/{space_id}/train/containers/{id}/ports/{port_id}` | — | `data=null` |

## 状态常量
端口代理：`init` / `running` / `failed` / `removed`。容器：`running`（操作前置条件）。
