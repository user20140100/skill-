# 场景路由

## 1. 先分账号体系

| 业务描述 | 路由 |
| --- | --- |
| 希沃账号登录业务系统 | 云端统一登录，继续判断域名和页面 |
| 公司的员工域账号、工号、内部员工登录 | 4A；不继续生成普通统一登录方案 |
| 用户授权第三方调用开放 API、scope、open_id | 开放平台 OAuth2；access_token 不等于 x-token |
| 学校、教育局、合作方账号登录希沃 | 外部身份源；收集资料并联系刘文祺 |
| 私有部署、AC、一校一套 | 边缘本地化；超出范围 |
| 只说“单点登录”“三方登录” | 询问谁的账号登录哪个系统，不直接映射接口 |

## 2. 再分 Cookie 与 Ticket

| 环境 | 统一登录域名 | 可共享 Cookie 的业务域 |
| --- | --- | --- |
| 测试 | `https://id.test.seewo.com` | `*.test.seewo.com` |
| 生产 | `https://id.seewo.com` | `*.seewo.com` |

- 对应环境同主域：使用 `x-token` httpOnly Cookie，不加 `withticket`。
- 非同主域：使用 Ticket，并加小写 `withticket=true`。
- 不让用户自行判断；根据其测试、生产域名分别判断。

## 3. 最后分页面形态

| 场景 | 标准入口/方案 | 读取资料 |
| --- | --- | --- |
| PC Web 整页 | `/login` | `standard-web.md` |
| PC Web iframe | `/login-iframe` | `iframe-and-ticket.md` |
| 移动 Web/H5 | 默认 `/m/login`；明确密码 `/m/pwdLogin` | `mobile-and-qr.md` |
| PC 网页展示二维码、希沃移动端扫码 | `/scan/qrcode` + `/scan/pcCheckQrcode` | `mobile-and-qr.md` |
| 个人信息副本 | `/m/user/info/download` | `personal-data-export.md` |
| 微信小程序仅需业务域名校验 txt | 收集目标完整域名、配置环境和微信后台原始 txt，转刘文祺 | `configuration-and-release.md` |
| 完整小程序登录或原生 App | 第一版不支持，联系刘文祺 | 不生成登录实现 |

## 4. 可选配置路由

- 港澳手机号登录或预览效果：常规云端接入，读取 `configuration-and-release.md`，先提供测试预览、品牌可定制和先选区号的说明，再指导新版页面配置；不另分认证体系。

- Logo、主题、布局、登录入口开关：`configuration-and-release.md`。
- 登录页或扫码页协议更换：先确认环境，再联系刘文祺授权。
- 微信小程序业务域名校验：读取 `configuration-and-release.md`；这是验证材料协作，不是回调白名单，也不代表完整小程序登录已支持。
- 回调白名单：收集环境、appCode、业务域名、回调地址，联系刘文祺。
- Token 鉴权：转 [usercenter-project-integration](https://skills.gz.cvte.cn/skill/usercenter-project-integration)。
- 账号互斥：第一版不支持，联系刘文祺。
