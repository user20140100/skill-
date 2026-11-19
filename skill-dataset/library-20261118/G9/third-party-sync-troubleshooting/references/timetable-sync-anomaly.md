# 课表同步异常定位

## 适用场景

用户反馈某个具体课节在产品侧不存在、未更新或与预期不一致，且反馈信息至少能定位到教室、周次、星期、节次中的大部分关键字段。

前提：已知信息必须能够定位出具体节次；如果连节次都无法确定，先补齐信息，不要继续排查。

进入主排查链路前，先执行两个独立前置分支：

1. 最近一次有没有正确触发数据同步。
2. 反馈场地是不是同步过来的。

## 排查前置认知

开始排查前，先理解本问题涉及的核心库表，不要跳过表级认知直接看日志。

### 1. 标准库课表表

表：`seewo_timetable.lesson`

用途：确认用户反馈的课节当前是否已经存在于标准库课表流水中。

重点字段：

- `uid`：课节唯一标识
- `plan_uid`：排课计划 uid
- `course_uid`、`course_name`
- `classroom_uid`、`classroom_name`
- `teacher_uid`、`teacher_name`
- `subject_uid`
- `week_index`、`day_index`、`section_index`
- `period_uid`、`period_size`
- `lesson_date`、`start_time`、`end_time`
- `strategy`
- `deleted`
- `update_time`

关联表：`seewo_timetable.timetable_plan`

用途：只核查启用中的排课计划，避免查到历史计划或无效计划数据。

排查要求：进入课表查询前，先获取启用中的排课计划；当前问题排查默认只查 `school_uid = '002'` 的启用计划。

重点字段：

- `uid`
- `school_uid`
- `plan_name`
- `enabled`
- `year_name`
- `term_name`
- `term_index`
- `start_day`
- `end_day`
- `update_time`
- `deleted`

### 2. 第三方中间库原始课表表

原始数据表：`third_data_sync.t_third_origin_room_timetable_info`

用途：确认上次同步时保存的第三方原始课节数据中是否存在该课节。

注意：这张表不是非常精准的固定结构数据。由于每个三方的原始数据是异构的，有些字段可能缺失。实际排查时可以先 `limit 1` 查一条最新记录，看原始数据长什么样，再决定后续 SQL 应该按哪个字段定位。

重点字段：

- `c_third_room_uid`、`c_third_room_name`
- `c_third_teacher_uid`、`c_teacher_name`
- `c_subject_name`
- `c_day_index`、`c_section_index`、`c_section_range`
- `c_start_time`、`c_end_time`
- `c_start_week_index`、`c_end_week_index`
- `c_week_index_list_str`
- `c_strategy`
- `c_version`
- `c_meta_uid`
- `c_update_time`
- `c_delete_time`

元信息表：`third_data_sync.t_third_origin_room_timetable_meta_info`

用途：确认原始数据所属版本、第三方编码、状态，辅助锁定最近一批课表数据。

重点字段：

- `c_uid`
- `c_third_code`
- `c_status`
- `c_version`
- `c_update_time`
- `c_delete_time`

三方关联关系表：`third_data_sync.t_third_data_rel`

用途：当标准库、场地表、三方原始数据之间需要做 id 映射时，使用这张表确认 `seewo id` 与 `third id` 的对应关系。

`c_data_type` 取值必须使用 `com.seewo.third.data.sync.constants.SyncDataType` 的 `name()`，禁止使用 code、desc、中文名或自造别名。完整枚举名已写在 skill 主文档的 “SyncDataType 枚举名” 小节；排查场地三方关联关系时使用 `BUILDING_ROOM`，不是 `ROOM`。

重点字段：

- `c_app_code`
- `c_third_code`
- `c_data_type`
- `c_seewo_id`
- `c_third_id`
- `c_unit_id`
- `c_delete_at`

建筑表：`seewo_class.seewo_sys_building`

用途：当用户只提供教学楼名称时，辅助定位教室所属建筑和组织信息。

重点字段：

- `c_uid`
- `c_unit_uid`
- `c_name`
- `c_status`
- `c_is_deleted`

场地表：`seewo_class.seewo_sys_building_room`

用途：当用户只提供场地名称时，辅助反查 `classroom_uid`，用于标准库课表查询。

重点字段：

- `c_uid`
- `c_building_uid`
- `c_unit_uid`
- `c_name`
- `c_status`
- `c_is_deleted`

### 3. 运行记录与过滤规则表

最新同步记录表：`third_data_sync.t_third_sync_record`

用途：确认最近一次课表同步是否执行成功、是否存在异常、执行时间和触发方式。

重点字段：

- `c_third_code`
- `c_uid`
- `c_has_exception`
- `c_exception_info`
- `c_execute_time`
- `c_status`
- `c_cur_data_type`
- `c_trigger_type`

环境配置表：`third_data_sync.t_third_env_config`

用途：查询同步任务的环境配置，重点确认 `c_env_key = 'job.cron'` 的定时任务表达式，用于判断最近一次同步是否应该正常触发。

补充说明：仓库内边缘端通过 `EdgeCommonThirdDataJobHandler` 读取 `job.cron`、`job.param`、`job.type` 后动态注册定时任务；云端接入了 XXL-JOB，相关配置见应用配置中的 `xxl.job.*`。

重点字段：

- `c_third_code`
- `c_unit_id`
- `c_env_key`
- `c_env_value`
- `c_class_path`
- `c_deleted`

黑白名单规则表：`third_data_sync.t_third_black_white_filter_rule`

用途：确认课节是否因为黑白名单规则被过滤。

重点字段：

- `c_third_code`
- `c_unit_id`
- `c_data_type`
- `c_field_name`
- `c_word`
- `c_word_type`
- `c_deleted`

同步异常记录表：`third_data_sync.t_third_sync_error_record`

用途：确认某次同步过程中是否有该课节的异常记录；其中 `json_data` 保存的是三方原始数据的 JSON。

重点字段：

- `c_sync_record_uid`
- `data_type`
- `json_data`

同步过滤记录表：`third_data_sync.t_third_sync_filter_record`

用途：确认该课节是否被过滤，以及命中了哪条过滤规则。

重点字段：

- `c_third_code`
- `c_unit_id`
- `c_data_type`
- `c_third_id`
- `c_json_data`
- `c_filter_rule_id`
- `c_deleted`

## 最小输入信息

至少收集以下信息中的大部分，缺失时先向前线补齐：

- 学校或租户标识：`unitId`、`thirdCode`
- 教室信息：教室名称、教室 uid，至少一个
- 时间信息：周次、星期、节次；如有 `lesson_date` 更好
- 课节辅助信息：学科、老师、开始时间、结束时间、排课策略
- 问题描述：不存在、未更新，还是和第三方不一致

如果用户只提供教学楼或场地名称，先用建筑表、场地表补出 `classroom_uid`，再进入正式排查。

如果用户提供的是场地名称但没有 `classroom_uid`，还需要先确认该场地是否存在三方关联关系；没有三方关联关系时，课表不会同步。

## 推荐排查 SQL

以下 SQL 是课表同步异常排查的推荐起点，实际执行时按已知信息替换占位符。

### 1. 查询启用中的排课计划
巡检
```sql
select *
from seewo_timetable.timetable_plan
where school_uid = '002'
	and enabled = 1
	and deleted = 0;
```

说明：

- 进入课表主流程前先执行这条 SQL，确认当前启用的排课计划。
- 后续查 `lesson` 时，应优先关联这些启用计划，避免查到历史计划数据。

### 2. 查询最近一次同步记录

```sql
select *
from third_data_sync.t_third_sync_record
where c_third_code = '${thirdCode}'
	and c_cur_data_type = 'ROOM_TIMETABLE'
	and c_deleted = 0
order by c_id desc
limit 1;
```

说明：

- 用于判断最近一次数据同步是否有执行记录。
- 示例里已经限定 `c_cur_data_type = 'ROOM_TIMETABLE'`，避免拿到无关数据类型的同步记录。

### 3. 查询定时任务表达式

```sql
select *
from third_data_sync.t_third_env_config
where c_third_code = '${thirdCode}'
	and c_unit_id = '${unitId}'
	and c_env_key = 'job.cron'
	and c_deleted = 0;
```

说明：

- 用于查询当前学校的同步定时任务表达式。
- 要结合最近一次同步记录的 `c_execute_time` 一起判断任务是否在应触发的时间内正常执行。

### 4. 通过场地名称反查场地 uid

```sql
select *
from seewo_class.seewo_sys_building_room
where c_unit_uid = '${unitId}'
	and c_name = '${roomName}'
	and c_is_deleted = 0;
```

说明：

- 用于先拿到场地的 `c_uid`。
- 如果同名场地不止一条，继续结合建筑、状态等条件缩小范围。

### 5. 查询场地是否存在三方关联关系

```sql
select *
from third_data_sync.t_third_data_rel
where c_third_code = '${thirdCode}'
	and c_unit_id = '${unitId}'
	and c_data_type = 'BUILDING_ROOM'
	and c_seewo_id = '${roomUid}'
	and c_delete_at = 0;
```

说明：

- 用于确认场地是否已经建立三方关联关系。
- `c_data_type` 必须使用 `SyncDataType.name()`；场地对应枚举是 `BUILDING_ROOM`。
- 如果不存在三方关联关系，说明场地本身没有同步来源，课表也必然不会同步，直接结束流程。

### 6. 查询课表是否真的不存在

```sql
select l.*
from seewo_timetable.lesson l
inner join seewo_timetable.timetable_plan plan on plan.uid = l.plan_uid
where plan.enabled = 1
	and plan.school_uid = '002'
	and plan.deleted = 0
	and l.deleted = 0
	and l.classroom_uid = '${classroomUid}'
	and l.day_index = ${dayIndex}
	and l.week_index = ${weekIndex};
```

说明：

- 这是标准起点 SQL。
- 前提是必须已经能定位到具体节次；如果同一天有多节课，继续补 `section_index`、`start_time`、`course_name` 等条件缩小范围。

### 7. 查询最新一批原始课表元信息

```sql
select c_uid
from third_data_sync.t_third_origin_room_timetable_meta_info
order by c_id desc
limit 1;
```

说明：

- 用于先拿到最近一批原始课表数据的 `c_meta_uid`。
- 这里查出来的 `c_uid`，就是后续原始数据表里的 `c_meta_uid`。
- 如果需要更精准，应继续加 `c_third_code`、`c_status` 等条件限制。

### 8. 先看一条原始课表数据长什么样

```sql
select *
from third_data_sync.t_third_origin_room_timetable_info
where c_meta_uid = '${metaUid}'
limit 1;
```

说明：

- 由于原始数据异构，先看一条样例再决定后续过滤字段。
- 若 `limit 1` 发现字段名和示例 SQL 不完全一致，后续查询应优先以实际返回的列名为准。
- 如果字段齐全，再补 `c_third_room_name`、`c_day_index`、`c_section_index`、`c_subject_name` 等条件。

### 9. 查询原始三方库里是否存在目标课节

```sql
select *
from third_data_sync.t_third_origin_room_timetable_info
where c_meta_uid = '${metaUid}'
	and c_third_room_name = '${roomName}'
	and c_day_index = '${dayIndex}';
```

说明：

- 这是示例 SQL，不是固定终版 SQL。
- 由于不同三方字段不一定完整，必要时改为按 `c_third_room_uid`、`c_section_index`、`c_start_time`、`c_week_index_list_str` 等字段组合查询。

### 10. 查询最近一条同步记录

```sql
select c_uid
from third_data_sync.t_third_sync_record
where c_third_code = '${thirdCode}'
	and c_cur_data_type = 'ROOM_TIMETABLE'
	and c_deleted = 0
order by c_id desc
limit 1;
```

说明：

- 这条 SQL 用于快速拿最近一次课表同步记录的 `c_uid`，给异常记录表做关联查询。
- 已经限定 `thirdCode`、`ROOM_TIMETABLE` 和未删除条件，避免拿到无关同步记录。

### 11. 查询同步异常记录里有没有这门课

```sql
select *
from third_data_sync.t_third_sync_error_record
where c_sync_record_uid = '${syncRecordUid}'
	and data_type = 'ROOM_TIMETABLE'
	and json_data like '%${courseName}%';
```

说明：

- `json_data` 存的是三方原始 JSON。
- 这张表的字段名是 `data_type`，不是 `c_data_type`。
- 如果课程名不稳定，也可以改成按老师名、教室名、三方 id 等关键片段模糊查。

### 12. 查询是不是被黑白名单或过滤规则过滤掉了

```sql
select *
from third_data_sync.t_third_sync_filter_record
where c_data_type = 'ROOM_TIMETABLE'
	and c_json_data like '%${courseName}%';
```

说明：

- 这张表的字段名是 `c_data_type`，和异常记录表里的 `data_type` 不同，写 SQL 时不要混用。
- 命中过滤记录后，应继续结合 `c_filter_rule_id` 回查 `t_third_black_white_filter_rule`，确认具体命中的规则。
- 若已知三方 id，优先按 `c_third_id` 查，比 `like` 更稳定。

## 标准排查链路

### 前置独立分支 A：最近一次有没有正确触发数据同步

先查询最近一次同步记录，再查询 `third_data_sync.t_third_env_config` 中 `c_env_key = 'job.cron'` 的配置。

手动触发补充：

- 云端环境优先走现有 XXL-JOB 控制台触发。
- 边缘端环境优先核对 `EdgeCommonThirdDataJobHandler` 读取到的 `job.cron`、`job.param`、`job.type` 配置，并结合 `logs/xxl-job/jobhandler` 下的日志确认是否真的执行过。
- 如果现场没有可用的手动触发入口或调度控制台，记录为阻塞并转交对应维护人，不要在数据库里伪造执行记录。

判定结果：

- 没有 `job.cron` 配置：结束，先反馈任务配置缺失。
- 有 `job.cron` 配置，但最近一次没有拿到有效同步记录：结束，直接反馈 bug。
- 配置了 `job.cron`，但按表达式本应触发却没有正常执行：结束，直接反馈 bug。
- 最近一次同步记录和定时任务触发都正常：通过该分支，进入下一个前置分支。

### 前置独立分支 B：场地是不是同步过来的

先通过场地名称查询 `seewo_class.seewo_sys_building_room` 拿到场地 `c_uid`，再用场地 `c_uid` 查询 `third_data_sync.t_third_data_rel`。

判定结果：

- 没有场地记录：结束，先反馈场地基础数据异常。
- 有场地记录，但没有三方关联关系：结束，直接退出流程，因为场地没有三方关系，课表必然不会同步。
- 存在场地三方关联关系：通过该分支，进入课表主流程。

### 第一步：先获取启用中的排课计划

先查询 `seewo_timetable.timetable_plan`，只查 `school_uid = '002'`、`enabled = 1`、`deleted = 0` 的计划。

判定结果：

- 没有启用中的排课计划：结束，反馈基础配置异常。
- 存在启用计划：继续第二步。

### 第二步：确认课表是否真的不存在

根据用户反馈的课节信息，在 `seewo_timetable.lesson` 中核查目标课节。优先使用上面的“查询课表是否真的不存在”SQL；如果同一天数据较多，继续补节次、课程名、开始时间等条件缩小范围。

判定结果：

- 查得到：标准库已有该课节，继续第三步。
- 查不到：标准库不存在该课节，继续第四步。

### 第三步：确认上次同步的中间库数据是否存在反馈课节

先查最近一批 `c_meta_uid`，必要时先 `limit 1` 看一条原始数据结构，再在 `third_data_sync.t_third_origin_room_timetable_info` 中核查上次课表同步保存的原始课节数据。

判定结果：

- 存在：说明问题更可能出在同步异常或被过滤，继续检查过滤规则。
- 不存在：说明问题更可能出在中间库异常或同步频率不足，跳到第四步。

如果原始数据存在，则继续在同步过滤记录、黑白名单、异常过滤等数据里查找是否存在该课节。

判定结果：

- 存在：结束，直接反馈过滤原因。
- 不存在：继续排查同步日志。

日志排查要求：

1. 抓取上次课表数据同步日志。
2. 结合 `third_data_sync.t_third_sync_record` 确认最近一次执行记录。
3. 先看 `t_third_sync_error_record` 中是否已有该课节的异常记录，再检查日志里是否出现异常堆栈、解析报错、落库报错、批量写入失败等信号。

结束条件：

- 存在异常：结束，报 bug。
- 不存在异常：结束，按疑似同步逻辑缺陷报 bug。

### 第四步：中间库异常或同步频率不足

当标准库不存在且中间库也不存在该课节时：

1. 将当前数据同步频率告知前线。
2. 手动触发一次数据同步，确认该课节是否可以恢复。

结束条件：

- 恢复：结束，结论为数据同步频率问题。
- 未恢复：结束，结论为中间库异常。

## 结论收敛

排查结果应收敛到以下几类之一：

- 同步任务配置缺失。
- 最近一次同步没有正确触发，需要报 bug。
- 场地没有三方关联关系，课表必然不会同步。
- 启用中的排课计划缺失，属于基础配置异常。
- 被黑白名单或异常过滤规则过滤。
- 同步日志存在异常，需要报 bug。
- 手动同步后恢复，属于同步频率问题。
- 手动同步后仍未恢复，属于中间库异常。

## 约束

- 本分支只处理课表同步异常，不扩展到外部系统排查。
- 若需要补 SQL、修代码、补日志埋点，应另开实现任务，不在本文展开。
