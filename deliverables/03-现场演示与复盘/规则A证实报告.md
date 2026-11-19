# 规则 A 证实报告：tier1 对白名单域名外发的误报与规则 A 的降噪

> 课题：AI Agent 技能（Agent Skills）全链路安全审计与效果评估系统
> 作者：杨宇涵 ｜ 日期：2026-11-18

## 一、结论先行

tier1 内置规则 **E1「External Transmission」** 对「带数据上传的外部请求」一律报 MEDIUM，**无法区分**「发往企业可信域名的合法外发（日志采集 / telemetry / 镜像源上传）」与「发往恶意 C2 的外泄」。

因此当 skill 向 `*.cvte.com` / `*.gz.cvte.cn` 这类**白名单域名**上传时，不挂规则 A 的 tier1 会持续误报；挂上规则 A 后，这些 finding 从 `kept` 移到 `suppressed`（降误报），**不新增任何 finding**。

> 与规则 B 方向相反：规则 B = **新增** HIGH finding（补盲）；规则 A = **抑制**误报 finding（降噪）。两者严格正交。

| 样本 skill | 目标域名 | 命中白名单模式 | 不添加规则 A | 添加规则 A |
|---|---|---|---|---|
| custom-rules-whitelist | `api.cvte.com` | `*.cvte.com`（单级子域） | E1 误报 | 抑制放行 |
| custom-rules-whitelist | `a.b.cvte.com` | `*.cvte.com`（多级子域） | E1 误报 | 抑制放行 |
| custom-rules-whitelist | `upload.gz.cvte.cn` | `*.gz.cvte.cn`（第二条通配） | E1 误报 | 抑制放行 |
| custom-rules-range | `evil-c2.example.com` | 非白名单 | E1 保留 | **E1 保留（不放行）** |
| custom-rules-range | `cvte.com` | 裸域名（`*.` 只匹配子域） | E1 保留 | **E1 保留（不放行）** |
| custom-rules-range | `cvte.com.evil.com` | 陷阱后缀 | E1 保留 | **E1 保留（不放行）** |

---

## 二、不添加规则 A（仅内置 tier1）

### 2.1 白名单域名外发片段 —— 被误报

`custom-rules-whitelist/SKILL.md:29-32` 的 4 条 http 上传，目标域名全部落在企业白名单内，但内置 E1 仍将其当作「外部传输」报警：

```bash
curl -d '{"env":"demo"}' https://api.cvte.com/v1/telemetry
curl -d '{"env":"demo"}' https://a.b.cvte.com/v1/telemetry
curl -d '{"env":"demo"}' https://upload.gz.cvte.cn/collect
wget --post-data="env=demo" https://upload.gz.cvte.cn/collect
```

**这 4 条合法内网上传被 E1 全部当作「外部传输」误报——规则 A 要降的正是这些噪声。**

### 2.2 内置规则实际找出的 findings（红色标记命中片段）

| # | 规则 | 位置 | 命中片段（红） | 类别 / 严重度 |
|---|---|---|---|---|
| 1 | E1 | SKILL.md:29 | **`curl -d … https://api.cvte.com/v1/telemetry`**（含 a.b.cvte.com / upload.gz.cvte.cn） | 外部传输 / MEDIUM |
| 2 | E1 | SKILL.md:29 | **`https://api.cvte.com/`** | 外部传输 / MEDIUM |
| 3 | E1 | SKILL.md:32 | **`wget --post-data=… https://upload.gz.cvte.cn/collect`** | 外部传输 / MEDIUM |

### 2.3 tier1 结果（不添加规则 A）

| 指标 | 值 |
|---|---|
| risk_score | 10 |
| severity | LOW |
| recommendation | SAFE |
| findings 总数 | 3 |
| E1 外发命中 | **3（白名单域名误报）** |
| suppressed | 0 |

---

## 三、添加规则 A

### 3.1 白名单域名外发片段 —— 被抑制放行

同一批上传经 `allow_domain`（`*.cvte.com` / `*.gz.cvte.cn`）匹配后，从 `kept` 移入 `suppressed`，不再计入评分：

**`https://api.cvte.com/v1/telemetry` → 命中 `*.cvte.com` → 放行**
**`https://a.b.cvte.com/v1/telemetry` → 命中 `*.cvte.com` → 放行**
**`https://upload.gz.cvte.cn/collect` → 命中 `*.gz.cvte.cn` → 放行**

### 3.2 被抑制的 findings（红色标记，附审计留痕）

| # | 规则 | 位置 | 被抑制片段（红） | 抑制原因 |
|---|---|---|---|---|
| 1 | E1 | SKILL.md:29 | **`curl -d … https://api.cvte.com/v1/telemetry`** | 规则 A：发往企业白名单域名放行 |
| 2 | E1 | SKILL.md:29 | **`https://api.cvte.com/`** | 同上 |
| 3 | E1 | SKILL.md:32 | **`wget --post-data=… upload.gz.cvte.cn/collect`** | 同上 |

### 3.3 tier1 结果（添加规则 A）

| 指标 | 值 |
|---|---|
| risk_score | 0（↓10） |
| severity | LOW |
| recommendation | SAFE |
| findings 总数 | 0 |
| E1 外发命中 | **0（3 条全部抑制放行）** |
| suppressed | 3 |

---

## 四、边界验证：非白名单 / 陷阱域名不放行

规则 A 的 `*.` 只匹配子域名，对非白名单、裸域名、陷阱后缀**一律不放行**。`custom-rules-range` 的三类保留侧样本（添加规则 A 后）仍保留 `kept`：

| 目标域名 | 判定 | 结果 |
|---|---|---|
| `evil-c2.example.com` | 非白名单 | 保留 kept（不放行） |
| `cvte.com` | 裸域名，`*.cvte.com` 要求 `host != 后缀` | 保留 kept（不放行） |
| `cvte.com.evil.com` | 后缀是 `evil.com` 而非 `cvte.com` | 保留 kept（不放行） |

| 指标 | 不添加规则 A | 添加规则 A |
|---|---|---|
| risk_score | 20 | 20（不变） |
| findings 总数 | 5 | 5（不变） |
| suppressed | 0 | **0（非白名单不放行）** |

---

## 五、为什么 tier1 需要白名单放行降误报

内置 E1「External Transmission」只有「带数据上传的请求」一个维度，无法感知目标域名的**信任关系**：企业内大量合法场景（日志采集、telemetry 回传、镜像源 / 制品上传）都指向 `*.cvte.com` / `*.gz.cvte.cn`，这些请求会被 E1 一视同仁地报 MEDIUM，从而**淹没真实的恶意外发告警**。

规则 A 在**抑制层**补上「域名」这一维度：把「发往白名单域名」的外发 finding 从 `kept` 移到 `suppressed`（保留 `reason` 审计留痕，不计分），对非白名单 / 裸域名 / 陷阱后缀一律不放行——体现「**检测归检测、放行归放行**」：检测能力完全由内置 E1 承担，规则 A 自身不新增任何 finding，与规则 B 严格正交。
