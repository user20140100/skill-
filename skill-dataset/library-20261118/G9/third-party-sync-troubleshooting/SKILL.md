---
name: third-party-sync-troubleshooting
description: >-
  当前仓库三方数据同步问题排查 skill。适用于排查同步异常、数据缺失、 中间库是否有数据、黑白名单过滤、同步日志报错、手动触发同步、课表同步异常，
  以及围绕 third_data_sync、seewo_timetable、t_third_sync_record、
  t_third_sync_error_record、t_third_sync_filter_record、
  t_third_black_white_filter_rule、t_third_data_rel 关联关系 的结构化定位场景。
version: 1.0.0
author: luobin12754
---

# Third-party sync troubleshooting

## Purpose

提供一个独立的问题排查 skill，用于处理当前仓库内的运行期同步异常。先在本文件中完成问题分类，再只读取命中的问题分支文档。当前已覆盖课表同步异常，并内置两个前置独立分支：最近一次同步是否正确触发、场地是否存在三方关联关系。

## How to use this skill

1. 先根据用户反馈判断问题类别，不要先翻日志。
2. 若是课表问题，前提是已知信息必须能够定位到具体节次；如果连节次都无法确定，先补齐信息再排查。
3. 在本文件里选择唯一的问题分支。
4. 进入分支后，再阅读对应分支文档并先理解涉及库表。
5. 按分支顺序推进，除非文档要求，否则不要跳过前置核查直接看日志。
6. 当结论命中分支定义的结束状态时停止扩散排查。
7. 查询 `third_data_sync.t_third_data_rel` 时，`c_data_type` 必须使用 `com.seewo.third.data.sync.constants.SyncDataType` 的 `name()`，不要使用 code、desc、中文名或自造别名；可用枚举名见下方完整列表。

## SyncDataType 枚举名

查询 `t_third_data_rel.c_data_type`、`t_third_sync_record.c_cur_data_type`、`t_third_sync_filter_record.c_data_type` 等数据类型字段时，只能使用以下枚举名：

```text
UNIT
CLASS
USER
SUBJECT
BUILDING
BUILDING_ROOM
GRADE
TEACHER_CLASS
DEPARTMENT
TEACHER_DEPARTMENT
STUDENT_CLASS
CAMPUS
ACADEMY_MAJOR
TIMETABLE_PLAN
ROOM_TIMETABLE
DEBUG_ROOM_TIMETABLE
CALENDAR
STUDENT_OPTIONAL_CLASS
CLASS_BUILDING_ROOM_REL
TIMETABLE
TEACHER
STUDENT
PARENT
TEACHER_WITH_PHONE
TEACHER_COMMON
SCHOOL_GROUP
MIS_CUBE
COUNT_STUDENT
COUNT_ROOM_TIMETABLE
COUNT_STUDENT_OPTIONAL_CLASS_REL
COUNT_STANDARD_OPTIONAL_CLASS_REL
SCHEDULE_TABLE
OPTIONAL_STANDARD_CLASS_REL
COURSE_STUDENT_REL
ROOM_OCCUPY
PKH_LESSON_RULE_MAP
COURSE_ID_MAP
RESCHEDULE_ROOM_TIMETABLE
SEATING_CHART
ADJUST_ROOM_TIMETABLE
LUBO_SYNC_FACE
BANPAI_SYNC_FACE
COUNT_BANPAI_FACE
USER_FACE_TRAIT_VALUE
USER_CARD_LOCAL
USER_PASSWORD
OPTIONAL_CLASS
OPTIONAL_STANDARD_CLASS_REL_V2
BANPAI_SYNC_CLOUD_FACE
USER_CARD_CLOUD
PARENT_CLOUD
CLASS_ADVISER_CLOUD
EXAM_PLAN_CLOUD
ROOM_ORDER_CLOUD
SEND_INBOX
THIRD_DATA_QUERY
DEFAULT
```

常见排障映射：

- 场地：`BUILDING_ROOM`，不是 `ROOM`。
- 课表：`ROOM_TIMETABLE`。
- 学生：`STUDENT`。
- 班级：`CLASS`。
- 教师：优先确认业务用的是 `TEACHER_COMMON` 还是历史 `TEACHER`。

## Current issue categories

| Category | File | Summary |
|------|------|------|
| 课表同步异常 | [references/timetable-sync-anomaly.md](references/timetable-sync-anomaly.md) | 前提是能定位到具体节次，先做“同步是否触发”“场地是否有三方关系”两个前置分支，再按“启用排课计划 -> 标准库课表 -> 中间库原始数据 -> 过滤/异常记录 -> 同步日志 -> 手动同步”链路定位原因 |

## 问题路由

### 课表同步异常

满足任一条件即可进入 [references/timetable-sync-anomaly.md](references/timetable-sync-anomaly.md)：

- 用户反馈某个教室某周某天某节课在产品侧查不到。
- 用户反馈某个具体课节同步后消失、未更新、与第三方不一致。
- 前线提供的信息是“教室 + 周次 + 星期 + 节次 + 学科/老师”这类课节级反馈。

进入前必须确认信息足以定位出具体节次。进入后先看“排查前置认知”和“推荐排查 SQL”，不要直接开始查日志。
