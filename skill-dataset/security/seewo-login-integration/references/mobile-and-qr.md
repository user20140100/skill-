# 移动 Web 与 PC 网页扫码

## 1. 移动 Web/H5

| 目标 | 入口 |
| --- | --- |
| 默认移动端登录 | `/m/login` |
| 明确要求账号密码登录 | `/m/pwdLogin` |
| 注册 | `/m/register` |
| 找回密码 | `/m/findpsw` |
| 明确短信登录/注册 | `/m/loginByCode` |

URL 继续携带 `system=${appCode}` 和已编码的 `redirect_url`。第一版不提供小程序 `redirectType` 跳转或原生 App 接入步骤；遇到这两类需求联系刘文祺。若小程序只需业务域名校验 txt，则转读 `configuration-and-release.md`，不得把材料协作误判为完整小程序登录支持。

当前 `/m/login` 是业务方默认入口，具体页面分发由统一登录当前实现和业务配置决定。不要根据历史文档把它固定解释为短信页，也不要让业务自行调用内部短信、注册或密码接口。

## 2. PC 网页扫码登录

标准场景是 PC Web 页面展示二维码，用户使用希沃移动端扫码确认：

- `GET /scan/qrcode`：生成二维码/二维码地址。
- `GET /scan/pcCheckQrcode?type=long`：长轮询扫码状态。
- `qrkey` 默认由 Cookie 关联；跨域 iframe 参照 `iframe-and-ticket.md` 使用 `qrKey=true`。
- 业务需要处理未扫码、已扫码待确认、成功、取消和过期状态。
- 非同主域成功后按 Ticket 方案建立业务会话。

第三方 App 扫码、企业微信或钉钉身份源不是本标准流程。不要把 `thirdCode`、外部票据或特殊项目示例交给普通业务；收集环境、appCode、扫码主体和目标页面后联系刘文祺。

## 3. 验收重点

- 默认移动入口、明确密码、注册和找回入口语义正确。
- system 使用 appCode，回调编码且白名单已配置。
- PC 二维码生成、轮询、确认、取消和过期均有正确状态。
- 跨域不依赖 Cookie，Ticket 只消费一次。
- 页面内部凭证、短信和加密接口不暴露给业务方。
