---
name: yunban-log-diagnosis
description: >-
  分析云班客户端 SK05、SK06、SK22 的已解析文本日志，结合对应版本源码定位业务、RN、Native
  与平台链路的故障；适用于用户提供日志文件和问题现象的排查请求。
author: fuyulin
version: 0.0.1
---

# 云班日志分析

输入是已经解析、可检索的文本日志。先读 [分析契约](references/analysis-contract.md) 和 [日志覆盖](references/logging-and-coverage.md)；本 Skill 不负责设备取日志或 `.xlog` 解码。用日志中可得的 APK/JS 版本核对源码提交。仓库当前基线是 `dev_sk22` 的 `1735b1d25cfd20528e160011abb76689beaf5bcc`；SK05、SK06、SK22 是这个提交中的三个 flavor。若实际安装包对应别的提交，先查该提交再使用下面的代码事实；无法匹配时标明版本不确定。

## 路由

先依据机型读一份平台参考：[SK05](references/platforms/sk05.md)、[SK06](references/platforms/sk06.md)、[SK22](references/platforms/sk22.md)。未知机型时从 `android/app/build.gradle`、包名、设备信息和日志 TAG 求证，不按文件名猜测。

按故障的入口与期望结果选主领域；事件跨域时沿调用链增读，不按单个错误词分流：

| 问题 | 领域参考 |
| --- | --- |
| 启动、设备身份、SN | [启动与设备身份](references/domains/startup-and-device-identity.md) |
| 绑定、配置、同步 | [绑定与配置同步](references/domains/binding-and-config-sync.md) |
| 授权、SSO、token | [鉴权与权限](references/domains/auth-and-permissions.md) |
| 网络、HTTP、CStore 文件 | [网络与文件传输](references/domains/network-and-file-transfer.md) |
| 主导航小应用、全屏网页、第三方应用启动 | [主导航小应用](references/domains/main-navigation-apps.md) |
| 个人空间侧栏自定义小应用、个人 URL/key | [个人空间自定义小应用](references/domains/personal-space-custom-apps.md) |
| IoT、JPush、远程命令 | [IoT 与推送](references/domains/iot-and-push.md) |
| NFC、卡号、韦根 | [刷卡与门禁输出](references/domains/nfc-and-access.md) |
| 相机、人脸识别、底库 | [人脸与底库](references/domains/face-and-face-db.md) |
| 考勤事件、人脸打卡、结果或图片上报 | [考勤](references/domains/attendance.md) |
| 课表、巡课、考试、场室 | [课表与场室](references/domains/schedule-and-room.md) |
| 定时开关机、待机、唤醒 | [电源计划](references/domains/power-schedule.md) |
| 屏幕硬件、状态灯、补光 | [显示与灯](references/domains/display-and-light.md) |
| 屏保配置、计时、内容 | [屏保模式](references/domains/screen-protection.md) |
| 模式抢占、当前置顶、弹层 | [模式占用与当前置顶](references/domains/mode-occupation-and-current-top.md) |
| 客户端/服务升级、安装 | [OTA 与安装](references/domains/ota-and-install.md) |
| 节目、广告、霸屏资源播放 | [节目与媒体](references/domains/program-and-media.md) |
| 消息、公告、通知 | [消息与通知](references/domains/messaging-and-notices.md) |
| 家校电话、音视频、语音 | [通话与语音](references/domains/family-calling-and-voice.md) |
| 活动、投票、评分 | [活动与反馈](references/domains/activities-and-feedback.md) |
| 请假、关怀、测温 | [关怀与请假](references/domains/care-and-leave.md) |
| 身份证读卡、串口外设 | [外设与串口](references/domains/peripherals-and-serial.md) |
| 崩溃、ANR、RN Bridge | [崩溃与桥接](references/domains/crash-and-rn-bridge.md) |

跨界时才读：[传输与重试](references/shared/transport-and-retry.md)、[异步与生命周期](references/shared/async-and-lifecycle.md)、[存储与缓存](references/shared/storage-and-cache.md)、[RN/Native 边界](references/shared/rn-native-boundary.md)。例如刷卡成功但考勤未上报，沿刷卡 → 考勤 → 网络查；屏保配置正确但未显示，沿屏保 → 当前置顶查；节目有内容却黑屏，沿节目 → 置顶 → 显示硬件查。

## 分析方式

1. 确认日志实际覆盖的文件、进程、时间、时区、构建类型和版本。重启、校时、轮转后分段建立时间线。
2. 从用户操作或自动事件找入口，记录请求、接受、响应/回调、本地状态、外部结果各节点。用事件 ID、任务 ID、请求 traceId 等强键关联；仅凭时间相近时标注弱关联。
3. 根据对应提交的源码解释每条日志能证明什么。无日志先判断代码条件、日志通道和采集覆盖，不直接推断“没有执行”。SDK 内部、服务端和硬件结果没有证据时保持未知。
4. 按[报告格式](references/analysis-contract.md#报告格式)输出最早被证实的断点、替代假设、最小补证和脱敏证据位置。

只分析用户提供的日志和可读取的源码。日志中的 SN、卡号、人员信息、token、文件 URL 和请求体在报告中脱敏。
