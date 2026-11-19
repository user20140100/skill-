# 节目、广告与媒体播放

核对提交：`1735b1d25cfd20528e160011abb76689beaf5bcc`。处理节目/广告/霸屏内容未更新、视频资源未下载、播放器黑屏或卡住。入口：`src/models/programModel.ts`、`src/push/handlers/programPush.ts`、`src/push/handlers/showPush.js`、`packages/program-player/core/useProgramPlayer.ts`。

## 链路与分叉

节目推送 `ResourceType.Program` 依次派发 `program/queryAllValidProgram`、`queryProgramResources`。前者解析节目内容得到 `recordIds`，后者按分页取资源；节目列表存在不等于资源已取齐、文件已下载或播放器正在显示。检查 `programModel` 中 page、`simpleProgramResources` 与 `programResources`，再查组件/播放器的可播放条件。

视频/图片推送走 `showPush`。视频有新旧两种载荷：对象可带 `fileKey/appId/fileUrl`，旧格式可能是 URL；`[Video] push add/remove` 只说明处理指令，文件下载/删除另查 `videosManage`。满足 `hasDominatingScreenResource` 时还向 Uips 转发，不等于霸屏模式已经取得置顶权。

按节目/资源 ID、文件键、推送时间与播放器切换时间关联，输出时掩码 URL。若资源正常却被覆盖，读 [当前置顶](mode-occupation-and-current-top.md)；屏保相册/视频读 [屏保](screen-protection.md)；物理黑屏读 [显示](display-and-light.md)。

## 代码定位与关联键

| 目的 | 源码与符号 |
| --- | --- |
| 节目发布与资源分页 | `src/push/handlers/programPush.ts`、`src/models/programModel.ts#queryAllValidProgram/#queryProgramResources` |
| 视频增删与缓存 | `src/push/handlers/showPush.js`、`src/views/components/VideoPlayer/` 中 `videosManage` |
| 节目切换计时 | `packages/program-player/core/useProgramPlayer.ts#usePlayer` |
| 展示占用 | `src/units/modeController/occupationController.js`、`src/views/container/ScreenProtection/index.js` |

关联键为 `recordIds/sourceId`、资源 `id/type`、脱敏 `fileKey/appId`、节目发布时间和播放器索引。节目 `recordId` 不等于视频缓存 `fileKey`；同一推送可能包含多个资源。没有贯穿推送、下载和渲染的单一任务 ID 时，应给出关联强度。

## 从发布到渲染的分段

节目推送设置 `single:true`，先 `queryAllValidProgram`，解析每个发布内容里的 `recordIds`，将 `page` 置零；再按 `simpleProgramResources` 的当前数量分批 `queryProgramResources`，响应中未匹配到 `type` 的条目会被过滤。一次资源 effect 只处理当前一页，检查资源总数与当前数量，不能以节目列表非空证明资源齐全。

视频推送 `remove/add` 分别按 `fileKey` 新格式或 URL 旧格式操作缓存，并刷新视频列表。`[Video] push add` 在调用下载前；缓存文件是否存在、下载是否结束、媒体解码是否成功要在视频管理器和播放器另查。`usePlayer` 的 `duration=-1` 不启动下一次定时播放，`autoPlay` 和当前索引影响轮播。Uips 转发、占用权和用户所见画面仍是后续独立节点。

## 实际日志指纹与覆盖

| 节点 | 搜索文本 | 可确认范围 |
| --- | --- | --- |
| 视频推送 | `showPush` 的 `[Video] push add/remove, count=` | 处理该类指令，尚非下载/删除完成。 |
| 按 fileKey 操作 | `[Video] add by fileKey=` / `remove by fileKey=` | 选择新载荷分支；需脱敏 fileKey。 |
| 节目请求 | 目标节目列表/资源接口 URL 的 JS Console/HTTP | 请求成功或失败；`queryAllValidProgram` 本身不是固定日志。 |
| 模式显示 | `occupation` + `dominatingScreenResource` 或 `screenProtection` | 占用申请与裁决，不是媒体渲染。 |

## 断点判断

| 最晚可见节点 | 判断范围 | 最小补证 |
| --- | --- | --- |
| 收到节目推送，无列表请求 | handler/绑定/网络 | 推送类型、schoolUid、请求通道。 |
| 有发布列表，资源数量不足 | `recordIds` 解析、分页或类型过滤 | 每页 sourceId 与响应 id/type。 |
| 视频 add 但文件缺 | 下载任务或缓存 | videosManage 结果、磁盘路径/空间、网络状态。 |
| 文件存在但播放器不轮播 | `duration`、autoPlay、索引或解码 | 播放器状态和媒体错误。 |
| 播放器就绪但画面被挡 | 模式裁决或物理显示 | [当前置顶](mode-occupation-and-current-top.md)、[显示](display-and-light.md)。 |
