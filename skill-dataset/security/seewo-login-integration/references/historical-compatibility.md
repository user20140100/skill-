# 历史兼容与迁移

本文件只用于识别和迁移存量实现。除非用户明确在排查旧业务，不把以下内容加入新接入方案。

| 历史内容 | 现行处理 |
| --- | --- |
| `system` 使用历史别名 | 新业务统一 `system=appCode`；存量先核对 Apollo 映射，不盲改 |
| `withTicket` 大写 T | 新业务使用小写 `withticket=true` |
| `/login-iframe-v2` | 新业务统一 `/login-iframe`，页面版本由配置决定 |
| `/m/login?loginType=HK` | 港澳临时过渡入口；新接入按 `configuration-and-release.md` 选择新版页面及区号，沿用常规接入流程 |
| `/auth` JSONP/CORS 跨域鉴权 | 仅存量排障；新业务跨域使用 Ticket |
| 跨站依赖 Cookie 或 `x-samesite-none-token` | 浏览器策略不可靠；新业务改 Ticket |
| 业务直调 `/login`、`/login/v2` POST | 页面内部旧路由；新业务只使用托管页面 |
| 把 PC 登录描述为旧链路 | 当前页面账号密码为 V3，认证下游 API4；业务不复刻内部链路 |
| `/m/login` 固定等同短信登录 | 当前默认入口由分发逻辑和配置决定；明确短信才用 `/m/loginByCode` |
| 小程序 `redirectType` 示例 | 第一版不支持完整小程序登录，联系刘文祺；仅业务域名校验 txt 可按 `configuration-and-release.md` 协作 |
| Ticket 可重复使用 | 现行契约为 60 秒且一次性消费 |
| 个人信息链接 72 小时或 7 天 | 现行负责人口径为 2 小时 |
| Apollo 修改后需要重启 | 业务方配置热更新，预计约 5 分钟生效 |

迁移前先确认存量业务是否依赖历史行为、环境配置和回调链路。未经联调不要机械替换参数或入口。
