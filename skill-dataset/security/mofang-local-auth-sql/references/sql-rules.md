# SQL 生成规则

四张配置表的字段定义、硬性约束与 SQL 模板。流程规范见 `SKILL.md`，此处不重复。

## `tb_service_open` — 服务开通

仅在「新服务需默认开通」或用户明确要求洗数据时生成。

固定字段：
- `app_code = 'mis-admin'`
- `unit_id = '002'`
- `extra = '{"activeTimeRange":[0,32503564800000],"count":-1,"monthCount":-1}'`（无限时间、无限点数）
- `expire_time = 32503564800000`
- `c_status = 1`、`c_sync_flag = 1`
- `delete_at = 0`
- `c_operator_source = 'cloud'`、`c_version = ''`、`c_activate_time = 0`

规则：
- `c_order_uid` 使用随机 32 位 UUID（不带连字符）
- `operator_uid` 未提供时用 `3418e4f3bfef4efe97cf6aa15b3d3f8f`
- `create_time` / `update_time` 未指定时用同一个当前时间

```sql
INSERT INTO seewo_class.tb_service_open
    (app_code, unit_id, service_code, extra, operator_uid, create_time, update_time,
     delete_at, expire_time, c_operator_source, c_order_uid, c_version,
     c_activate_time, c_status, c_sync_flag)
VALUES
    ('mis-admin', '002', 'teacher-student-evaluation',
     '{"activeTimeRange":[0,32503564800000],"count":-1,"monthCount":-1}',
     '3418e4f3bfef4efe97cf6aa15b3d3f8f', '2025-10-14 16:38:50', '2025-10-14 16:38:50',
     0, 32503564800000, 'cloud', '27b6cf00dd444adfb44cd8b9063acf33', '',
     0, 1, 1);
```

## `t_power_config` — 权限点

必填：`c_code`、`c_name`、`c_parent_code`、`c_order`

规则：
- `c_code` 全局唯一
- 一级权限 `c_parent_code = ''`；二级及以下必须引用已存在或本次生成的父权限
- 必须用 `ON DUPLICATE KEY UPDATE`，重复写入时可更新

新增 / 更新：
```sql
INSERT INTO mofang_local.t_power_config
    (c_code, c_name, c_parent_code, c_order)
VALUES
    ('TEACHER_STUDENT_EVALUATION_MANAGEMENT', '师生评教', 'PINCO_MANAGEMENT_BACKGROUND', 22)
ON DUPLICATE KEY UPDATE
    c_code = VALUES(c_code),
    c_name = VALUES(c_name),
    c_parent_code = VALUES(c_parent_code),
    c_order = VALUES(c_order);
```

删除（按 `powerCode`，不处理父子级联）：
```sql
DELETE FROM mofang_local.t_power_config WHERE c_code = 'POWER_CODE';
```

顺序变更（只更新 `c_order`）：
```sql
UPDATE mofang_local.t_power_config SET c_order = 22 WHERE c_code = 'POWER_CODE';
```

## `t_app_role_power_config` — 角色授权

必填：`c_service_code`、`c_role_code`、`c_role_name`、`c_role_level`、`c_power_code`

规则：
- 一条记录 = 一个服务下某角色拥有某权限
- 每个 `(service_code, role_code, power_code)` 组合独占一行；多角色共享权限时也要分别写
- 必须显式补齐 `manager` 的超管授权，默认覆盖本次服务下全部新增权限
- `c_role_level`：校级 = `1`，院级 = `2`

新增：
```sql
INSERT INTO mofang_local.t_app_role_power_config
    (c_service_code, c_role_code, c_role_name, c_role_level, c_power_code)
SELECT 'attendance', 'ATTENDANCE_ADMIN', '考勤管理员', 1, 'ATTENDANCE_VIEW'
WHERE NOT EXISTS (
    SELECT 1 FROM mofang_local.t_app_role_power_config
    WHERE c_service_code = 'attendance'
      AND c_role_code = 'ATTENDANCE_ADMIN'
      AND c_power_code = 'ATTENDANCE_VIEW'
      AND c_delete_time = 0
);
```

删除（按 `powerCode` 清理全部关联）：
```sql
DELETE FROM mofang_local.t_app_role_power_config WHERE c_power_code = 'POWER_CODE';
```

## `t_index_app_config` — 首页卡片

仅当用户明确要求卡片或描述了平台入口时才生成。

必填：`c_app_id`、`c_app_key`、`c_name`、`c_desc`、`c_order`、`c_url`、`c_color`、`c_icon`
可选：`c_powers`

规则：
- `c_app_key` 必须等于服务编码
- `c_powers` 是 JSON，表示卡片可见的权限范围；无权限限制用 `NULL`

```sql
INSERT INTO mofang_local.t_index_app_config
    (c_app_id, c_app_key, c_name, c_desc, c_order, c_url, c_color, c_icon, c_powers)
SELECT 'attendance', 'attendance', '智慧考勤', '考勤业务入口', 10,
       '/kindlink/frontend/attendance/index', 'SKY_BLUE', 'ATTENDANCE',
       JSON_ARRAY('ATTENDANCE_VIEW')
WHERE NOT EXISTS (
    SELECT 1 FROM mofang_local.t_index_app_config
    WHERE c_app_id = 'attendance'
      AND c_app_key = 'attendance'
      AND c_delete_time = 0
);
```

## 最少确认清单

通用：
- 服务编码是什么，是否全新服务，存量学校是否默认开通
- 需要哪些角色、角色名称、校级还是院级
- 每个角色拥有哪些权限

涉及"默认角色""所有角色""系统预置角色"时（先按 `edge-db-read.md` 用 `ccloud-cli` 查询目标机构，查不到再问）：
- 默认角色名单、对应 `role_code`、`role_name`、角色层级
- 哪些属于手动创建角色

删除权限点：`powerCode`
变更权限点顺序：`powerCode` + 新 `c_order`
首页卡片：`app_id`、名称、描述、顺序、URL、颜色、图标、是否按权限控制展示
服务开通洗数据：是否指定 `operator_uid`、`create_time`

## 用户只给中文名的处理

- 用户只给中文名、未给编码时，先问是否允许自动生成稳定的全大写编码；未确认不直接生成
- 但若中文名依赖现有角色体系或现有父权限，这类编码影响 SQL 目标对象，不能自动生成，必须先确认
