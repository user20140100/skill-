# 个人空间自定义小应用

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理个人空间侧栏没有自定义小应用、点击后空白、个人 URL 参数错误、个人访问 key 获取失败或网页加载失败。入口：`src/models/applicationModel.ts`、`src/views/container/PersonalCenter/widgets/SideTab.tsx`、`src/views/container/PersonalCenter/PersonalApplication/index.js`。主导航全屏/外部应用读[主导航小应用](main-navigation-apps.md)；个人空间登录本身读[鉴权](auth-and-permissions.md)及相关人脸/刷卡领域。

## 从列表到个人页面

与主导航共用 `application/queryAppList`：先取总列表，再取自定义应用详情，按 `appKey` 合并。仅当总列表条目 `routeName` 为空、详情存在且 `personCenterSwitch` 为真时加入 `ucenterApps`；`SideTab` 从 `application.ucenterApps` 绘制侧栏。主导航的 `showStatus === true` 过滤发生在 `NavigationModal`，`ucenterApps` 的生成没有这个同样的过滤条件；不能用主导航是否显示判断个人空间侧栏是否应显示。详情里的 `personCenterUrl` 与主导航的 `fullScreenUrl/fullScreenType` 是不同字段。

用户进入个人空间后，`SideTab.handleSideBarSelected` 选中 `application` 并传 `appKey/name`，`PersonalCenter` 选用 `TABWIDGET.application → PersonalApplication`。如果刷新后 `ucenterApps` 不再包含所选 `appKey`，`SideTab.componentDidUpdate` 切到 `course`。`PersonalApplication.countUri` 另从完整 `appList` 找详情，并用当前 `roleInfo.uid/sid` 替换 `personCenterUrl` 的 `${swbp_uid}`、`${swbp_code}`；侧栏有条目不能直接证明 URL 已可用。若所选 `appKey` 在 `appList` 已不存在，当前代码在访问 `app.personCenterUrl` 时可能直接报 JS 异常，需要查崩溃/Console，而非推断 WebView 网络失败。

当个人 URL 的查询参数 `encrypt=1` 时，请求 `/api/userinfo/v1/user/{userId}/key`，把返回的 `userKey/ttl` 附到 URL，再写入组件状态；请求失败会打印 `personCenter` 错误，`finally` 仍设置原 URL。无 `encrypt=1` 则直接设置 URL。组件随后渲染 `EasiWebView`，其封装会追加 `_swbpdata`（除非 URL 带 `_swbptype=self`）、合并应用白名单与 `seewo.com`，并把首个页面 host 加入可访问列表。URI 格式错误、DNS/页面错误、跳转 host 被拦、H5 内部报错属于不同断点。

## 代码定位与关联键

| 节点 | 源码与符号 |
| --- | --- |
| 配置查询与开关映射 | `src/models/applicationModel.ts#queryAppList`、`src/services/application.ts#queryAllAppList/#queryCustomAppList` |
| 个人空间侧栏 | `src/views/container/PersonalCenter/widgets/SideTab.tsx#handleSideBarSelected/#componentDidUpdate` |
| 选中内容 | `src/views/pages/PersonalCenterPage/PersonalCenter.tsx#handleTabSelected`、`TABWIDGET` |
| 个人 URI 与访问 key | `src/views/container/PersonalCenter/PersonalApplication/index.js#countUri`、`src/services/application.ts#queryPersonKey` |
| 网页加载和白名单 | `src/views/components/EasiWebView/index.js`、`WebView.js`、`android/app/src/main/java/com/seewo/yunban/packages/webView/basic/BasicEasiWebView.java` |

以脱敏 `appKey` 关联总列表、详情、`ucenterApps`、选中项和 `appList`；再以脱敏用户 UID/学号及 URL host 关联个人 key 请求、WebView。`roleInfo` 是当前进入个人空间的用户，不应拿设备绑定人员代替。`userKey`、`ttl`、完整 URL、`_swbpdata` 含敏感信息，报告只留是否存在及脱敏 host/错误码。

## 实际日志指纹与边界

| 节点 | 搜索文本/通道 | 可确认范围 |
| --- | --- | --- |
| 应用列表 | JS Console 两条 `/api/application/.../app/all` URL；失败时 `请求失败` | 接口响应进入模型前的请求结果；不能证明已加入 `ucenterApps`。 |
| 合并异常 | RN XLog `NFCTrain` 的错误 | `applicationModel.queryAppList` 捕获异常；TAG 名称不能当作 NFC 证据。 |
| 侧栏点击 | 分析/埋点名 `device_personal_space_click_menu_navigation`，`classify=application` | 代码会发送点击埋点；输入日志未必含埋点，且不证明页面加载。 |
| 侧栏渲染 | JS Console `tabItems` | 仅内置 tab 列表调试输出，不能据此证明自定义 `ucenterApps` 已绘制。 |
| 个人 key | JS Console `/api/userinfo/v1/user/.../key`、`请求失败`、`personCenter` | key 请求成功或失败分支；`personCenter` 错误后仍可能尝试加载未附 key 的 URL。 |
| WebView 开始与错误 | `EasiWebViewManager` + `onPageStarted` / `onReceivedError`；JS Console `handleError` | 页面请求开始或 WebView 错误；不证明 H5 业务完成。白名单拦截可表现为页面 403。 |

埋点可能只在远端统计系统可见；JS Console 和 XLog 的覆盖范围也不同。Native WebView 日志的 URL 和请求头可能带个人参数，不能原样引用。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 应用列表已有键、侧栏没有 | 自定义详情、`routeName`、`personCenterSwitch` | 两接口同键条目及合并后的 `ucenterApps`。 |
| 点击后跳回课程 | 刷新后的 `ucenterApps` 不再含所选键 | 选中前后列表与 `SideTab.componentDidUpdate` 时序。 |
| 点击后空白且无 WebView | `appList` 详情丢失、URL 构造异常、组件状态 | JS 异常、选中 `appKey`、`personCenterUrl` 是否存在。 |
| key 请求失败后页面拒绝 | `encrypt=1`、用户 UID、key 接口 | 脱敏业务错误码与是否附 `userKey/ttl`。 |
| WebView 启动后白屏/403 | URL、网络、跳转 host 白名单、H5 自身 | 脱敏 host、WebView 错误/拦截事件、H5 Console。 |
