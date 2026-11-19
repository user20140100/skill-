# 网络、响应语义与 CStore

本文件只记录跨领域通用的网络边界。各业务接口、请求体和“业务成功后更新什么状态”必须以对应领域手册为准。代码事实基于 ab680809。

## 请求到日志的实际路径

默认 Retrofit 使用 FullLogOkHttp，日志级别是 BODY。CStore 和人脸特征接口使用 BasicLogOkHttp，日志级别是 BASIC；不能期待这些接口一定保留完整 multipart 请求体或完整响应体。

所有客户端依次经过网络可用性、服务器地址、设备请求头、响应解密与 HTTP 日志相关拦截器。两个常见的请求前断点是：

| 现象 | 日志或异常 | 可确认的事实 |
| --- | --- | --- |
| 网络不可用 | NetworkInterceptor + Network is not available | 请求在进入后续网络链路前被拒绝，不能因缺少 HTTP 请求行就断言业务代码没有尝试调用接口 |
| 服务器地址未配置 | local server not set | HostInterceptor 拒绝请求，当前服务器地址仍是本地占位地址 |

HeaderInterceptor 为每次请求生成新的 x-device-traceId，并添加设备序列号、版本与时间戳。该 traceId 未写入当前业务任务模型；若原始 HTTP 日志保留它，可用于同一次请求的相关日志比对，但不能跨请求复用。

DecryptInterceptor 不对人脸特征和考勤接口的响应执行解密处理。分析接口失败时，先按原始响应和应用层 onCommonResponse 或 onOptionalCommonResponse 的调用点判断，不要因为是否经过解密而推断业务成败。

## 通用响应判断

HTTP 状态、网络日志和应用层业务成功是三个不同层次：

1. 请求准备或 HTTP 请求行出现，只证明客户端进入网络边界。
2. HTTP 响应出现，仍需看业务码和领域代码使用的响应扩展。
3. 只有领域日志确认本地状态已回填、任务已删除或结果已发射，才能表述为该客户端业务节点完成。

不同接口对 data 为空的处理不同。不得把门禁 opened 的可空成功规则外推到考勤、签到、配置或人脸同步。

## CStore 语义

CStoreUploaderRepositoryImpl 将 uploadFile 的第二个参数传给上传接口的 isTempCstore；上传接口中的 isTemp 固定为 false。接口注释说明实际七天保存策略由 isTempCstore 控制。

| 场景 | 调用参数 | 本地后续 |
| --- | --- | --- |
| 开门人脸图 | isTemp=false | 成功时回填开门任务的 faceFileKey；失败可降级为无图上报 |
| 考勤人脸图 | isTemp=true | 成功或失败后调用本地考勤记录逻辑，失败时 fileKey 为空 |
| 签到人脸图 | isTemp=true | 成功或失败后调用人脸签到接口，失败时 facePicFileKey 为空 |
| 设备日志压缩包 | isTemp=true | 远程日志上传成功后仅保存下载地址，随后删除本地临时目录 |

CStore 上传成功需要结合两层日志：CStoreUploaderRepositoryImpl 的 upload file success，以及领域调用方对 fileKey 的回填或下游请求日志。前者不自动证明业务已经使用该文件。

本地缓存图片或压缩包被删除，与 CStore 是否临时保存不是同一个含义。输出报告时不得输出完整 fileKey、downloadUrl、请求头或 multipart 内容。
