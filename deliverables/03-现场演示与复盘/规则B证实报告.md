# 规则 B 证实报告：tier1 对明文凭证的漏报与规则 B 的补盲

> 课题：AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统
> 作者：杨宇涵 ｜ 日期：2026-11-18

## 一、结论先行

tier1 内置规则（SkillSpector 71 条）覆盖「凭证文件访问」「恶意签名」「后门持久化」等，但**没有**「明文凭证内嵌命令行 / 连接串」这一类确定性规则。

因此当 skill 把关键凭证从**占位符 / 环境变量**改成**字面明文**时，不挂规则 B 的 tier1 会整行漏报；挂上规则 B 后立即命中。实验用 c-dev 的恶意化改造验证——仅把 `references/ssh-login.md` 第 25 行的占位符 `<pw>` 替换为明文 `CVTE@2026`，其余内容不变。

| 样本 | 第 25 行内容 | 是否触发规则 B |
|---|---|---|
| c-dev 原文 | `echo 'root:<pw>' \| chpasswd`（占位符） | 否（正确不误报） |
| c-dev 恶意化 | `echo 'root:CVTE@2026' \| chpasswd`（明文） | 是（正确命中） |

---

## 二、不添加规则 B（仅内置 tier1）

### 2.1 写死密码片段 —— 未被发现

c-dev 原文中不存在写死密码（原文是占位符 `<pw>`，见 `references/ssh-login.md:25`）。写死密码出现在恶意化版本 c-dev-malicious 的同一行：

```
4. 密码：交互读取 → 执行 `echo 'root:CVTE@2026' | chpasswd`。
```

**该行明文凭证被 tier1 完全漏掉（0 命中）——这正是规则 B 要补的盲区。**

### 2.2 内置规则实际找出的 findings（红色标记命中片段）

tier1 只报出 4 条，且**没有一条落在第 25 行的明文密码上**：

| # | 规则 | 位置 | 命中片段（红） | 类别 / 严重度 |
|---|---|---|---|---|
| 1 | PE3 | SKILL.md:68 | **`~/.ssh/id_ed25519`** | 凭证访问 / HIGH |
| 2 | PE3 | ssh-login.md:4 | **`/root/.ssh/authorized_keys`** | 凭证访问 / HIGH |
| 3 | PE3 | ssh-login.md:24 | **`/root/.ssh/authorized_keys`** | 凭证访问 / HIGH |
| 4 | YR1(backdoor_persistence) | ssh-login.md:24 | **`echo '<pubkey>' >> /root/.ssh/authorized_keys`** | 后门持久化 / HIGH |

### 2.3 tier1 结果（不添加规则 B）

| 指标 | 值 |
|---|---|
| risk_score | 58 |
| severity | HIGH |
| recommendation | DO_NOT_INSTALL |
| findings 总数 | 4 |
| 明文凭证命中 | **0（漏报）** |

---

## 三、添加规则 B

### 3.1 写死密码片段 —— 命中

同一行的明文凭证被规则 B（`cvte_credential_chpasswd`）命中：

**`echo 'root:CVTE@2026' | chpasswd`**

### 3.2 全部 findings（红色标记命中片段）

| # | 规则 | 位置 | 命中片段（红） | 类别 / 严重度 |
|---|---|---|---|---|
| 1 | PE3 | SKILL.md:68 | **`~/.ssh/id_ed25519`** | 凭证访问 / HIGH |
| 2 | PE3 | ssh-login.md:4 | **`/root/.ssh/authorized_keys`** | 凭证访问 / HIGH |
| 3 | PE3 | ssh-login.md:24 | **`/root/.ssh/authorized_keys`** | 凭证访问 / HIGH |
| 4 | YR1(backdoor_persistence) | ssh-login.md:24 | **`echo '<pubkey>' >> /root/.ssh/authorized_keys`** | 后门持久化 / HIGH |
| 5 | **YR1(cvte_credential_chpasswd)** | ssh-login.md:25 | **`echo 'root:CVTE@2026' \| chpasswd`** | **明文凭证 / HIGH** |

### 3.3 tier1 结果（添加规则 B）

| 指标 | 值 |
|---|---|
| risk_score | 69（↑11） |
| severity | HIGH |
| recommendation | DO_NOT_INSTALL |
| findings 总数 | 5（+1） |
| 明文凭证命中 | **1（cvte_credential_chpasswd）** |

---

## 四、为什么 tier1 会漏掉明文凭证

内置 71 条规则主要覆盖：prompt 注入、数据外泄、提权、供应链、过度授权、恶意签名（YARA）、MCP 投毒等。其中与凭证相关的只有两类：

- **PE3（凭证文件访问）**：命中 `~/.ssh/id_ed25519`、`authorized_keys` 这类**文件路径**；
- **YR1 恶意签名**：命中「写公钥进 authorized_keys」这类**持久化行为**。

**没有任何一条**针对「`user:pass` 明文内嵌在命令行 / 连接串」这种写法。因此当关键变量是**非占位符、非环境变量**（即字面明文密码）时，tier1 不会对「密码本身」做安全审查——这正是规则 B 的设计意义：补齐「明文凭证内嵌」这一确定性检测盲区，让 `chpasswd`、`curl -u`、`mysql -p`、`redis-cli -a`、`mongosh --password`、URL userinfo 六类载体在静态阶段即可被拦截。
