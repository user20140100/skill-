---
name: custom-rules-whitelist
description: >-
  【安全靶场·放行对照】验证规则 A（抑制层域名白名单 allow_domain）对「命中检测层后应放行」的
  白名单域名外发进行抑制。样本全部为 http 上传方向（curl 上传 / wget 上传，命中内置 E1
  外部传输），目标域名均落在企业白名单（*.cvte.com / *.gz.cvte.cn），覆盖单级/多级子域名与
  第二条通配模式，均应被 allow_domain 抑制、不计入 kept。仅供离线安全扫描验证，请勿安装或执行。
author: 杨宇涵
tags: [security-range, rule-a, whitelist, suppression-control]
version: 0.3.0
---

# 规则 A 白名单放行对照靶场（请勿执行）

> 本 Skill 验证规则 A 的**放行侧**：向企业白名单域名的 **http 上传**命中内置 E1「外部传输」
> 检测后，应被抑制层 `allow_domain` 统一放行 —— 不进 `kept`、不计入风险评分。
> 与 `custom-rules-range` 的区别：range 里是**非白名单/陷阱域名**（应保留 kept），
> 这里是**白名单域名**（应放行 suppressed）。

## 覆盖的域名边界（均应命中白名单、应放行）

| 样本 | 目标域名 | 命中模式 |
|------|----------|----------|
| 单级子域名 | `api.cvte.com` | `*.cvte.com` |
| 多级子域名 | `a.b.cvte.com` | `*.cvte.com` |
| 第二条通配 | `upload.gz.cvte.cn` | `*.gz.cvte.cn` |

```bash
curl -d '{"env":"demo"}' https://api.cvte.com/v1/telemetry
curl -d '{"env":"demo"}' https://a.b.cvte.com/v1/telemetry
curl -d '{"env":"demo"}' https://upload.gz.cvte.cn/collect
wget --post-data="env=demo" https://upload.gz.cvte.cn/collect
```

## 说明

- 以上 4 条均为 **http 上传方向**（curl 上传 / wget 上传），命中内置 E1 检测层后，
  再由规则 A 白名单抑制，是「检测归检测、放行归放行」的正向对照；
- 非白名单/陷阱域名的**保留侧对照**见 `custom-rules-range/`（`cvte.com` 裸域名、
  `cvte.com.evil.com` 陷阱后缀、`evil-c2.example.com` 非白名单，均应保留 kept）。
