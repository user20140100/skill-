# 标准 Web 托管页面

## 1. 环境基础地址

| 环境 | 基础地址 |
| --- | --- |
| 测试 | `https://id.test.seewo.com` |
| 生产 | `https://id.seewo.com` |

以下模板中的 `${idBase}` 按环境替换，`${appCode}` 使用已申请的真实 appCode。

## 2. PC 整页入口

```text
${idBase}/login?system=${appCode}&actionType=login&redirect_url=${encodedRedirectUrl}
```

参数：

- `system`：新业务固定使用 appCode。
- `actionType`：`login`、`register`、`findpsw`。
- `redirect_url`：通过 URL 指定本次目标，使用 `encodeURIComponent` 等价方式编码；通过校验后优先于默认回调。目标域名已被当前环境白名单覆盖即可使用，无需逐条登记完整 URL；仅未覆盖域名需新增配置。
- `withticket=true`：仅非同主域加入，参数名必须小写。

同主域登录成功后由统一登录写入 `x-token` httpOnly Cookie，业务服务端读取。业务若需要实现 Token 鉴权，转 [UC Skill](https://skills.gz.cvte.cn/skill/usercenter-project-integration)，本 Skill 不提供接口细节。

非同主域登录成功后，统一登录把 Ticket 追加到回调地址。业务后端应立即使用 `GET ${idBase}/api/v2/cas/exchangeToken?ticket=...` 兑换，成功后建立自己的安全会话并清除浏览器 URL 中 Ticket。

Ticket 契约：

- 60 秒有效。
- 一次性消费。
- 成功：`statusCode=200` 并返回 Token。
- 无效：`statusCode=40105`。
- 其他细粒度错误码未冻结，不得编造。

## 3. 托管页面边界

业务方只使用页面入口，不调用页面内部接口。PC 账号密码当前由统一登录页面使用 V3 链路提交 `/login/v3`，认证下游走 API4，公钥材料仍走原链路；这些是平台内部实现，不应复制到业务项目。

注册、找回密码和弱密码重置同样只暴露托管页面能力。业务方不得自行采集密码、复刻加密或直调内部注册/重置接口。

## 4. 退出并回跳

```text
${idBase}/logoutToRedirect?redirect_url=${encodedRedirectUrl}
```

业务方同时清理自身应用会话。该入口支持基础退出和回跳，但跨应用、联登父子 Token 或特殊会话的影响范围未冻结；用户追问“是否退出所有业务”时联系刘文祺，不能承诺全部退出或互不影响。

## 5. 最小实现责任

业务前端：

- 发起页面跳转，不读取 x-token。
- 正确编码回调，不把 Token 放入 URL。

业务后端：

- 同域从请求 Cookie 读取登录态；具体 UC 鉴权转 UC Skill。
- 跨域只接收短时 Ticket，立即兑换并建立自身会话。
- 登录回调防开放重定向，退出时清理自身会话。

统一登录/刘文祺：

- AppCode 对应配置、回调白名单和需要人工完成的环境配置。

