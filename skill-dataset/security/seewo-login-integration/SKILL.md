---
name: seewo-login-integration
description: >-
  希沃统一登录业务方接入，内部区分云端与边缘方案；当前版本提供云端接入，边缘场景仅识别和分流。显式触发：用户提到统一登录、希沃账号登录、公司登录服务、单点登录、appCode、system、x-token、Ticket、登录
  iframe、移动端登录、PC 扫码、港澳手机号登录、微信小程序业务域名校验、登录页或扫码页协议、个人信息副本下载、私有部署、AC
  或一校一套。隐式触发：项目正在自行采集账号密码、前端读取或在 URL 传 Token、跨域依赖 Cookie、复制
  /auth、withTicket、/login-iframe-v2 等历史方案。不负责 4A、开放平台 OAuth2、外部身份源实施、Token
  鉴权接口、完整小程序登录、原生 App 或账号互斥；这些场景只负责分流。
author: liuwenqi
version: 0.1.0
tags:
  - seewo-login
  - seewo-account
  - appcode
  - ticket
  - iframe
  - sso
allowed-tools:
  - Read
  - Bash
  - Write
---

# 希沃统一登录接入

把业务方口语化、信息不完整的登录诉求识别为云端或边缘统一登录场景。当前版本把云端诉求转成可执行、可验证的接入方案，并在代码任务中完成项目检查、实现和验收闭环；边缘场景只完成识别、信息收集和人工分流，为后续在同一 Skill 内扩展边缘接入保留入口。

> **代码接入任务的第一个动作必须读取 [`references/preflight.md`](./references/preflight.md)，先检查调用方项目并输出「Preflight 确认摘要」，之后才能生成或修改代码。普通方案问答、配置咨询和故障排查不受该门禁限制。**

## 权威性与冲突处理

按以下顺序判断登录事实：

1. 统一登录负责人刘文祺当前明确确认的口径。
2. 当前主线代码的完整调用链。
3. 线上配置和实际运行结果；配置以 Apollo 为准。
4. 当前接入流程手册。
5. 知识库文档和历史示例。
6. 仓库本地配置样例。

不能只因路由仍存在就认定它是现行方案。代码校准至少追踪“页面入口 → 当前前端调用 → BFF/控制器 → 下游接口 → Cookie/Ticket 写入或回传”。发生冲突时说明证据并转刘文祺，禁止自行拼接结论。

## 核心规则

- 新业务统一使用申请得到的 appCode：URL 写 `system=<appCode>`，不得复制历史 system 别名。
- 默认使用统一登录托管页面。业务方不采集或保存用户密码，不复刻页面内部 RSA、公钥、注册、重置或登录提交接口。
- 同主域使用 `x-token` httpOnly Cookie：生产共享域为 `.seewo.com`，测试共享域为 `.test.seewo.com`。前端不得读取、持久化、覆盖或放入 URL。
- 非同主域使用 Ticket；参数固定为小写 `withticket=true`，同主域不加。Ticket 60 秒有效且一次性消费，由业务后端立即兑换、建立自身会话并从 URL 清除。
- iframe 父页必须校验 `event.origin` 和消息结构，再把 Ticket 交给后端兑换；不能接受任意来源消息。
- 回调目标可通过 URL 参数指定并正确编码，外部地址须命中当前环境已有域名白名单；已有覆盖无需重复配置，仅新增未覆盖域名联系刘文祺。详见 `references/configuration-and-release.md`，不能绕过校验。
- 业务方 Apollo 配置均热更新，发布后预计约 5 分钟生效，无需重启。
- 不把“代码生成”“编译通过”或“页面可打开”描述为端到端接入完成。

## 工作流

### Phase 1：识别与 Preflight

先判断账号体系，再判断凭证传递，最后判断页面形态：

1. 希沃账号登录业务系统：进入云端统一登录。
2. 公司的员工域账号/工号登录：分流 4A，不套用本 Skill。
3. 第三方经授权调用开放 API：分流开放平台 OAuth2，不把 access_token 当 x-token。
4. 学校、教育局或合作方账号登录希沃：外部身份源，收集信息后联系刘文祺。
5. 私有部署、AC 或一校一套：识别为边缘统一登录。当前版本暂不提供边缘实施步骤，收集环境、部署形态、目标账号体系和业务域名后飞书联系刘文祺。

用户只说“我想接公司的登录服务”时，不假设其理解上述术语。先复述理解，首轮最多问两个普通问题：

1. 希望用户使用“希沃账号”，还是“公司的员工域账号”登录？
2. 系统是网页、移动网页、PC 网页扫码，还是把登录框嵌入已有页面？

用户不确定时，让其提供访问地址和期望操作过程，由 Skill 判断。代码任务继续执行 [`preflight.md`](./references/preflight.md)。

### Phase 2：按场景加载资料

先读 [`scenario-routing.md`](./references/scenario-routing.md) 完成路由，只加载命中场景所需资料：

| 业务目标 | 读取资料 |
| --- | --- |
| Web 整页登录、注册、找回、退出 | [`standard-web.md`](./references/standard-web.md) |
| iframe、跨域 Ticket、postMessage | [`iframe-and-ticket.md`](./references/iframe-and-ticket.md) |
| 移动 Web 或 PC 网页扫码 | [`mobile-and-qr.md`](./references/mobile-and-qr.md) |
| AppCode、页面定制、港澳手机号（新版页面与区号选择）、微信小程序业务域名校验、协议、白名单、生产迁移 | [`configuration-and-release.md`](./references/configuration-and-release.md) |
| 个人信息副本下载 | [`personal-data-export.md`](./references/personal-data-export.md) |
| 历史示例迁移或旧业务排查 | [`historical-compatibility.md`](./references/historical-compatibility.md) |
| 登录失败、回调失败、Cookie/Ticket 异常 | [`troubleshooting.md`](./references/troubleshooting.md) |

适配调用方已有技术栈、BFF/网关、鉴权中间件、会话模型和测试体系，不另建平行架构。

### Phase 3：实现与 Postcheck

代码生成或修改完成后自动读取 [`postcheck.md`](./references/postcheck.md)，执行当前环境允许的静态检查、项目验证、测试联调和生产冒烟，并清楚区分：

- 已实际验证。
- 未执行及其缺失条件。
- 需要业务方完成。
- 需要刘文祺完成。

生产配置修改、发布及真实业务生产变更不在本 Skill 的自动执行范围。

## 第一版不支持的能力

- 边缘统一登录：本 Skill 已负责识别和内部路由，但当前版本只提供云端接入；不得套用云端域名、Cookie、Ticket 或配置步骤，收集最小信息后飞书联系刘文祺。
- Token 鉴权接口：引导业务方前往 [CVTE Skill 中心的 usercenter-project-integration](https://skills.gz.cvte.cn/skill/usercenter-project-integration) 使用 UC Skill 咨询，不复制或猜测 UC 接口。
- 完整小程序登录、原生 App、账号互斥：说明第一版边界，收集环境、appCode、业务域名和目标流程后飞书联系刘文祺。微信小程序业务域名校验材料指导是例外，按 `configuration-and-release.md` 处理，但不得延伸为完整小程序登录实施。
- 外部身份源、特殊第三方扫码、跨应用退出影响：收集最小信息后联系刘文祺，不生成未经确认的步骤。

## 输出要求

信息不足时只输出：需求理解、最多两个问题、带条件的初步推荐。方案确定后按需提供：

1. 场景判断与依据。
2. Preflight 已知信息和未决项。
3. 推荐方案及不应采用的历史方案。
4. AppCode、测试配置、业务开发、生产迁移步骤。
5. 前端、后端、统一登录/UC 各自责任。
6. 可复制的 URL 模板、参数或项目代码。
7. 已执行的 Postcheck 与真实结果。
8. 未验证项、补测方式和人工协作清单。

人工协作清单至少包含：目标环境、appCode、业务域名、回调地址、页面形态、期望能力和计划验证时间。

## 禁止事项

- 禁止编造 appCode、环境域名、白名单、Apollo 值、权限或测试结果。
- 禁止指导业务方直调账号密码、注册、重置密码等托管页面内部接口。
- 禁止把 Token 放入 URL，或在日志、埋点、Referer、localStorage 中记录 Token、Ticket、用户密码；Ticket 只允许按标准回调短暂出现并应立即兑换、清除。
- 禁止跨域继续依赖第三方 Cookie，或用 `/auth` JSONP 作为新接入默认方案。
- 禁止新业务使用 `withTicket`、`/login-iframe-v2` 或历史 system 别名。
- 禁止把 Ticket 描述为可重复使用；它是 60 秒、一次性消费凭证。
- 禁止为第一版排除能力生成看似可执行的实施步骤。
