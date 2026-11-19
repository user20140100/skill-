# 个人信息副本获取

业务方把已登录用户引导至统一登录托管的移动页面，由平台完成身份校验、短信验证、邮箱确认、文件生成、Cstore 上传和邮件投递。业务方不自建导出接口。

## 1. 页面入口

| 环境 | 页面地址 |
| --- | --- |
| 测试 | `https://id.test.seewo.com/m/user/info/download?system=${appCode}` |
| 生产 | `https://id.seewo.com/m/user/info/download?system=${appCode}` |

## 2. 登录态

同主域：直接跳转页面，复用 `x-token` httpOnly Cookie。

跨域：

1. 由业务后端向 `${idBase}/common/userExchangeTicket` 发起 `POST`。
2. 请求携带 `system=${appCode}` 和请求体 `tokenId`；Token 不进入 URL。
3. 获得 60 秒、一次性 Ticket。
4. 跳转 `${idBase}/m/user/info/download?ticket=${ticket}&system=${appCode}`。

未登录、Ticket 无效或过期时进入移动登录，登录后返回下载页按现有稳定能力处理。

## 3. 页面能力和边界

- 展示账号绑定手机号的脱敏值，只向该手机号发送验证码。
- 用户填写短信验证码和接收文件的邮箱。
- 同一 IP 或手机号每天最多 10 次。
- 短信验证码有效期不超过 5 分钟。
- 邮件下载链接有效期为 2 小时。
- 页面内部使用 `/api/v2/user/downloadV2` 及加密流程；业务方不得直调或复制。
- URL、日志和页面不得泄露原始 Token、完整手机号或个人信息文件内容。

## 4. 验收

- 同域 Cookie 和跨域 Ticket 均能进入正确 appCode 主题页面。
- 缺失、篡改、过期或重复消费 Ticket 不建立登录态。
- 无手机号、错误/过期验证码、非法邮箱和重复提交有明确反馈。
- 超过频次限制被拦截。
- 邮件可收到，链接在 2 小时后失效。
