# iframe 与 Ticket

## 1. 标准入口

新业务统一使用：

```text
${idBase}/login-iframe?system=${appCode}&actionType=login&redirect_url=${encodedRedirectUrl}&callbackIframeUrl=${encodedCallbackUrl}
```

- 页面版本由 `systems[appCode]` 配置决定，不让业务方选择实现版本。
- `/login-iframe-v2` 是历史兼容入口，不向新业务推荐。
- `callbackIframeUrl` 是登录成功后的中继回调，可在 URL 上直接传入并编码；外部地址须命中已有域名白名单，仅未覆盖的域名需要新增配置。
- `redirect_url` 是业务返回目标，不能与中继回调混为一谈；父页面收到结果并建立会话后自行控制刷新或跳转。参数与默认配置的关系见 [回调地址与域名白名单](./configuration-and-release.md#4-回调地址与域名白名单)。

## 2. 同主域 iframe

- 使用 `x-token` 主域 httpOnly Cookie。
- 不加 `withticket`。
- 中继回调通知父页关闭登录框、刷新或进入业务页面。
- 父页面和回调页面仍应限制可信 origin。

## 3. 非同主域 iframe

入口增加：

```text
withticket=true&qrKey=true
```

- `withticket` 必须小写。
- `qrKey=true` 用于跨站 iframe 扫码时由页面持有并传递二维码 key。
- 登录成功后统一登录通过 `postMessage` 返回 JSON 字符串 `{"ticket":"..."}`。
- 父页验证 `event.origin` 必须等于当前环境统一登录 origin，并校验消息结构。
- Ticket 只交给业务后端兑换，前端不得持久化或重复消费。
- 后端使用 `/api/v2/cas/exchangeToken` 立即兑换，建立自身会话后从 URL/状态中移除 Ticket。

示意代码需按业务框架改写：

```javascript
window.addEventListener('message', event => {
  if (event.origin !== expectedIdOrigin) return;
  let message;
  try {
    message = JSON.parse(event.data);
  } catch (_) {
    return;
  }
  if (!message || typeof message.ticket !== 'string' || !message.ticket) return;
  // 仅提交给业务后端一次；后端完成换票并建立业务会话。
});
```

禁止使用 `event.origin` 未校验的旧示例，禁止接受 `*` 来源，禁止在日志或埋点中记录 Ticket。

## 4. Ticket 不变量

- 60 秒有效、一次性消费。
- 篡改、过期、重复消费不得建立业务会话。
- 业务端也应通过回调 nonce/state、幂等标记或会话状态避免同一回调被并发处理。
- 只公开已确认的 `200` 和 `40105`；其他错误码联系刘文祺。

