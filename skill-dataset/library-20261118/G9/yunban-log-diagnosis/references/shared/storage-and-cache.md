# 本地状态、文件与缓存边界

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理“接口成功但页面没变”“上传成功但业务找不到文件”“重启后状态变化”等问题。每次先确定对象处于哪层：接口响应、RN reducer 内存、持久化存储、Native 数据库/磁盘、最终页面或 SDK。

## 数据跨层的实际路径

| 例子 | 状态与存储链 | 不可直接推出的结论 |
| --- | --- | --- |
| RN model | `effect 请求 → put(reducer) → Redux state → 页面 selector/props` | 请求成功不说明 reducer 已提交，也不说明组件当前正在读取该字段。 |
| Redux 持久化 | `src/index.js` 调用 `init`，`src/app.js` 配 `persistReducer` + AsyncStorage，`PersistGate` 等待恢复；持久化黑名单为 `blacklist/personalCenter` | model 的内存值、AsyncStorage 已写入、重启后恢复是三个节点；不能从一次 put 直接断言已落盘。 |
| 考勤结果/图片 | `FaceRecorder → attendanceResult/attendanceImages → reportResult/reportImages → 成功后推进或清理` | 页面提示、本地队列、`/data` 结果与 `/images` 图片是独立状态，详见[考勤](../domains/attendance.md)。 |
| 人脸库 | `faceDBModel.queryClassFaceDB → RN classFaceData`；另一路 `updateFaceData → FaceDataModule → FaceService.dataRefresh → Native DB/SDK` | RN 已有人员列表不能说明 Native 底库或 SDK 可识别。 |
| 节目 | `queryAllValidProgram → simpleProgramResources → queryProgramResources 分页 → programResources → 播放器` | 发布列表有资源 ID 不等于资源详情齐、文件存在或画面显示，详见[节目](../domains/program-and-media.md)。 |
| CStore 文件 | `本地 file.isFile → 上传策略/直传 → fileKey/URL → 调用方保存引用` | 上传成功不说明业务对象已写入该 `fileKey`，详见[传输](transport-and-retry.md)。 |

`src/units/dva/retSetHook.js` 处理 `RESET_ALL` 时重建大部分 model，却明确保留 `device`、`jPush.registerId`、`attendanceResult`、`attendanceImages` 等；所以“重置后还有考勤队列”与这份代码相符。另一方面，是否真的持久化成功仍取决于 redux-persist 写入和恢复，须结合具体时点/状态证据。`src/index.js` 的持久化黑名单是根 model 名称，不要把它误读成这些 model 内所有字段的局部过滤。

人脸 `queryClassFaceDB` 仅 `put(setClassFaceData)`；`updateFaceData` 还要先查算法激活，`active.data` 为真才调用 Native，`FaceDataModule` 的 `updateFaceData:` 日志写在调用 `dataRefresh` 之前。`FaceUserDBHelper` 定义 Native `user_v5.db`，但文件存在或 RN 名单条数相等都不是“此次刷新已完成”的证据。节目 model 在取得发布内容时把 `programResources` 清空，再按当前数量分页加载资源；必须用同一批 `recordIds/sourceId` 核对资源数量和播放器取用。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 持久化初始化/恢复 | `src/index.js`、`src/app.js#init`、`src/units/dva/create.js`、`src/units/dva/retSetHook.js` |
| 考勤双队列 | `src/models/attendanceModel.js#recordAttendanceResult/#recordAttendanceImages`、`src/views/container/Attendance/shared/ReportService/` |
| 人脸 RN 与 Native | `src/models/faceDBModel.ts#queryClassFaceDB/#updateFaceData`、`android/app/src/main/java/com/seewo/yunban/packages/face/rn/data/FaceDataModule.kt#updateFaceData`、`android/app/src/main/java/com/seewo/yunban/packages/face/service/ym/FaceUserDBHelper.java` |
| 节目资源 | `src/models/programModel.ts#queryAllValidProgram/#queryProgramResources`、`packages/program-player/core/useProgramPlayer.ts` |
| 文件上传 | `android/app/src/main/java/com/seewo/yunban/system/helper/cstore/CStoreUploader.kt#uploadFile` |

用同一对象键串层：考勤用 `userUid#eventId#attendanceDate`，人脸库用脱敏 `schoolUid/classUid` 与刷新时间，节目用 `recordId/sourceId`，文件用路径、大小和回调 `fileKey`。不同层可能没有统一事务 ID；仅因数量相同或日志同秒不代表同一版本。人员、图片 URL、SN 和文件键在报告中脱敏。

## 实际日志指纹与边界

| 节点 | 搜索文本/通道 | 可确认范围 |
| --- | --- | --- |
| RN 接口成功 | JS Console 目标 URL | 已通过对应 RN HTTP/业务码检查；是否 put/reducer 成功仍需核对。 |
| RN 状态更新 | 多数 reducer 没有固定日志；按业务找后续页面/组件日志 | 缺 reducer 日志不能判定状态未变；需要可得的 state 快照或调用方证据。 |
| 人脸激活/刷新入口 | JS Console `afu`；XLog `FaceDataModule updateFaceData:` | 算法激活结果和 Native 刷新调用前入口；不能证明 DB/SDK 已完成。 |
| 考勤本地候选 | `RNDEBUG` + `record attendance items:`；JS Console `reportImages` | 前者在结果 dispatch 前，后者在图片上传前；均不是持久化/后台成功。`RNDEBUG` 还受 `Config.LOG` 控制。 |
| CStore 开始/失败 | `CStoreUploader` + `start ... file upload:` / `upload file fail:` | 本地文件检查后进入策略，或上传异常；业务引用另查。 |

Redux 持久化、`RESET_ALL` 和多数 reducer 没有可依赖的固定成功 XLog。只有已解析日志而无状态快照时，要把“已写入内存/磁盘”列为待证，不用接口成功行填补。日志文件自身的快照与轮转限制读[日志覆盖](../logging-and-coverage.md)。

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 接口成功、页面仍旧 | effect 的 put、reducer、selector 或组件生命周期 | 同键 model 状态、页面 props、对应业务域日志。 |
| 重启后数据不同 | 持久化写入/恢复、黑名单、RESET_ALL 与后续刷新 | 重启前后 state、`RESET_ALL` 时点、PersistGate/存储错误。 |
| RN 人脸名单有、识别不到 | 算法激活、Native 刷库/SDK 映射 | `afu`、`FaceDataModule` 及 Native 刷新结果。 |
| 发布节目有 ID、画面没资源 | 资源分页、磁盘文件、播放器索引 | 当前资源数量、文件状态和播放器日志。 |
| CStore 有 URL、业务附件缺 | 调用方是否保存/引用 `fileKey` | 后续业务请求与后台对象记录。 |
