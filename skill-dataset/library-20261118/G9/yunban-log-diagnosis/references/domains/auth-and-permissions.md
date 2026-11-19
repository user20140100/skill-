# 鉴权与权限

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理设备/用户 token、SSO、功能授权、按钮或资源缺失。入口：`src/units/network/request.ts`、`src/units/network/token.ts`、`src/units/network/units.ts`、`src/models/authStatusModel.ts`、`src/services/sso.ts`。

## 排查链

`绑定与身份 → token 注入 → HTTP/业务响应 → 失效处理 → 授权配置查询 → model 状态 → 功能开关/页面`。`request.ts` 默认 `hasToken=true`，绑定成功后附学校和场室 ID；`units.ts#checkHttpResponse` 区分 HTTP 错误，`#checkStatusCode` 要求业务 `statusCode=200`。设备令牌 `40112` 有专门分支，不能把 HTTP 200 当作授权成功。

`authStatusModel.ts#queryResourceList` 把授权配置转为资源项，并尝试同步活体配置到 Native；同步失败只在 Console 打 `sync liveness detect configs to native failed`，因此“RN 资源已更新”和“Native 活体/灯状态已更新”必须分别证实。角色更新还有 `src/push/handlers/authorizationPush.ts#UpdateRolePower`。

检索请求 URL/业务码、`40112`、`queryResourceList` 及具体资源 key；若输入没有 Console，标注覆盖缺口。不要复制 token 或完整授权响应。网络失败读 [传输](../shared/transport-and-retry.md)，绑定前置条件读 [绑定](binding-and-config-sync.md)。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 请求构造 | `src/units/network/request.ts#_request`、`src/units/network/token.ts` |
| HTTP 与业务码处理 | `src/units/network/units.ts#checkHttpResponse/#checkStatusCode/#handleRequestError` |
| 资源开关与 Native 同步 | `src/models/authStatusModel.ts#queryResourceList` |
| 角色权限推送 | `src/push/handlers/authorizationPush.ts#UpdateRolePower` |
| SSO 服务端点 | `src/services/sso.ts` |

关联键优先为目标 URL、脱敏学校/场室 ID、资源 `key`、用户或设备身份和一次请求时间窗。token 只在本地核对是否存在/是否被更新，不得原样输出；HTTP 请求日志未携带可靠统一 traceId 时，多个并发相同 URL 请求不能只靠同一秒合并。

## 请求与授权状态边界

`_request` 根据 `useNode` 选择 host，绝对 URL 不加 host；默认 `hasToken=true`，已绑定时附 `schoolUid/roomUid`。随后经 Native `httpHelper.fetch`、HTTP 2xx 检查、JSON 解析、业务 `statusCode=200` 检查，再到 model。非 2xx、JSON 解析错误、业务 40112 和普通业务错误的原因不同。`InvalidUserTokenStringCode` 是 HTTP 错误分支的另一条路径；累计超过 5 次且已绑定时可能弹 `TokenAuthModal`。

`queryResourceList` 将 `configDtos` 转为 `enable=d.value==='1'` 的资源表，并先尝试同步活体配置到 Native；失败被捕获并继续走后续资源处理。状态灯是否打开再由 `statusLampShow`、`schedule.inCourse` 决定。最终 `setResourceList` 是 RN 资源状态节点，不能拿它替代 Native 活体同步或实体灯变化。SSO、角色权限与设备资源开关分开查。

## 实际日志指纹

| 节点 | 搜索文本与通道 | 可确认范围 |
| --- | --- | --- |
| 请求成功后日志 | JS Console 中目标 URL；`attendance/member/list` 类 URL 只打印 options，其余可能还含响应 | 已通过 HTTP/业务码检查并进入 `log()`；注意敏感数据。 |
| 请求失败 | JS Console `请求失败` + URL/错误对象 | 进入 `handleRequestError`；结合 statusCode 判断层次。 |
| 资源映射 | JS Console `result` + 资源 key 列表 | `queryResourceList` 已完成 DTO 映射；不代表页面或灯已更新。 |
| 活体同步失败 | `sync liveness detect configs to native failed` | Native 同步尝试失败，但 RN 后续可能继续。 |
| 特殊设备令牌 | 错误对象 `statusCode=40112` | 业务码分支，不等于 HTTP 401。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| URL 请求未见 | 调用方前置条件或日志覆盖 | 对应 effect、绑定状态、Native HTTP 日志。 |
| HTTP 非 2xx | 传输/服务端网关层 | 状态码、目标 host、同时间窗网络状态。 |
| HTTP 2xx、业务码非 200 | 后台业务鉴权或配置 | 脱敏业务码、学校/用户作用域。 |
| 资源列表已映射，按钮仍缺 | reducer、组件条件或角色权限 | `resourceConfig` key、角色推送、页面状态。 |
| Native 同步失败或灯不亮 | Native 桥接/平台灯能力 | 该异常、`RNCDevice` 调用及机型 Adapter 结果。 |
