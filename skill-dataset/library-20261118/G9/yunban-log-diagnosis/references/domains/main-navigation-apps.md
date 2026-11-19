# 主导航小应用

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理主导航小应用不显示、点击无响应、WebView 白屏/被拦截、第三方 Android 应用打不开。入口：`src/models/applicationModel.ts`、`src/views/container/Navigation/NavigationModal.tsx`、`src/views/container/Navigation/NavigateTo.tsx`、`src/views/container/NavigationApp/`。个人空间侧栏小应用读[个人空间自定义小应用](personal-space-custom-apps.md)；考勤向小应用发回调读[考勤](attendance.md)，不是本页的打开链路。

## 从配置到打开

`RootPage.startSchoolScopedInitialization` 在网络、绑定、`schoolUid` 等条件具备后派发 `application/queryAppList`；首页数据任务和 `homePush.refreshAppInfo` 也会刷新。effect 按顺序请求 `/api/application/v2/school/app/all?schoolUid=...&snCode=...`（总列表、顺序/状态）和 `/api/application/v1/school/{schoolUid}/app/all?snCode=...`（自定义小应用详情）；任一请求失败进入 `catch`，不提交新 `appList`。只有两份 `data` 都存在时才按 `appKey` 合并为 `appList`，并生成 `naviApps`、`ucenterApps`。`applicationModel.ts` 此处错误日志 TAG 是 `NFCTrain`，不能按 TAG 字面归为刷卡故障。

`NavigationModal.getApps` 先过滤 `showStatus === true`；有 `routeName` 的配置作为内置页面入口，空 `routeName` 的作为小应用入口。自定义详情缺失时无法得到该小应用的 URL、打开类型等字段；当前合并代码还会把未匹配的 `undefined` 放入 `appList`，随后访问 `r.showStatus` 可能报 JS 异常。总列表里存在 `appKey` 不等于导航项可打开。小应用点击由 `NavigateTo.navigateToApp` 再按当前 `appList` 的同一 `appKey` 查找；找不到会提示“该小应用已经下架或失效”。

`fullScreenType=0` 普通网页分支写入 `application/setNaviAppKey`；`NavigationApp` 还要求 `appKey` 出现在 `naviApps`（由详情中的 `fullScreenSwitch` 决定）、`naviVisible` 为真且 `appList` 找到详情，才渲染 `NavigationApp/Modal → EasiWebView`。因此“导航图标可见”“已设置 naviAppKey”“WebView 已挂载”是三个节点。`fullScreenType=1` 走 `startExternalAppExact`：有 `fullScreenActivity` 时指定 Activity，否则按包名启动；Native Promise resolve 只证明启动调用被接受，不能证明第三方应用页面正常。无匹配类型会弹非法小应用提示。

`isAI` 网页应用另先跳 `PersonalLogin`；登录后 `fullScreenSwitch` 为真时走 `NavigationApp`，否则走 `AIClass` 页面。不要把登录中、普通 WebView 和第三方 Android 应用的日志按同一路径解释。普通 `EasiWebView` 校验 URI、附设备上下文、应用域名白名单并加载页面；初始 URL 可加载不等于页面内跳转通过白名单，也不等于 H5 业务成功。

## 代码定位与关联键

| 节点 | 源码与符号 |
| --- | --- |
| 刷新与合并 | `src/views/pages/RootPage/index.js#startSchoolScopedInitialization`、`src/views/container/LoadData/LoadDataTasks/homeTask.js`、`src/push/handlers/homePush.js#refreshAppInfo`、`src/models/applicationModel.ts#queryAppList` |
| 两个配置接口 | `src/services/application.ts#queryAllAppList/#queryCustomAppList` |
| 导航显示与点击 | `src/views/container/Navigation/NavigationModal.tsx#getApps`、`NavigateTo.tsx#navigateToApp` |
| 网页弹层与 AI 分叉 | `src/views/container/NavigationApp/index.js#render`、`Modal.js#render`、`src/views/container/PersonalCenter/PersonalLogin/index.js#navigateToAIClass` |
| WebView 与 Android 外部应用 | `src/views/components/EasiWebView/WebView.js`、`android/app/src/main/java/com/seewo/yunban/packages/webView/basic/BasicEasiWebView.java`、`android/app/src/main/java/com/seewo/yunban/packages/activity/ActivityModule.java#startExternalApp/#startExternalAppExact` |

以脱敏 `appKey` 贯穿两份配置、`appList/naviApps`、点击和弹层；辅以 `schoolUid`、`snCode`、`routeName`、`appStatus`、`fullScreenSwitch`、`fullScreenType`。网页问题再关联脱敏 host 与点击时间，Android 应用问题关联包名/Activity；同名不同 `appKey` 不要合并。URL 可能含身份参数，不在报告中粘贴全文。

## 实际日志指纹与边界

| 节点 | 搜索文本/通道 | 可确认范围 |
| --- | --- | --- |
| 配置请求成功 | JS Console 两条 `/api/application/.../app/all` URL | 分别通过 HTTP 和业务码校验；仍须核对合并、显示条件。 |
| 配置异常 | JS Console `请求失败` + 对应 URL；RN XLog `NFCTrain` 的错误 | 查询/解析失败分支；`NFCTrain` 在这里是 applicationModel 的 TAG。 |
| 点击分支 | JS Console `fullScreenType` | 找到当前 `appKey` 后进入类型分支，不代表 WebView/Android Activity 已打开。 |
| 普通网页开始加载 | `EasiWebViewManager` + `onPageStarted`，或 `set sources` | Native WebView 入口，不能证明页面加载完或 H5 可用。 |
| 网页错误 | `EasiWebViewManager:onReceivedError`；JS Console `handleError` | 传输/渲染错误；域名白名单拦截主要通过 RN 回调显示 403，未必有专属 XLog。 |
| AI 网页 | JS Console `AIClassPage url:` | AI 弹层已拼出加载 URL；其中可能有 UID/SN，必须脱敏。 |
| 外部应用启动问题 | 当前调用处没有固定的启动成功/失败 XLog；拒绝后仅显示错误提示 | 需查用户所见提示、Native 异常或目标应用日志；单靠主应用日志不证明外部应用运行结果。 |

配置接口的 JS Console 可能包含完整响应，Native `onPageStarted`、`set sources` 可能包含 URL，分析时只摘取脱敏 `appKey`、host 和错误码。日志仅来自 XLog 时，JS Console 的 `fullScreenType`、`handleError` 可能缺失；不要把无行直接判为未点击。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 有总列表、无详情列表 | 第二接口、网络/业务码或 `appKey` 合并 | 两接口同轮响应、对应脱敏 `appKey`。 |
| 两接口成功、导航未显示 | `showStatus`、`routeName`、详情匹配或 JS 异常 | 合并后的条目、`NavigationModal.getApps` 条件和 Console 异常。 |
| 点击后图标仍在、网页不出现 | `fullScreenType`、`naviApps/fullScreenSwitch`、`naviVisible` | 同键的 model 状态、`NavigationApp` 渲染条件。 |
| WebView 已开始、页面空白/403 | URI、网络、白名单或 H5 自身 | 脱敏 URL host、WebView 错误/拦截事件、H5 Console。 |
| 第三方启动 Promise 成功、页面异常 | 目标包/Activity 自身 | 目标应用进程日志和前台 Activity。 |
