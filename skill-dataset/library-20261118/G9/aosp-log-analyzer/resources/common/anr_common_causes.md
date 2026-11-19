# ANR 通用分析模式

## 适用平台
通用

## 问题现象
应用无响应，用户看到"应用未响应"弹窗，或系统日志中出现 ANR 记录。

## 典型日志特征

### logcat 中 ANR 标识
```
ANR in [package_name]
Reason: [reason]
PID: [pid]
```

### 常见 ANR 原因关键词
- `input dispatching timed out` — 输入事件处理超时（默认 5s）
- `executing service [service_name]` — Service 执行超时（前台 10s / 后台 200s）
- `Broadcast of Intent` — 广播处理超时（前台 10s / 后台 60s）
- `ContentProvider not responding` — ContentProvider 超时

## 分析方法

### 1. 从 traces.txt 提取信息
```
DALVIK THREADS:
"main" prio=5 tid=1 TIMED_WAIT
  at java.lang.Object.wait(Native Method)
  at com.xxx.xxx.xxx.method(File.java:123)
```

### 2. 关键分析维度
- **主线程状态**：WAIT / BLOCKED / RUNNABLE — 确定主线程卡在哪里
- **锁信息**：`- waiting to lock <0x...>` — 找到锁持有者
- **调用栈深度**：过深的调用栈可能表示递归或设计问题

### 3. 时序关联
- ANR 时刻前后其他进程的 activity
- 系统资源状态（CPU、内存、IO）

## 常见根因模式

| 模式 | 特征 | 解决方向 |
|------|------|----------|
| 主线程 IO | 主线程在文件/数据库操作 | 移到子线程 |
| 主线程网络 | 主线程有网络调用 | 使用异步网络库 |
| 锁竞争 | `waiting to lock` / `BLOCKED` | 减小锁粒度，避免嵌套 |
| Binder 超时 | 主线程在 Binder 调用上等待 | 检查对端服务性能 |
| 资源等待 | CPU 高负载 / 内存不足 | 优化资源使用 |

## 解决方案
1. 获取 ANR 时的 traces 文件
2. 定位主线程阻塞点
3. 分析阻塞原因（IO/锁/网络等）
4. 将耗时操作移出主线程

## 关联信息
- ANR traces 路径：`/data/anr/traces.txt`
- 可通过 `adb pull /data/anr/traces.txt` 获取
