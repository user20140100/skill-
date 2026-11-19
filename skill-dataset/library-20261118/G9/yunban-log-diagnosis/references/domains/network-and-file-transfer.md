# 网络与文件传输

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理断网、请求超时、HTTP/业务码错误、图片或文件上传失败。主要入口：`src/units/network/request.ts`、`src/units/network/units.ts`、`android/app/src/main/java/com/seewo/yunban/system/helper/cstore/CStoreUploader.kt`、`android/app/src/main/java/com/seewo/yunban/system/helper/HttpHelper.java`。

## 排查链

先分通道：RN `httpHelper.fetch`、Native 业务 HTTP、CStore 上传策略、第三方直传、IoT 上报不能混查。RN 链路为 `选 host/附 token 和绑定信息 → Native fetch → HTTP 状态 → JSON → 业务 statusCode → 页面状态`。CStore 为 `文件存在 → 上传策略 → 快传或直传 → callback → 业务保存返回值`。`CStoreUploader` 的 `start ... file upload` 只说明开始，`upload file fail` 说明失败分支；最终业务结果还要看调用方 callback。

检索 URL、接口业务码、`请求失败`、`CStoreUploader`、`file upload`，再用调用方的文件/任务键关联。仅在 Debug 且采集了直接 logcat 时才可能见 HTTP BODY；Release 没有 BODY 不等于未请求。业务与临时 CStore 文件类型由 `isTmp` 决定，不能仅凭本地临时路径推断上传类型。

响应、回调、重试的通用语义见 [传输](../shared/transport-and-retry.md)。若问题是某个业务的附件，继续读该业务领域；文件路径或 URL 要脱敏。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| RN 请求与业务码 | `src/units/network/request.ts#_request`、`src/units/network/units.ts` |
| Native HTTP | `android/app/src/main/java/com/seewo/yunban/system/helper/HttpHelper.java`、`android/app/src/main/java/com/seewo/yunban/system/helper/http/client/BpHttpClient.java` |
| CStore 策略和上传 | `android/app/src/main/java/com/seewo/yunban/system/helper/cstore/CStoreUploader.kt#uploadFile/#getUploadPlan/#uploadByPolicy` |

优先用 URL、请求方法、业务对象 ID、文件名/大小、脱敏 `fileKey` 和窄时间窗关联。`fileKey` 仅在 CStore 结果之后存在；不能拿相同文件名认定两次上传是同一次。日志没有统一请求 ID 时并发相同 URL 只能给弱关联。

## 分通道的成功条件

RN `_request` 依次经过 Native fetch、HTTP 2xx、JSON 解析和业务 `statusCode=200`。`uploadEvent` 另走 `/audit/v1/upload/event`，捕获失败后返回 `statusCode=-1`，调用方若未检查该值会造成“发起了但没有成功”的误判。

CStore 先检查文件存在，再根据 `isTmp` 选 `yunban-temp` 或 `yunban-business`，取 appId 和 `/route/file/v1/file/uploadPolicy`。策略若含有效 quick 结果则直接返回；否则用第三方 `uploadUrl` 和策略字段上传，最后必须有 `fileKey` 与 URL 才回调成功。业务策略请求、第三方 HTTP 和最终业务附件提交是三个边界。`needCallServer` 在当前实现不触发上传后的业务后台回执，不能虚构这一环。

## 实际日志指纹

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| RN 成功 | JS Console 目标 URL | 已过 RN 的 HTTP/业务码检查；特定 URL 仅打印 options。 |
| RN 失败 | JS Console `请求失败` + URL | 进入错误处理；需区分 `statusCode`、网络断开和 JSON 解析。 |
| CStore 开始 | `CStoreUploader` + `start yunban-business file upload:` / `start yunban-temp file upload:` | 文件检查通过，异步上传开始；不代表策略成功。 |
| CStore 失败 | `upload file fail:` / `CStore upload coroutine failed:` | 捕获到上传异常；还要看调用方 callback。 |
| Native HTTP BODY | Debug 的直接 logcat 拦截器 | 仅当构建和输入包含该通道才可使用。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 业务动作无请求 | 调用条件/日志通道 | effect 入口、绑定/网络状态。 |
| HTTP 失败 | host、网关、网络 | 状态码、同时间窗网络、服务器请求记录。 |
| HTTP 2xx 但业务报错 | 后端业务码 | 脱敏响应码/消息，不贴完整响应体。 |
| CStore `start` 后无 callback | 策略、第三方请求或日志截断 | 文件大小、策略错误、第三方状态码及回调日志。 |
| CStore callback 成功但附件未见 | 调用方是否使用 `fileKey` 提交 | 业务保存接口和后台文件索引。 |
