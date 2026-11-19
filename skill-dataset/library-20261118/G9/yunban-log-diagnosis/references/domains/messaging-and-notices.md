# 消息、公告与通知

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理新闻/公告推送未显示、列表与详情不一致、屏保公告没更新。入口：`src/push/handlers/messagePush.js`、`src/models/messageModel.ts`、`src/services/message.js`。

## 排查链

`ResourceType.News/Notes 推送 → 月份时间列表 → 当前/旧月份列表请求 → message model 按 monthTime 保存 → Home/消息页渲染`。`messagePush#updateTimeList` 依据新旧 `publishTime` 决定查询月份；跨月或删除后只看当前月会遗漏另一更新。`messageModel` 的新闻与通知列表、分页、详情是不同状态，列表更新不代表已读到详情。

当 `screenProtection.mode=MODE.notice` 且 `notice.id` 存在时，Notes 推送还查询屏保公告详情；屏保未变可能是配置、公告详情或置顶问题。满足霸屏资源条件时，推送也向 Uips 转发，仍需查资源状态与占用模式。

按 `publishUid`、月份、页码和学校/班级/场室 ID 关联。推送入口可查 [IoT/JPush](iot-and-push.md)，屏保显示查 [屏保](screen-protection.md)；消息内容和人员信息脱敏。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 新闻/公告推送 | `src/push/handlers/messagePush.js#updateTimeList` |
| 时间线、列表、详情 | `src/models/messageModel.ts#queryNewsTimeList/#queryInfoTimeList/#queryNewsList/#queryInfoList` |
| 发布 API | `src/services/message.js#queryTimeList/#queryNewsList/#queryInformList/#queryInformDetail` |
| 屏保公告详情 | `src/models/screenProtectionModal.ts#queryInformDetail` |

`publishUid` 只关联某篇内容与详情；列表还要按 `monthTime`、`page`、`schoolUid/classUid/roomUid` 分开。`newPublishTime/oldPublishTime` 可能跨月，缺旧发布时间时无法断定旧月列表已刷新。新闻与公告使用不同 `typeKey` 和 model 状态，不能互借列表结果。

## 推送刷新与阅读分叉

News/Notes 推送先查询月份时间线，再按 `updateTimeList` 选新月份、旧月份或最新月份重新拉第 1 页；若时间线为空，函数直接返回。model 的页码默认在未显式传入时递增，page=1 会替换该月数据，后续页会追加。详情 `/api/publish/v1/resource/{publishUid}/extra` 与列表是独立请求，`isClick=true` 还会调用点击数接口；列表可见不代表详情/点击计数成功。

Notes 推送若当前屏保为 `MODE.notice` 且已有 `notice.id`，还会请求屏保公告详情，但这个 dispatch 没有加入 News/Notes handler 的 `Promise.all`；推送处理完成不等于屏保详情完成。满足霸屏条件还会向 Uips 转发，仍需另查展示占用。

首次检索按 `/api/publish/v1/resource/monthline`、`/api/publish/v1/resources/all`、`/api/publish/v1/resource/{publishUid}/extra` 和 `/view/count` 分段。`/resources/all` 要核对 `typeKey`、`monthTime`、`start`，且 `queryNewsList/queryInfoList` 的 `data.page===1` 才替换当前月列表；其它页追加。详情 HTTP 已返回与整个 effect 成功分开：默认 `isClick=true` 时，后续点击数请求失败仍可使 effect 报错。

## 可观测证据与断点

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 推送到了，未见 monthline 请求 | handler 路由或 HTTP/Console 覆盖 | ResourceType、学校/班级/场室、目标 URL。 |
| monthline 为空 | `updateTimeList` 不发列表刷新 | 响应月份数组、服务端发布条件。 |
| 新月已刷新，旧内容未删除 | 旧月份是否被再次请求 | `oldPublishTime`、旧月 URL、page=1 响应。 |
| 列表有条目，详情空/旧 | 详情接口或 `publishUid` 不匹配 | `/extra` 响应、点击数请求。 |
| 公告详情已更新，屏保仍旧 | RN 屏保状态/模式占用 | `screenProtection.notice.id/mode`、[屏保](screen-protection.md)。 |

本层没有稳定的专用 XLog 指纹；以推送入口、目标 URL 的 JS Console/HTTP 与状态变化组合取证，明确日志通道缺口。内容正文、用户标识和图片链接要脱敏。
