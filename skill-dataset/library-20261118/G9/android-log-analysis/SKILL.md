---
name: android-log-analysis
description: "Analyze logs captured from Android devices (logcat, dmesg, bugreport, tombstone, pstore, crashdump, dumpsys, etc.) to reconstruct event timelines, identify anomalies, and perform root cause analysis. Optionally correlates with AOSP-derived source code when invoked from a source tree. Use when the user provides Android device logs and asks for log analysis, timeline reconstruction, anomaly detection, crash analysis, or mentions 日志分析, 时空链, 异常分析, tombstone, bugreport, crashdump, ANR, or panic."
author: zhonghongyu
---

# Android Log Analysis (日志分析助手)

分析 Android 设备抓取的日志，重建事件时空链条、识别异常、给出初步原因分析。特异性地面向基于 AOSP 源码派生的 Android 设备。

## Activation Conditions

- 用户提供了 Android 设备日志文件或目录路径
- 用户希望了解设备在某段时间内发生了什么（时空链）
- 用户希望定位、分析日志中的异常或问题
- 用户提到"日志分析"、"时空链"、"异常"、"崩溃"、"ANR"、"tombstone"、"bugreport"等关键词

---

## Phase 0: Input Collection

### 0.1 Required Input

| Input | Description | Required |
|---|---|---|
| Log path | 日志文件或目录路径 | **必须** |

**无日志路径时立即向用户索要，不猜测、不跳过。**

### 0.2 Optional Inputs

| Input | Description | Default |
|---|---|---|
| 时间范围 | 用户关注的起止时间 | 分析全部日志 |
| 现象描述 | 用户观察到的表现（黑屏、重启、卡顿等） | 无 |
| 操作描述 | 触发问题前用户做了什么 | 无 |
| 怀疑方向 | 用户猜测的可能原因 | 无 |
| 源码模块提示 | 用户指向的源码位置或模块名 | 无 |

### 0.3 Source Code Detection

检测当前工作目录是否为 AOSP 源码树：

```
是否存在 .repo/ 或当前目录为单个 .git 仓库？
  ├─ YES → 源码模式：可结合代码分析
  └─ NO  → 纯日志模式：仅基于日志分析
```

**绝不主动询问或搜索源码位置**——仅在 agent 工作目录恰好是源码树时启用源码模式。

---

## Phase 1: Log Discovery & Classification

### 1.1 Path Exploration

```bash
# 若路径为目录，递归发现所有日志文件
find <log_path> -type f \( -name "*.log" -o -name "*.txt" -o -name "*.gz" \
  -o -name "*.zip" -o -name "bugreport*" -o -name "tombstone*" \
  -o -name "last_kmsg*" -o -name "console-ramoops*" -o -name "dmesg*" \
  -o -name "logcat*" -o -name "*.minidump" -o -name "*.fulldump" \
  -o -name "*.dmp" -o -name "*.core" -o -name "dumpsys*" \
  -o -name "anr_*" -o -name "traces.txt" -o -name "*.xlog" \) 2>/dev/null

# 解压 .gz / .zip 以读取内容
```

### 1.2 xlog Preprocessing

当发现 `.xlog` 文件时，必须先将其解码为可读文本日志，再进行后续分析。xlog 是一种二进制日志格式（常见于微信 Mars/xlog 框架），无法直接阅读。

提供两个版本的解码脚本：

| 脚本 | Python 版本 | 路径 |
|---|---|---|
| **decode_xlog.py** (默认) | Python 3 | `/config/.cursor/skills/android-log-analysis/decode_xlog.py` |
| **decode_xlog_py2.py** (备用) | Python 2.7 | `/config/.cursor/skills/android-log-analysis/decode_xlog_py2.py` |

**解码流程：**

```bash
SKILL_DIR="/config/.cursor/skills/android-log-analysis"
XLOG_VENV="$SKILL_DIR/.xlog_venv"

# 1. 设置 Python venv（仅首次需要创建）
if [ ! -d "$XLOG_VENV" ]; then
    python3 -m venv "$XLOG_VENV"
    "$XLOG_VENV/bin/pip" install --quiet zstandard
fi

# 2. 对每个 .xlog 文件执行解码（默认使用 Python 3 版本）
DECODE_SCRIPT="$SKILL_DIR/decode_xlog.py"
for xlog_file in <discovered .xlog files>; do
    "$XLOG_VENV/bin/python" "$DECODE_SCRIPT" "$xlog_file"
    # 输出文件：${xlog_file}.log
done
```

**Python 3 版本解码结果异常时的回退流程：**

若使用 `decode_xlog.py` (Python 3) 解码后发现输出文件为空、内容为乱码、或解码报错，则回退到 Python 2.7 版本：

```bash
# 回退：使用 Python 2.7 版本
XLOG_VENV_PY2="$SKILL_DIR/.xlog_venv_py2"
DECODE_SCRIPT_PY2="$SKILL_DIR/decode_xlog_py2.py"

if [ ! -d "$XLOG_VENV_PY2" ]; then
    python2 -m virtualenv "$XLOG_VENV_PY2" || virtualenv -p python2.7 "$XLOG_VENV_PY2"
    "$XLOG_VENV_PY2/bin/pip" install zstandard
fi

for xlog_file in <failed .xlog files>; do
    "$XLOG_VENV_PY2/bin/python" "$DECODE_SCRIPT_PY2" "$xlog_file"
done
```

**处理规则：**

1. 默认使用 Python 3 版本 (`decode_xlog.py`) 解码
2. 解码成功后，使用生成的 `.xlog.log` 文件参与后续分析，原始 `.xlog` 文件不再需要
3. 若 Python 3 版本解码失败或输出异常（空文件/乱码），自动回退到 Python 2.7 版本 (`decode_xlog_py2.py`)
4. 两个版本均失败时记录错误并跳过该文件，不阻断整体分析流程
5. 加密的 xlog 文件（需要私钥解密）无法解码，报告"xlog 文件已加密，无法解码"
6. 若系统既无 `python3` 也无 `python2`，报告环境不支持 xlog 解码并跳过

### 1.3 Log Type Classification

根据文件名和内容特征自动分类：

| 日志类型 | 识别特征 | 典型信息 |
|---|---|---|
| **logcat** | `mm-dd HH:MM:SS.mmm PID TID LEVEL TAG:` 格式 | App/Framework 运行时日志 |
| **kernel (dmesg)** | `[    0.000000]` 时间戳格式 或 `<N>` 优先级前缀 | 内核启动、驱动、硬件事件 |
| **bugreport** | 含 `== dumpstate:` 或 `DUMP OF SERVICE` 段落 | 系统全量快照 |
| **tombstone** | `*** *** *** *** *** *** ***` + `Build fingerprint:` | Native crash |
| **ANR traces** | `"main" prio=` + `----- pid \d+ -----` | ANR 堆栈 |
| **pstore/ramoops** | `console-ramoops-*` 或 `last_kmsg` 文件名 | 上次崩溃前的内核日志 |
| **crashdump** | minidump/fulldump/memorydump 文件名或头部魔数 | 全系统崩溃 |
| **dumpsys** | `DUMP OF SERVICE <service_name>` | 系统服务状态快照 |
| **xlog** | `.xlog` 扩展名，二进制格式，需经 Phase 1.2 解码后分析 | App 层运行日志（微信 Mars/xlog 框架） |
| **私有日志** | 非标准格式 | 厂商自定义日志 |

对无法识别的文件，尝试读取前 50 行推断格式；仍无法识别则标记为"未知类型"并跳过。

### 1.4 Timestamp Awareness

**日志时间戳不完全可信**（用户可修改系统时间）。处理原则：

1. 以各日志内部的**相对时间序**为准，不盲信绝对时间
2. 同一份日志内，若出现时间回跳，标记为"疑似时间调整"
3. 跨日志文件对齐时，优先使用 kernel uptime（`[秒.微秒]`）作为锚点
4. bugreport 中的 `== dumpstate: <timestamp>` 可作为采集基准时间参考

---

## Phase 2: Log Parsing & Event Extraction

### 2.1 Time Range Filtering

用户提供时间范围时：

1. 仅提取该范围内的日志条目进行详细分析
2. 范围边界 ±30 秒的上下文也纳入参考
3. 无时间范围时分析全部日志，但优先聚焦异常密集区段

### 2.2 Anomaly Pattern Detection

按优先级从高到低扫描以下模式：

**P0 — 致命异常**

| Pattern | 类别 | 说明 |
|---|---|---|
| `FATAL EXCEPTION` / `AndroidRuntime: FATAL` | Java Crash | App/System 进程 Java 崩溃 |
| tombstone 文件存在 | Native Crash | signal (SIGSEGV, SIGABRT, SIGBUS 等) |
| `Kernel panic` / `Unable to handle kernel` | Kernel Panic | 内核崩溃 |
| `watchdog: BUG` / `SysRq : Trigger a crash` | Watchdog | 看门狗触发重启 |
| `ANR in` / `Input dispatching timed out` | ANR | 应用无响应 |
| pstore/ramoops 文件存在 | 异常重启 | 上次运行异常终止 |

**P1 — 严重异常**

| Pattern | 类别 |
|---|---|
| `E/ActivityManager: Force finishing` | 进程强杀 |
| `lowmemorykiller` / `oom_reaper` / `Out of memory` | 内存不足 |
| `WATCHDOG KILLING SYSTEM PROCESS` | System Server 重启 |
| `ShutdownThread: Rebooting` / `sys.powerctl` | 系统重启 |
| `E/SELinux: avc: denied` (大量) | SELinux 阻断 |
| `init: Service .* (pid .*) killed by signal` | Native 服务崩溃 |

**P2 — 值得注意**

| Pattern | 类别 |
|---|---|
| `W/` 级别日志密集出现 | 警告集中 |
| 长时间无 logcat 输出（gap > 5s） | 可能卡死/重启 |
| `screen_toggled` / `wakeup` / `suspend` | 亮灭屏/休眠唤醒 |
| `Binder: transaction failed` / `DeadObjectException` | Binder 通信异常 |
| `HEAT` / `thermal` / `throttling` | 温度异常 |
| `battery` + `voltage` + 异常值 | 电池异常 |

### 2.3 Event Timeline Reconstruction

将解析出的事件按时间排序，构建时空链：

```
HH:MM:SS.mmm  [类别]  事件摘要  (来源日志:行号)
```

例如：

```
14:30:01.234  [BOOT]      Kernel started, uptime=0          (dmesg:1)
14:30:15.678  [BOOT]      Zygote started                    (logcat:523)
14:30:18.901  [BOOT]      SystemServer ready                (logcat:1024)
14:32:05.123  [ANR]       ANR in com.example.app            (logcat:3456)
14:32:05.123  [MEMORY]    lowmemorykiller: kill pid=2345    (dmesg:8901)
14:32:10.456  [CRASH]     FATAL EXCEPTION in com.example    (logcat:3500)
```

---

## Phase 3: Analysis

### 3.1 Analysis Strategy

```
用户诉求判定
  ├─ 仅要求时空链 → Phase 2 时空链输出，列出异常发生情况，不分析原因
  ├─ 要求分析问题 → 先输出时空链，再进入深度分析
  └─ 有怀疑方向   → 优先验证怀疑方向
      ├─ 怀疑方向成立   → 围绕该方向深入分析
      └─ 怀疑方向不成立/不完整 → 降低其优先级，扩展到其他方向
```

### 3.2 Anomaly Correlation

将检测到的异常事件进行关联分析：

1. **时间关联**：短时间窗口内（±5s）的多个异常通常有因果关系
2. **进程关联**：同一 PID/UID 的多个异常串联
3. **模块关联**：同一子系统（如 Camera、Audio、Display）的异常归组
4. **因果链推断**：例如 OOM → kill → crash → ANR 的级联效应

### 3.3 Source Code Explanation (源码级解释)

对每个核心异常，**必须给出源码级解释**，说明异常在 AOSP/Kernel 源码中的触发路径和机制。根据当前环境分两种模式：

#### 3.3.1 源码模式（工作目录为源码树）

1. 根据日志 TAG 和类名定位源码文件
2. 根据用户提示的模块/位置查看相关代码逻辑
3. 阅读源码，解释异常的触发条件、调用路径和关键判断逻辑
4. 引用具体源码文件路径和关键函数/行号

```bash
# 通过 TAG 定位源码
grep -rn "TAG.*=.*\"<LogTag>\"" --include="*.java" --include="*.kt" --include="*.cpp"

# 通过异常类/方法名定位
grep -rn "<ClassName>\|<MethodName>" --include="*.java" --include="*.cpp"
```

**不主动大范围搜索源码**，仅根据日志线索和用户提示做定点查找。

#### 3.3.2 纯日志模式（无源码树）

即使没有源码，仍需基于 AOSP 公开源码知识给出源码级解释：

1. 根据异常日志中的 TAG、类名、方法名，说明其对应的 AOSP 源码模块和文件路径
2. 解释该处代码的核心逻辑——为什么会打印这条日志、触发条件是什么
3. 说明异常从触发到最终表现的调用链路（例如：`ActivityManagerService.appNotResponding()` → `ProcessRecord.kill()` → `SIGKILL`）
4. 引用 AOSP 中的文件路径和函数名作为参考（如 `frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java`）

**示例**：

```
异常: "lowmemorykiller: Kill pid=2345 (com.example.app)"
源码解释:
  - 源码位置: drivers/staging/android/lowmemorykiller.c (旧版) 或 lmkd (新版在 system/memory/lmkd/)
  - 触发逻辑: 当系统可用内存低于 minfree 阈值时，lmk 按 oom_adj_score 从高到低选择
    进程进行回收。被杀进程的 oom_adj_score 越高（越不重要），越先被选中
  - 调用链: memory pressure → kswapd → shrinker → lowmemorykiller/lmkd → kill(pid, SIGKILL)
```

### 3.4 Anomaly Layer Classification (异常层级归属)

对每个核心异常，**必须标注其所属层级**，帮助定位问题责任方和排查方向。

#### 层级定义

| 层级 | 说明 | 典型表现 |
|---|---|---|
| **第三方应用** | 第三方 APK 自身的问题 | 第三方包名的 Crash/ANR、第三方 SDK 异常 |
| **App** | 系统内置应用（非 framework）的问题 | SystemUI/Launcher/Settings 等系统应用的崩溃 |
| **Framework/Service** | Android Framework 层服务问题 | AMS/WMS/PMS 等系统服务异常、Binder 通信故障 |
| **HAL** | 硬件抽象层问题 | Camera HAL/Audio HAL/Sensor HAL 崩溃或超时 |
| **Kernel** | Linux 内核问题 | Kernel panic、驱动崩溃、调度异常、文件系统错误 |
| **硬件** | 硬件故障或异常 | ECC 错误、thermal shutdown、电压异常、存储坏块 |

#### 领域标签（可叠加）

层级之外，还需标注问题的功能领域（可多选）：

| 领域 | 典型表现 |
|---|---|
| **性能** | 卡顿、掉帧、CPU/IO 占用高、调度延迟 |
| **内存** | OOM、内存泄漏、lowmemorykiller 频繁触发 |
| **网络** | 断网、DNS 失败、Socket 超时、Wi-Fi/移动数据切换异常 |
| **电源** | 异常耗电、唤醒锁滥用、充电异常、无法休眠 |
| **显示** | 花屏、闪屏、黑屏、合成失败、帧率异常 |
| **音频** | 无声、杂音、AudioFlinger 异常、音频焦点抢占 |
| **存储** | I/O 错误、文件系统损坏、空间不足 |
| **安全** | SELinux 拦截、权限不足、证书/签名问题 |
| **稳定性** | 反复崩溃、看门狗重启、系统服务循环重启 |

#### 归属判定原则

1. **就近原则**：异常直接发生在哪一层，首先归属到该层
2. **穿透追溯**：若底层问题导致上层表现（如 Kernel 驱动 bug 导致 HAL 崩溃），同时标注表现层和根因层
3. **多层关联**：复杂问题可标注多个层级，但必须区分"表现层"和"根因层"

### 3.5 Crash-Specific Analysis

#### Java Crash
1. 提取完整异常堆栈（Exception type + message + stack trace）
2. 定位 `Caused by` 根因
3. 关联进程名、PID、所在前台/后台状态

#### Native Crash (Tombstone)
1. 提取 signal 类型（SIGSEGV/SIGABRT 等）和 fault addr
2. 提取 backtrace，定位崩溃函数
3. 检查是否为已知模式（空指针、栈溢出、use-after-free）

#### Kernel Panic / Pstore
1. 提取 panic 调用栈
2. 检查 last_kmsg / console-ramoops 中 panic 前的最后输出
3. 关联可能的硬件事件（thermal、电压异常等）

#### ANR
1. 提取 ANR 进程和触发原因（Input dispatching / Broadcast / Service）
2. 分析 traces.txt 中主线程堆栈（阻塞在锁/IO/Binder？）
3. 关联同时段系统资源状况（CPU、IO、内存）

### 3.6 Troubleshooting Guidance (概率性/兼容性故障排障)

当分析结论指向**概率性故障**（偶发、难以稳定复现）或**兼容性问题**（特定设备/版本/App 组合下出现）时，尝试给出缩小问题范围的排障方法。

#### 适用判定

```
分析结论判定
  ├─ 问题有明确根因且可稳定复现 → 跳过本节，直接给出修复建议
  └─ 问题为概率性 / 兼容性 / 根因不完全明确
      ├─ 日志中有足够线索可缩小范围 → 输出排障方法
      └─ 日志信息不足，无法有效缩小范围 → 跳过本节，在报告中注明"日志信息不足以进一步缩小范围"
```

#### 排障方法输出要求

给出的排障方法应具备可操作性，可包含以下类型：

| 排障类型 | 说明 | 示例 |
|---|---|---|
| **环境隔离** | 改变运行环境以排除外部因素 | 更换网络环境、更换充电器、调整环境温度 |
| **版本对比** | 通过版本切换定位引入点 | 回退到上一版本验证、对比不同 ROM 版本 |
| **模块隔离** | 逐步禁用/替换模块以定位故障模块 | 安全模式启动排除第三方 App、禁用特定 HAL 模块 |
| **日志增强** | 增加日志级别或开启调试选项以获取更多信息 | 开启 verbose 日志、启用特定 TAG 的 debug 输出 |
| **压力测试** | 通过压力测试提高复现概率 | monkey 测试、循环执行触发操作、内存压力测试 |
| **硬件排查** | 排除硬件单体问题 | 更换同型号设备对比、运行硬件自检工具 |

**注意**：排障方法应尽量简洁（3-5 步），面向有一定技术能力的工程师，而非终端用户。

### 3.7 After-Sales Assessment (售后问题判定与处理建议)

当输入内容可识别为**用户报告的售后问题**（如包含用户现象描述、客诉记录、售后工单信息等）时，结合分析结论给出售后处理建议和客服话术。

#### 适用判定

```
输入内容判定
  ├─ 纯技术分析请求（工程师自查、开发调试） → 跳过本节
  └─ 可识别为售后问题（含用户反馈/客诉/售后工单特征）
      └─ 输出售后处理建议 + 客服话术
```

识别特征包括但不限于：用户描述的使用场景和现象、"客户反馈"/"用户投诉"/"售后"等关键词、工单编号、用户操作步骤描述等。

#### 售后问题分类

对分析出的问题进行**售后维度的分类**（与技术层级归属不同，面向责任判定和处理流程）：

| 问题分类 | 说明 | 典型场景 |
|---|---|---|
| **产品软件设计问题/BUG** | 我方产品软件的设计缺陷或 BUG | 系统服务逻辑错误、ROM 功能缺陷、OTA 升级导致的回归问题 |
| **产品硬件设计问题/BUG** | 我方产品硬件方案的设计缺陷 | 天线设计导致信号差、散热设计不足导致降频、电源管理电路设计缺陷 |
| **硬件单体不良** | 个别设备的硬件元器件故障 | DDR/eMMC 芯片不良、按键损坏或挤压导致频繁误触、屏幕排线虚焊、传感器失灵 |
| **性能问题** | 设备性能不满足用户预期 | 运行卡顿、App 启动慢、存储读写慢（非故障，属性能瓶颈） |
| **使用环境问题** | 用户使用环境导致的异常表现 | 高温/低温环境、网络信号弱的区域、电池老化或低电量、强电磁干扰 |
| **第三方软件问题** | 第三方 App 或服务导致的问题 | 第三方 App 崩溃/ANR、第三方 SDK 兼容性问题、第三方云服务异常 |
| **第三方硬件/设施问题** | 用户侧的外部硬件或基础设施问题 | 路由器故障、运营商网络问题、充电线/充电头不兼容、蓝牙外设兼容性 |
| **网络波动/故障** | 网络环境自身的异常 | DNS 解析异常、网络信号差/速度慢、目标网址不可达、运营商网络拥塞 |
| **非问题（误报）** | 实际并非问题，用户理解偏差 | 用户操作错误、对正常现象的误解（如正常发热被认为异常）、功能设计如此但用户预期不同 |

#### 分类判定原则

1. **证据优先**：分类必须有日志证据支撑，不凭猜测
2. **多因素时取主因**：多个因素共同导致时，以主要责任方为分类依据，次要因素在说明中注明
3. **不确定时标注**：证据不足以明确分类时，列出最可能的 2-3 个分类并说明各自的可能性依据
4. **区分根因与触发**：如"第三方 App 内存泄漏导致系统 OOM"，分类为"第三方软件问题"而非"产品软件问题"

#### 售后处理建议

根据问题分类给出对应的处理建议：

| 问题分类 | 处理方向 |
|---|---|
| 产品软件问题/BUG | 记录并转研发，告知用户后续版本修复计划 |
| 产品硬件设计问题 | 记录并转硬件团队评估，视严重程度决定是否召回/补偿 |
| 硬件单体不良 | 走售后换货/维修流程 |
| 性能问题 | 提供优化建议，必要时说明设备性能定位 |
| 使用环境问题 | 引导用户改善使用环境，提供相关建议 |
| 第三方软件问题 | 引导用户联系第三方或提供替代方案 |
| 第三方硬件/设施问题 | 引导用户排查外部设备，提供兼容设备建议 |
| 网络波动/故障 | 引导用户排查网络环境，建议联系运营商 |
| 非问题（误报） | 耐心解释正常行为，提供正确操作指引 |

#### 客服话术要求

话术需满足以下原则：

1. **通俗易懂**：避免技术术语，用用户能理解的语言
2. **态度专业友善**：体现对用户问题的重视和理解
3. **结论明确**：清晰传达问题原因和处理方案
4. **不推诿**：即使是非我方问题，也应提供有建设性的建议
5. **有后续动作**：每段话术应包含下一步操作指引

---

## Phase 4: Output Generation

### 4.1 Output File

**必须将分析结果写入 `.md` 文件**：

```bash
# 命名格式：LogAssistent_YYMMDD_序号.md
# 序号从 01 开始，同一天内递增
OUTPUT_FILE="LogAssistent_$(date +%y%m%d)_01.md"

# 若同名文件已存在，递增序号
SEQ=1
while [ -f "LogAssistent_$(date +%y%m%d)_$(printf '%02d' $SEQ).md" ]; do
    SEQ=$((SEQ + 1))
done
OUTPUT_FILE="LogAssistent_$(date +%y%m%d)_$(printf '%02d' $SEQ).md"
```

文件保存在 agent 当前工作目录下。

### 4.2 Report Template

```markdown
# Android 日志分析报告

**日志路径**: <path>
**分析时间**: <YYYY-MM-DD HH:MM>
**时间范围**: <用户指定范围 或 "全量">
**分析模式**: <纯日志模式 / 源码辅助模式>

---

## 1. 日志概览

| 日志类型 | 文件名 | 时间跨度 | 条目数/大小 |
|---|---|---|---|

## 2. 时空链条（事件流水账）

按时间顺序列出关键事件，每条包含：
- 事件描述
- 日志时间
- 关键日志（1-5 行原文）

### HH:MM:SS — <事件类别>: <事件摘要>

**时间**: <日志时间戳>
**描述**: <发生了什么>
**关键日志**:
> <1-5 行原始日志>

---
(重复以上结构)

## 3. 异常总结

| # | 时间 | 类别 | 摘要 | 严重级别 | 所属层级 | 领域标签 |
|---|---|---|---|---|---|---|

## 4. 问题分析（仅在用户要求分析时输出）

### 4.1 用户怀疑方向验证
（若用户提供了怀疑方向）
- 验证结论：<成立/不成立/部分成立>
- 依据：<日志证据>

### 4.2 根因分析

**问题现象**: <一句话描述>
**直接原因**: <日志证据指向的直接触发因素>
**根本原因**: <推断的底层原因>
**影响范围**: <受影响的进程/功能>
**表现层级**: <异常直接表现所在层级>
**根因层级**: <问题根本原因所在层级>
**领域标签**: <性能/内存/网络/电源/显示/音频/存储/安全/稳定性>

**证据链**:
1. <时间> <日志证据1>
2. <时间> <日志证据2>
...

### 4.3 源码级解释

针对每个核心异常，从源码角度解释其触发机制：

#### 异常 N: <异常摘要>

**相关源码位置**:
| 源码文件路径 | 关键函数/方法 | 相关日志 TAG |
|---|---|---|

**触发机制**:
- <该异常在源码中的触发条件和判断逻辑>
- <从哪个调用路径到达异常点>

**调用链路**:
```
<函数A>() → <函数B>() → ... → <异常打印/抛出点>()
```

**源码解读**:
<结合源码上下文，解释为什么在当前场景下触发了该异常。若为纯日志模式，基于 AOSP 公开源码知识给出等效解释>

---
（对每个核心异常重复以上结构）

## 5. 建议（可选）

- <排查/修复建议>

## 6. 排障指引（概率性/兼容性故障时输出，无法缩小范围时跳过）

**问题特征**: <概率性/兼容性/偶发等特征描述>
**当前定位程度**: <已确定的范围 和 尚不明确的部分>

### 排障步骤

| 步骤 | 操作 | 目的 | 预期结果判定 |
|---|---|---|---|
| 1 | <具体操作> | <排除什么因素> | <如果结果A则说明X，如果结果B则说明Y> |
| 2 | ... | ... | ... |

### 预期收敛方向

- 若步骤 N 结果为 A → 问题指向 <方向1>，建议进一步 <操作>
- 若步骤 N 结果为 B → 问题指向 <方向2>，建议进一步 <操作>

## 7. 售后处理建议（仅当识别为售后问题时输出）

### 7.1 问题分类

| 分类项 | 判定结果 |
|---|---|
| **问题分类** | <产品软件问题/产品硬件设计问题/硬件单体不良/性能问题/使用环境问题/第三方软件问题/第三方硬件设施问题/网络波动故障/非问题> |
| **分类依据** | <支持该分类的关键日志证据，1-2 句> |
| **置信度** | <高/中/低> |
| **备选分类** | <若置信度非"高"，列出其他可能分类及理由> |

### 7.2 处理建议

**建议处理方式**: <具体处理动作，如转研发/换货/引导用户操作等>
**处理优先级**: <紧急/一般/低>
**后续跟进**: <是否需要跟进，跟进什么内容>

### 7.3 客服参考话术

**场景**: <用户描述的问题现象>

**参考回复**:

> <面向客户的回复内容，通俗易懂，态度专业友善，包含：>
> 1. 对用户问题的确认和理解
> 2. 问题原因的简要说明（非技术语言）
> 3. 处理方案或下一步操作
> 4. 预期解决时间或后续跟进说明

**内部备注**（仅供客服人员参考，不对外）:
- 技术原因: <一句话技术摘要>
- 问题分类: <分类>
- 注意事项: <与客户沟通时需注意的要点>
```

### 4.3 Output Rules

1. **时空链条必须为流水账形式**：按时间顺序逐条展示，每条含"事件描述 + 日志时间 + 1-5行关键原始日志"
2. **异常总结与时空链分开**：时空链记录所有关键事件，异常总结仅聚焦问题
3. **异常总结必须包含层级归属**：每条异常必须标注"所属层级"和"领域标签"
4. **源码级解释必须输出**：对每个核心异常（P0/P1），必须在第 4.3 节给出源码级解释，包含源码位置、触发机制和调用链路；无源码树时基于 AOSP 公开源码知识给出等效解释
5. **仅总结 vs 总结+分析**：由用户诉求决定是否输出第 4 节
6. **不编造日志内容**：所有引用的日志行必须来自原始日志文件
7. **源码解释可基于知识**：源码级解释中的 AOSP 文件路径和函数名允许基于公开知识引用，但需标注"基于 AOSP 公开源码"以区别于实际源码树中的定点查找结果
8. **排障指引有条件输出**：仅当问题为概率性/兼容性故障且日志信息足以缩小范围时输出第 6 节；无法有效缩小范围时跳过并注明原因
9. **售后建议有条件输出**：仅当输入可识别为售后问题时输出第 7 节；纯技术分析请求不输出售后话术
10. **话术面向非技术人员**：第 7.3 节客服话术必须使用通俗语言，不含技术术语；技术细节仅放在"内部备注"中
11. **问题分类基于证据**：售后问题分类必须有日志证据支撑，不确定时列出多个可能分类及各自依据
12. 输出完成后在对话中告知用户文件路径，并附简要摘要

---

## Constraints

1. **日志为必须输入** — 无日志路径时立即索要，不猜测
2. **时间戳不完全可信** — 注意时间回跳和不连续
3. **不主动搜索源码** — 仅在工作目录为源码树时且有日志线索时定点查找
4. **不编造** — 所有引用的日志行、堆栈、时间戳必须来自原始日志
5. **大文件策略** — 日志文件过大时按时间范围或异常关键词抽取，不强行全文读取
6. **隐私意识** — 不在输出中暴露非必要的用户隐私信息（IMEI、手机号等）
7. **流水账格式** — 时空链和问题总结必须按流水账格式展示
8. **源码级解释必输出** — 对所有 P0/P1 核心异常必须给出源码级解释；有源码树时基于实际代码，无源码树时基于 AOSP 公开源码知识，并明确标注来源
9. **层级归属必标注** — 每个核心异常必须标注所属层级（第三方/App/Framework·Service/HAL/Kernel/硬件）和领域标签（性能/内存/网络等），复杂问题需区分表现层和根因层
10. **排障指引量力而行** — 概率性/兼容性故障尝试给出排障方法缩小范围；若日志信息不足以有效缩小范围则主动放弃，不硬凑
11. **售后分类与技术层级独立** — 售后问题分类（产品软件BUG/硬件单体不良/第三方问题/非问题等）是面向责任判定的业务分类，与技术层级归属互不替代
12. **话术不推诿** — 即使问题非我方原因，客服话术也应提供有建设性的引导和建议，不简单推脱

## Error Handling

| Scenario | Action |
|---|---|
| 日志路径不存在 | 报告路径无效，要求重新提供 |
| 日志文件为空 | 报告并跳过该文件 |
| 日志格式无法识别 | 标记"未知类型"，尝试按纯文本搜索关键异常模式 |
| 压缩文件解压失败 | 报告，跳过该文件 |
| 日志量极大（>500MB 单文件） | 按用户时间范围或异常关键词做分段读取 |
| 无明显异常 | 报告"未检测到明显异常"，仍输出时空链 |
| 源码目录不可达 | 降级为纯日志模式，不报错 |
| xlog 解码失败 | 报告解码错误原因（格式损坏/加密/依赖缺失），跳过该文件 |
| xlog 为加密格式 | 报告"xlog 已加密，需私钥解码"，跳过该文件 |
| 系统无 python3 | 报告无法创建 xlog 解码环境，跳过所有 .xlog 文件 |
