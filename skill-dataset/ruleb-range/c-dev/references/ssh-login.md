# SSH 登录配置

## 场景说明
为开发容器配置本地 `~/.ssh/config` 并打通登录：免密（下发本地公钥到容器 `/root/.ssh/authorized_keys`）或密码（容器内 `chpasswd` 设置 root 密码）。随后用 `ssh <alias>` 直连。

## 前置条件
- 容器状态为 `running`。
- 免密模式：本地存在 `~/.ssh/id_*.pub`；缺失用 `ssh-keygen -t ed25519` 生成，或 `--pub-key` 指定。

## 命令
- `ai-cli dev ssh setup` — 配置 config + 设密码/下发公钥
- `ai-cli dev ssh exec <alias>` — 直连

## setup 参数
| flag | 说明 |
|------|------|
| `--cluster-id` / `--space-id` / `--container-id` | 必填 |
| `--password` | 切密码模式（交互输入，无回显）；默认免密 |
| `--pub-key` | 覆盖本地公钥文件路径 |

## 流程
1. `GetContainer` 取 `name` / `ssh_port` / `public_ip`（空回退 `node_ip`）。
2. 别名去重：读 `~/.ssh/config` 现有 `Host`，重名则 `name-1` / `name-2` …。
3. 免密：`selectPubKey` 取本地公钥 → `ExecContainerCommand` 执行 `mkdir -p /root/.ssh && echo '<pubkey>' >> /root/.ssh/authorized_keys`。
4. 密码：交互读取 → 执行 `echo 'root:<pw>' | chpasswd`。
5. 追加写 `~/.ssh/config`：`Host <alias>` / `HostName <ip>` / `Port <ssh_port>` / `User root`；打印 `ssh <alias>`。

## exec
`ai-cli dev ssh exec <alias>` 等价 `ssh <alias>`，接管终端。

## 示例
```bash
ai-cli dev ssh setup --cluster-id ctrain --space-id <space> --container-id <id>   # 免密
ai-cli dev ssh setup --cluster-id ctrain --space-id <space> --container-id <id> --password
ssh <container-name>
```

## 常见问题
- 容器非 running：先启动容器再 setup。
- 公钥缺失：`ssh-keygen -t ed25519` 后重试。
- `~/.ssh/config` 不可写：检查权限。
