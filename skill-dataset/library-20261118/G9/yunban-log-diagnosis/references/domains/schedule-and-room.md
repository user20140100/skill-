# 课表、巡课、考试与场室

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理课表过期、课程屏保错、巡课/考试模式异常、场室预约未更新。入口：`src/models/scheduleModel.ts`、`src/models/roomOrderModel.ts`、`src/models/patrollessonModel.js`、`src/models/examModel.js`。

课表链：`schoolUid/roomUid + 当前周日期 → queryCourseScheduleList → weekSchedules → UipsInterface.updateBanpaiData('Course', ...) → reducer → 页面/屏保`。`scheduleModel.ts` 遇服务端 `weekIndex/totalWeek=-1` 会保留既有值；“接口成功”不等于显示周次变化。`setCourseAttendanceList` 只处理包含 `lessonId` 且类型为课程的考勤事件，课堂签到显示缺口需核对过滤条件。

场室预约：`roomOrderModel.ts#queryLatestRoomOrder/queryRoomOrders` 依赖 `roomUid/schoolUid`；`queryRoomOrders` 在缺少 `unitUid` 时提前返回。巡课、考试各有自己的 model 和推送 handler，不可凭课表刷新推断它们也刷新。

检索 `queryCourseScheduleList`、`queryLatestRoomOrder`、`schedulePush`/`planPush` 和实际接口 URL；这些符号不保证有落盘日志。按学校、场室、周次/日期关联。课程屏保读 [屏保](screen-protection.md)，考试或巡课抢占读 [当前置顶](mode-occupation-and-current-top.md)。

## 代码定位与关联键

| 场景 | 源码与符号 |
| --- | --- |
| 本周/下周及人员课表 | `src/models/scheduleModel.ts#queryCourseScheduleList/#queryNextWeekScheduleList/#queryStudentSchedule` |
| 场室预约 | `src/models/roomOrderModel.ts#queryLatestRoomOrder/#queryRoomOrders`、`src/services/roomOrder.ts` |
| 巡课/考试事件 | `src/models/patrollessonModel.js`、`src/models/examModel.js` |
| 课表推送入口 | `src/push/handlers/schedulePush.js`、`src/push/handlers/planPush.js`；若具体扩展名或路由不同，以 `src/push/handlers/` 的实际注册为准 |

用 `schoolUid/roomUid`、一周的日期范围、`weekIndex/totalWeek`、课程 `lessonId`、预约 `unitUid` 与日期关联。学校/场室相同不意味着当前周与下周是同一个查询；`lessonId` 和预约 ID 也不能互换。报告说明设备时区与校时情况。

## 业务分叉与数据状态

`queryCourseScheduleList` 根据当前周的周一至周日生成日期范围，带学校/场室和房间信息请求。响应的 `weekIndex/totalWeek=-1` 会沿用旧 model 值，`days` 同步给 Uips `Course` 后再写 Redux；Uips 收到数据、Redux 写入和页面/屏保显示是三层。`setCourseAttendanceList` 只接收带 `lessonId` 且 `attendanceType=course` 的事件，其余考勤事件不会映射为课程签到。

场室预约 `queryRoomOrders` 先生成日期列表，缺 `unitUid` 就直接返回；`queryLatestRoomOrder` 与列表请求是两条链。巡课和考试有独立 model/事件及占用权，课表接口成功不能解释它们的所有状态。

课表本周请求为 `/api/timetable/v4/{schoolUid}/items/{roomUid}`，下周请求附查询参数并经 `adapterCourse` 转换；服务端原始响应和最终 model 数据可不同。预约列表是 `POST /api/room/v1/roomOrders`，最新预约则通过 `HTTP_ROOM_ORDER_SERVER` 的 `fetch(.../schedule/latest)` 获取，未走同一 `request.ts` 业务码处理。因此最新预约缺 JS 通用请求日志，不能据此判定未请求。

## 可观测证据与断点

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 收到课表刷新指令，未见接口 | handler 路由或绑定前置 | 推送方法、`schoolUid/roomUid`、请求 URL。 |
| 课表接口成功但周次未变 | `-1` 复用旧值或 Redux 更新 | 返回的 `weekIndex/totalWeek`、当前周日期。 |
| Redux 有课表、屏保错 | 屏保内容类型/组件或 Uips 消费 | `screenProtection.mode`、Uips `Course` 数据、页面截图。 |
| 考勤事件有但课表无签到 | `lessonId`/类型筛选 | 对应 `eventId`、`lessonId`、`attendanceType`。 |
| 预约列表没有请求 | `unitUid` 缺失或页面未触发 | 当前场室、`unitUid`、effect 入口。 |
| 考试/巡课数据有而页面没置顶 | 模式占用裁决 | [当前置顶](mode-occupation-and-current-top.md) 的 `final status`。 |
| 最新预约有，列表空 | 两条接口与 `unitUid` 门槛不同 | 最新预约 URL、列表 POST 请求、日期范围。 |

这些 model 主要靠接口和下游状态取证；`queryCourseScheduleList` 等函数名是源码搜索种子，并非固定 XLog。若只有应用 XLog 而无 JS Console/HTTP，明确“当前文本不足以确认请求是否发出”。
