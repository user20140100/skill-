# 请假、关怀与健康信息

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理请假申请/状态、关怀绑定与测温信息缺失。入口：`src/services/leave.ts`、`src/models/easiCareModel.ts`、`src/services/temperature.ts`。

请假：`queryUserLeaves` 以 `schoolUid/userUid/pageStart` 分页，详情用 `leaveUid`；区分 `Pending/UnPass/Pass/Revoke` 等状态，申请已发送不等于审批通过。列表与详情接口不同，先确认用户和学校范围、页码及日期，再讨论状态不一致。

关怀：`easiCareModel#queryCareBindInfo` 以班级 ID 查询，并将 `isBound` 转为是否有 `careClassCode`；接口返回对象不等于已绑定。测温走 `src/services/temperature.ts` 的独立接口，不要把考勤外设的温度数据自动等同于关怀页面数据。

检索具体 URL、业务码、`leaveUid` 和班级 ID；无固定应用日志时使用网络/页面证据并明确覆盖限制。用户姓名、请假原因、健康数据和附件链接须脱敏。跨接口问题读 [传输](../shared/transport-and-retry.md)。

## 代码定位与关联键

| 子域 | 源码与符号 |
| --- | --- |
| 请假列表/详情/创建/撤销 | `src/services/leave.ts#queryUserLeaves/#getLeaveDetail/#createLeave/#revokeLeave` |
| 请假页面动作 | `src/views/container/Leave/Personal/index.tsx#onCreate/#onRevoke` |
| 关怀绑定 | `src/models/easiCareModel.ts#queryCareBindInfo`、`src/services/easiCare.ts#queryCareBindInfo/#bindCare` |
| 测温记录 | `src/services/temperature.ts#queryTemperatureRecords/#postTemperatureRecord`、`src/views/container/Temperature/index.tsx` |

请假以脱敏 `userUid`、`schoolUid`、`leaveUid/leaveId`、`pageStart` 和时间范围关联；创建请求前还没有 leave ID，不能仅凭相近姓名将列表记录匹配到这次提交。关怀用 `classUid/careClassCode`，测温用 `meterDay` 与班级 ID；卡号和体温均为敏感数据。

## 独立业务链

请假：`页面表单 → createLeave POST → Promise 成功 → 提示提交成功/刷新列表 → 待审批状态 → 审批结果`。`onCreate` 会在提交时置 loading，成功后关闭弹窗并刷新；`createLeave` 本身会在 JS Console 打完整参数，报告绝不能原样转录。撤销走 DELETE `/leave/{leaveUid}` 后刷新；“撤销成功”只表示该接口通过客户端检查，列表新状态另需确认。状态 1/2/3/4 分别是审核中、未通过、已通过、已撤回。

关怀 `queryCareBindInfo(classUid)` 把 `isBound` 重算为 `!!careClassCode`。即使响应有其它字段，缺关怀班级编码也会显示未绑定；绑定操作 `bindCare` 是单独 PUT。测温 `queryTemperatureRecords` 按学校、班级和 `meterDay` 查询，`postTemperatureRecord` 是写入接口；查询成功不证明当天每个学生都已有测温记录。

首次检索把接口分开：请假列表 `/api/v1/attendance/v2/user/leaves`、详情/撤销 `/api/v1/attendance/v1/leave/{leaveUid}`、创建 `/api/v1/attendance/v1/student/leave`；关怀绑定 `/api/care/v1/{classUid}/carebind`；测温 `/route/temperature/v1/record`。请假列表固定 `pageSize=30`，前页没有目标记录时要查下一页；测温列表的 `meterDay` 需与设备本地日期对齐。

## 证据指纹与断点

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 点击提交，未见 POST | 表单校验或页面 loading 门槛 | 页面错误、脱敏字段是否齐全、请求 URL。 |
| JS Console `createLeave`，无成功提示 | 请求/业务码或页面异常 | POST 响应、`handleRequestError`、页面 catch。 |
| 创建成功但列表无记录 | 分页、筛选或后台处理 | `userUid/schoolUid/pageStart`、列表响应、新 leave ID。 |
| 关怀响应成功但显示未绑定 | `careClassCode` 为空 | 脱敏关怀编码是否存在、当前 classUid。 |
| 测温列表空 | 目标日期/班级或未写入 | `meterDay`、POST 记录、服务端查询。 |

此域除 `createLeave` Console 和通用网络日志外，固定业务 XLog 很少；不要把 effect 名称写成日志指纹。已解析文本若不含 JS Console/HTTP，只能给出代码条件和补证路径。
