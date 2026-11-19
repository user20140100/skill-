# 活动、投票与评分

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理活动弹幕/祝福、投票、评分未显示或提交后状态未更新。入口：`src/models/activityModel.ts`、`src/models/voteModel.ts`、`src/models/ratingModel.ts`，相应请求在 `src/services/activity.ts`、`src/services/vote.ts`、`src/services/rating.ts`。

活动：`activityModel#queryWish` 按班级取活动，检查 `questionDtos` 和 `enableEndDate`；活动过期或无问题时会设置 `wish=null`。错误码 `35005` 也会清空 wish，而一般请求失败返回空数组不等于活动不存在。确认有效活动后才请求弹幕并保存。

投票 model 主要以 `updateTag` 通知刷新，列表/提交逻辑要沿页面及 `src/services/vote.ts` 查；不能仅看 `doUpdateTag` 推断服务端保存成功。评分 model 的规则、明细、班级统计、荣誉与排行分别调用不同 effect，不能把其中一个接口成功解释成所有面板最新。

以活动/投票/评分 ID、班级 ID、请求/提交时间关联。优先从用户实际页面和推送 handler 找入口；这些 model 未必输出 XLog，搜 effect 名称用于定位代码，不当作运行日志。请求失败读 [网络](network-and-file-transfer.md)。

## 代码定位与关联键

| 子域 | 源码与符号 |
| --- | --- |
| 祝福/弹幕 | `src/models/activityModel.ts#queryWish/#check`、`src/services/activity.ts#queryWish` |
| 投票请求与提交 | `src/views/container/Vote/Voting/index.tsx`、`src/services/vote.ts#queryVotes/#postVoteRecord/#queryVoteDetail` |
| 投票刷新标记 | `src/models/voteModel.ts#doUpdateTag` |
| 评分规则与统计 | `src/models/ratingModel.ts#queryClassratingRules/#queryClassRatingStaInfo/#queryRatingRanking`、`src/services/rating.ts` |

活动用 `wish.uid/questionUid` 与 `classUid`；投票用 `voteUid`、`questionUid`、选项 ID、脱敏 `userUid`；评分用 `ruleId`、班级和日/周区间。三者的 ID 不能互换。投票结果页的统计请求与投票提交不是同一接口，也没有可复用的客户端任务 ID。

## 三条业务链

活动 `queryWish` 查班级活动，要求有非空 `questionDtos` 且 `enableEndDate` 未过期，才查弹幕并保存 wish；状态码 35005 会清空 wish，其它异常返回空数组但不必然清空已有状态。`check` 可在活动过期时另外清掉 wish 和弹幕。故“页面无活动”需要区分接口空、过期、业务码和普通失败。

投票记录由页面调用 `postVoteRecord` 的 `/route/vote/v1/record`；`voteModel` 没有提交 effect，`doUpdateTag` 只是刷新标记。提交成功后还可查详情/统计接口 `/record/{uid}/allStatistic`，但统计是否即时更新取决于后端。评分先取得规则并选中 `curRule`，没有 `ruleId` 时班级统计 effect 直接返回；日/周维度决定查询日期与展示值，榜单/荣誉另走请求。

第一次检索先按接口拆分：祝福 `/api/checkin/v1/class/task?type=5` 与弹幕 `/api/checkin/v1/page/review/records`；投票 `/route/vote/v1/votes`、`/route/vote/v1/record`、`/allStatistic`；评分规则 `/api/rating/v1/org/{schoolUid}/rules` 与统计 `/type/statical`。只有目标接口请求/响应或页面状态，才能把“没显示”和“提交失败”区分开。

## 证据指纹与断点

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 活动请求成功但 `wish=null` | 无问题或已过期 | `questionDtos` 数量、`enableEndDate`、设备时间。 |
| 活动请求异常返回空数组 | 不能推断活动不存在 | 状态码 35005 或其它错误、旧 model 状态。 |
| 投票 `updateTag` 变化但没记录 | 只是本地刷新 | `/route/vote/v1/record` 的业务响应、voteUid。 |
| 投票提交成功而统计旧 | 详情统计链路 | `/allStatistic` 响应、后端更新时间。 |
| 评分规则有而统计无请求 | `ruleId` 未选中或日期维度 | 当前 curRule、start/endDay、classUid。 |

这些 model 没有稳定覆盖所有分支的 XLog。优先检索 JS Console/HTTP 中的具体 URL 与业务码，明确采集通道；投票答案、人员信息和评分明细须脱敏。
