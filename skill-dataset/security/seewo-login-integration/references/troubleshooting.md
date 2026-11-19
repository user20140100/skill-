# 排障

优先判断问题位于业务会话、统一登录页面、回调/白名单、Ticket、Apollo 配置还是 UC。不要在日志中输出 Token、Ticket、密码或完整敏感用户信息。

## 快速定位

| 现象 | 检查 |
| --- | --- |
| 前端读不到 `x-token` | 正常的 httpOnly 行为；改为业务服务端读取，不降低安全属性 |
| 登录后没有回业务页 | `redirect_url` 是否编码、是否命中白名单、appCode 的默认 URL 是否正确 |
| 跨域登录没有登录态 | 是否误用 Cookie；确认小写 `withticket=true`、业务后端换票和自身会话 |
| Ticket 兑换失败 | 是否超过 60 秒、被篡改或已经消费；失败不建会话 |
| iframe 没收到结果 | 检查 `/login-iframe`、回调白名单、`event.origin`、消息 JSON；扫码再查 `qrKey=true` |
| Safari/跨站浏览器异常 | 不回退 `/auth` JSONP 或第三方 Cookie；使用 Ticket |
| 测试正常、生产默认样式 | 检查生产配置是否人工迁移；迁移后等待约 5 分钟 |
| 配置发布后立即看不到变化 | 业务方 Apollo 热更新约需 5 分钟，再刷新验证；无需重启 |
| appCode 不合法或主题不对 | 检查 URL system、配置键、systemCode 是否都为申请的 appCode |
| 个人信息页无手机号 | 当前账号不满足该页面前置条件，联系刘文祺确认处理方式 |
| 要 Token 鉴权接口 | 转 [usercenter-project-integration](https://skills.gz.cvte.cn/skill/usercenter-project-integration) |

## 已知错误契约

- Ticket 兑换成功：`statusCode=200`。
- Ticket 无效：`statusCode=40105`。
- 其他细粒度错误码未冻结，不编造；整理环境、appCode、时间、脱敏请求链路后联系刘文祺。

## 联系刘文祺前准备

- 测试或生产环境。
- appCode。
- 业务域名和已编码前的回调地址。
- 整页、iframe、移动 Web、PC 网页扫码或个人信息副本场景。
- 复现时间、浏览器/终端、预期与实际表现。
- 脱敏状态码、请求路径和必要日志；不包含 Token、Ticket、密码或完整手机号。

