# 传输、响应与重试边界

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。当一条业务链跨 RN HTTP、Native CStore、IoT 或第三方接口时读取。这里给公共判据；业务是否重试、何时写入状态由对应领域的调用方决定。

## 分通道追到结果

| 通道 | 本地入口到可确认结果 | 不可跨越的边界 |
| --- | --- | --- |
| RN 请求 | `request.ts#_request → httpHelper.fetch → HTTP 2xx → JSON 解析 → 业务 statusCode=200 → 调用方` | Sentry 请求 breadcrumb 只表示准备请求；HTTP 200 不表示业务成功；调用方是否更新页面另查。 |
| Native CStore | `CStoreUploader.uploadFile → 本地文件存在 → appId/上传策略 → quick 命中或第三方直传 → onUploadSuccess(fileKey, URL) → 业务引用` | `start ... file upload` 在策略请求之前；上传回调成功不表示引用该文件的业务已保存。 |
| IoT/第三方 | `SDK 回调/业务调用 → 本地处理 → postEvent/fetch 返回 → 对端处理` | `postEvent=true`、Native 回调返回或第三方 HTTP 成功各有自己的语义，不能替代服务端业务终态。 |

RN `_request` 依据 `useNode` 选 host，绝对 URL 不追加 host，默认 `hasToken=true`，已绑定时附学校/场室 ID。`checkHttpResponse` 处理非 2xx，`checkStatusCode` 只接受业务 `200`；异常由 `handleRequestError` 打 JS Console `请求失败` 后继续抛出。`units.ts#log` 在业务成功后打印 URL，但 URL 含 `attendance`、`member` 或 `list` 时只打印 options，不能从这行恢复响应内容。`request.ts#fetch` 是直接 Native fetch 出口，不能假设它也经过上述业务码校验；`uploadEvent` 捕获失败返回 `statusCode=-1`，调用方必须检查。

`CStoreUploader` 在 IO 协程检查文件，按 `isTmp` 选 `yunban-temp` 或 `yunban-business`，向业务后台取 appId/策略，再按策略快传或向第三方上传；返回值须有 `fileKey` 与 URL。文件不存在走 `onUploadFail(404)`，不会打印 `start ... file upload`；策略或上传异常走 `upload file fail:` 与 `onUploadFail(9999)`。该模块没有通用自动重试承诺，是否重试需回到具体调用方。`IotClientDepository.handleCommand` 的 `>>> handle callback` 是属性回调入口；服务指令走注册的 listener。以 `IotLoggerHandler.postResult` 为例，`post log result failed` 说明 SDK 未接受事件，缺这行不能证明远端已经收到。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| RN 构造、校验、错误 | `src/units/network/request.ts#_request/#_uploadEvent/#fetch`、`src/units/network/units.ts#checkHttpResponse/#checkStatusCode/#log/#handleRequestError` |
| Native 上传与回调 | `android/app/src/main/java/com/seewo/yunban/system/helper/cstore/CStoreUploader.kt#uploadFile/#getUploadPlan/#uploadByPolicy` |
| IoT 本地接收与事件上报 | `android/app/src/main/java/com/seewo/yunban/system/helper/IotClientDepository.kt#handleCommand`、`android/app/src/main/java/com/seewo/yunban/plugins/iot/handler/event/IotLoggerHandler.java#postResult` |
| 一例业务层重试 | `src/views/container/Attendance/shared/ReportService/reportResult.js#reportData` |

RN 用目标 URL、方法、脱敏对象 ID、业务码和窄时间窗关联；CStore 加入本地文件名/大小、`isTmp`、回调的脱敏 `fileKey`；IoT 优先 `topic/method/traceId`。这三类通道没有贯穿所有阶段的统一 ID。并发同 URL 或同文件名时，不凭时间相近认定同一次操作。token、签名、完整 URL、BODY 和文件键在报告中脱敏。

## 实际日志指纹与覆盖

| 节点 | 搜索文本/通道 | 可确认范围 |
| --- | --- | --- |
| RN 请求已过业务码 | JS Console 目标 URL | `units.ts#log` 已运行；仍要看调用方状态。仅有 XLog 文件时可能缺失。 |
| RN 请求失败 | JS Console `请求失败` + URL + `statusCode` | `handleRequestError` 分支，继续区分 HTTP、JSON、业务码或网络异常。 |
| CStore 开始 | XLog `CStoreUploader` + `start yunban-business file upload:` / `start yunban-temp file upload:` | 文件检查通过、上传策略尚待完成。 |
| CStore 失败 | `upload file fail:` / `CStore upload coroutine failed:` | 已捕获异常；文件不存在 404 主要由 callback 体现，可能没有这两行。 |
| IoT 属性回调 | `>>> handle callback: topic=` + `method=` + `traceId=` | Native 收到属性回调，不证明 RN handler 或业务完成。 |
| 日志上传结果未被 SDK 接受 | `IotLoggerHandler` + `post log result failed` | 本地 postEvent 返回 false；远端处理结果另取证。 |

`CStoreUploader` 的 start 行为 XLog Debug 级，日志级别过滤后可能缺失。Debug 构建才可能由相应 HTTP 拦截器输出完整 BODY；Release 或只含 XLog 的已解析文本缺 BODY 不等于没请求。CStore 的策略字段、IoT 参数和业务请求体可能含敏感信息，引用时只取阶段和错误码。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| RN breadcrumb，无请求结果 | Native fetch、网络或日志覆盖 | 同 URL 的 HTTP/业务响应、JS Console、服务端请求 ID。 |
| HTTP 2xx、业务码非 200 | 后台业务拒绝 | 脱敏 `statusCode`、业务错误和调用方 catch。 |
| CStore start 后无回调 | appId/策略、第三方上传、协程或日志截断 | 同文件的 `upload file fail`、回调结果、策略/第三方状态。 |
| CStore 回调成功、业务附件缺失 | 调用方是否使用 `fileKey` 再提交 | 后续业务接口及后台文件引用记录。 |
| 同一请求出现多次 | 调用方计时/重试、用户重复操作或重连 | 同一对象键的调度代码与每次请求时间；不能默认 SDK 自动重试。 |
| IoT postEvent 接受、后台仍无结果 | 对端接收与处理 | 服务端 traceId/事件回执。 |
