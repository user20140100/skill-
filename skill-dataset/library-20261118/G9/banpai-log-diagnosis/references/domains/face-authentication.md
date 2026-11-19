# 人脸认证

## 边界

本手册覆盖相机帧进入人脸服务、YM 算法识别、FaceUser 回调、人脸特征同步及其对开门、考勤、签到的下游影响。代码事实基于 ab680809。

“识别出用户”只说明人脸服务给出了用户回调；是否开门、完成考勤或签到，要继续使用对应领域手册验证。人脸特征、姓名、用户标识和图片均为敏感信息，应脱敏。

## 代码定位与关联键

下列源码路径均相对 app/src/main/java/com/seewo/yunban。

| 目的 | 路径与关键符号 |
| --- | --- |
| 相机生命周期与监听器 | usecase/face/FaceControllerUseCase.kt：start、stop、addOnFaceEventListener |
| 人脸服务及 IoT | usecase/face/FaceServiceUseCase.kt：getFaceApi、handleCommandMessage |
| 远端同步与重试 | data/remote/face/FaceRepositoryImpl.kt：syncFaceData、syncDataInternal |
| 算法用户保存与识别 | infrastructure/face/algorithm/ym/YMFaceImpl.kt：saveFaceUser、trackPersonId |
| 人脸同步 API | data/remote/api/IFaceApi.kt：getFaceData |

| 关联强度 | 键与使用限制 |
| --- | --- |
| 同步记录 | schoolUid、page、searchFromDateTime、FaceData.updateTime | API 当前没有客户端生成的同步批次 ID；多页同步必须保留连续时间窗 |
| 识别回调 | 脱敏 FaceUser.userId 加识别时间 | 人脸服务未生成可跨领域复用的识别事件 ID |
| 下游业务 | 门禁 taskId，考勤 ruleRecordKey 或签到 orderId | userId 相同不能证明它们是同一次业务操作 |
| 图片证据 | 下游生成的 fileKey | fileKey 不存在于人脸特征同步和算法识别阶段 |

## 识别与业务分流

    TextureView Surface 可用
      -> FaceControllerUseCase.start
      -> 启动相机，并在首次启动请求强制人脸数据同步
      -> FaceVerifyContainerView 输入普通相机帧
      -> YMFaceImpl 跟踪和识别
      -> FaceUser 回调给已注册的 OnFaceEventListener
      -> 当前页面的开门 / 考勤 / 签到处理

Surface 销毁时 FaceControllerUseCase 会停止相机并清除跟踪图。回调监听器由页面 ViewModel 注册和移除，所以同一张人脸能否进入某个业务，还取决于当时哪个页面及监听器处于活动状态。

YMFaceImpl 对低于或等于 75 的置信度不进入有效用户识别。算法层还可能因本地人脸服务未初始化、追踪到的人脸未匹配、UserDao 未找到用户或特征不兼容而不能给出可用 FaceUser。

## 人脸数据同步

    首次相机启动 / SyncData.loadConfigData / IoT userPhotoRefresh
      -> FaceRepositoryImpl.syncFaceData
      -> 校验人脸服务已初始化、15 秒同步间隔和是否正在同步
      -> GET /user/face/feature/v1/school/user/data，单页最多 100 条
      -> YMFaceImpl.saveFaceUser
      -> 成功时更新最后更新时间，满页继续取下一页

首次相机启动和 userPhotoRefresh 会强制同步。同步失败会设置 faceSyncFailFlag，并在 60 秒后再次强制同步；下次强制或失败后同步会把查询时间向前回退 1 秒。clearFace 会取消当前同步任务；FaceServiceUseCase 同时重置算法库和仓库的时间状态。

SyncData 的配置步骤触发人脸同步后并不等待这项异步同步结束。同步页的配置成功只能证明 ConfigRepository 的三类配置请求完成，不能证明人脸特征已经全部写入算法库。

## 日志指纹

| 节点 | TAG 或文本 | 出现时确认的事实 |
| --- | --- | --- |
| 相机生命周期 | FaceControllerUseCase + onSurfaceTextureAvailable / onSurfaceTextureDestroyed | 相机启动或停止路径被调用 |
| 同步被跳过 | FaceRepositoryImpl + 人脸服务未初始化 / 同步中或未到同步间隔 | 本次未执行远端同步 |
| 同步开始 | syncFaceData: 开始同步人脸数据 | 已准备拉取人脸数据 |
| 拉取分页 | syncDataInternal: updateTime / 同步 N 条数据 | 远端同步的查询和返回批次 |
| 写入算法库 | FaceService][syncFaceData] 用户服务存储 FaceUser 成功或失败 | 对应用户的算法库写入结果 |
| 同步失败 | 同步人脸数据出错 | 本次请求未得到成功业务响应，已安排延时重试 |
| 人脸识别 | YMFaceImpl + 回调用户 / 识别出用户 | 算法层提供了用户回调 |
| 识别失败 | 未找到匹配的用户 / UserDao中没有userId / 特征无法识别 | 识别或本地映射在该节点未完成 |

## 断点判断

| 最晚可见节点 | 最早可确认断点 | 下一步 |
| --- | --- | --- |
| 无 Surface 可用日志 | 相机视图或生命周期之前 | 查页面是否展示、相机权限和视图绑定 |
| 有同步请求，无用户写入成功 | 拉取响应、分页或算法库写入 | 查同步错误、返回数量和每个用户的失败日志 |
| 有识别回调，无开门或打卡日志 | 人脸回调到当前业务监听器 | 查当前页面、监听器注册、用户是否属于当前考勤或课次 |
| 有考勤或签到图片处理，无业务完成 | 已进入下游业务 | 切到考勤与签到手册继续查接口或队列 |
| 有开门鉴权，无最终事件上报 | 已进入门禁下游 | 切到门禁手册，使用 taskId 跟踪 Outbox |

不要将同一用户的同步写入成功或识别成功，直接推断为任意一次业务操作成功。
