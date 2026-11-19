# Native Crash 通用分析模式

## 适用平台
通用

## 问题现象
应用或系统服务发生 native 层崩溃，用户表现为应用闪退或系统重启。

## 典型日志特征

### tombstone 识别
```
signal 6 (SIGABRT), code -6 (SI_TKILL), fault addr --------
signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0
signal 7 (SIGBUS), code 2 (BUS_ADRERR), fault addr 0x7xxx
```

### 关键信息提取点
- **signal 类型**：SIGABRT(6) = 主动abort、SIGSEGV(11) = 内存非法访问、SIGBUS(7) = 总线错误
- **fault addr**：0x0 通常为空指针、有效地址附近可能是越界或 use-after-free
- **backtrace**：从 #00 开始逐帧分析，最顶部的用户空间帧是 crash 点
- **Abort message**：如果存在，通常是 abort() 时传入的错误信息

## 根因分类

| Signal | 常见原因 | 排查方向 |
|--------|----------|----------|
| SIGABRT | assert 失败、abort() 调用 | 查看 abort message |
| SIGSEGV | 空指针、越界、use-after-free | backtrace + 源码对照 |
| SIGBUS | 内存对齐、mmap 失败 | 硬件访问或 DMA 相关 |
| SIGFPE | 除零、整数溢出 | 数学运算代码 |

## 解决方案

1. 从 tombstone 中提取 crash 进程名和 backtrace
2. 使用 `addr2line` 或 `llvm-symbolizer` 将 PC 地址还原为源码位置
3. 结合源码分析 crash 点的上下文逻辑
4. 检查是否有并发访问、生命周期管理等常见问题

## 关联信息
- tombstone 文件路径：`/data/tombstones/`
- symbols 目录需要与固件版本匹配
