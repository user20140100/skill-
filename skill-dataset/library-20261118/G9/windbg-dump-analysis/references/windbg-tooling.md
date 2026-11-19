# WinDbg 工具与命令

> Step 1 / Step 3 的参考。MCP 工具用法 + CDB CLI 兜底 + 常用命令速查 + 活进程打断流程。

## MCP 工具（mcp-windbg v0.15.0）

会话内已加载 `mcp_windbg` 时用这些工具。优势：保持会话打开，多命令交互；支持活进程 remote。

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `list_windbg_dumps` | 列出 dump 文件 | 目录路径，用于批量发现 |
| `open_windbg_dump` | 打开 dump 分析 | `path`（dump 文件路径） |
| `close_windbg_dump` | 关闭 dump 会话 | session id — **必须调用** |
| `open_windbg_remote` | 连接 / 附加活进程 | 连接串如 `tcp:Port=5005,Server=...` 或本地 pid |
| `close_windbg_remote` | 关闭远程会话 | session id — **必须调用** |
| `run_windbg_cmd` | 执行 WinDbg / CDB 命令 | `session` + `command` |
| `send_ctrl_break` | 中断运行中目标 | 活进程挂起分析时打断取快照 |

### 崩溃 dump 典型序列

```
1. open_windbg_dump(path="C:\\dumps\\app.dmp")        → session
2. run_windbg_cmd(session, "!analyze -v")             → 自动分析
3. run_windbg_cmd(session, "k")                       → 当前线程栈
4. run_windbg_cmd(session, "~*k")                     → 所有线程栈
5. close_windbg_dump(session)                         → 清理（必须）
```

### 活进程挂起典型序列

```
1. open_windbg_remote(connection="...或 pid")         → session（附加活进程）
2. send_ctrl_break(session)                           → 打断目标，进入调试器
3. run_windbg_cmd(session, "~*k")                     → 所有线程栈
4. run_windbg_cmd(session, "!locks")                  → 锁状态找 owner
5. run_windbg_cmd(session, "!runaway")                → 区分 busy vs idle
6. close_windbg_remote(session)                       → 清理（必须， detach 目标进程）
```

## CDB CLI 兜底

MCP 未就绪时用。每次是独立 CDB 进程。

### 崩溃 dump 分析

```bash
cdb -z <dump> -c "<commands>; q" \
    -y "srv*C:\Symbols*https://msdl.microsoft.com/download/symbols;<project_pdb>" \
    -i <image_path>
```

- `-z <dump>` — dump 文件路径
- `-c "<cmds>; q"` — 执行命令后 `q` 退出（必须，否则 CDB 挂住）
- `-y <symbols>` — 符号路径
- `-i <image_path>` — 二进制镜像路径

### 活进程附加（挂起分析）

```bash
# 附加活进程，打断后执行命令再 detach
cdb -p <pid> -c "~*k; !locks; !runaway; qd" \
    -y "srv*C:\Symbols*https://msdl.microsoft.com/download/symbols;<project_pdb>"
```

- `-p <pid>` — 附加到进程
- `qd` — quit detach（退出并 detach，让目标进程继续运行）

⚠️ 附加会暂停目标进程。生产环境慎用，detach 前进程处于冻结状态。

### 取活进程 dump（不进交互）

无 mcp-windbg remote 时，用 procdump 或 CDB 把活进程快照存成 dump 再分析：

```bash
# procdump（推荐，简洁）
procdump -ma <pid> C:\dumps\hang.dmp

# 或 CDB 附加后生成 dump 再 detach
cdb -p <pid> -c ".dump /ma C:\dumps\hang.dmp; qd"
```

`/ma` = full dump（含完整内存，挂起分析推荐）。零依赖兜底：Task Manager → 进程右键 → "创建转储文件"。

### 交互模式（复杂多步分析）

不加 `-c` 进入交互：

```bash
cdb -z C:/dumps/app.dmp -y "..." -i "..."
# 或附加活进程
cdb -p <pid> -y "..."
# 逐条输入命令，最后 q（dump）或 qd（活进程 detach）
```

## 常用命令速查

### 通用

| 命令 | 用途 |
|------|------|
| `!analyze -v` | 自动崩溃分析（崩溃首选起点） |
| `k` / `kv` / `kn` | 当前线程栈（kv 带参数，kn 带帧号） |
| `~*k` | 所有线程栈（挂起分析核心命令） |
| `~Ns` | 切到第 N 线程（如 `~0s`） |
| `r` | 寄存器 |
| `dt <type>` | 显示结构体定义 |
| `lm` / `lm m <mod>` | 列模块 / 过滤模块 |
| `!lmi <mod>` | 模块详情（FileVersion / PDB GUID）— 版本定位用 |
| `q` / `qd` | 退出（dump）/ 退出并 detach（活进程） |

### 崩溃专用

| 命令 | 用途 |
|------|------|
| `.ecxr` | 切到异常发生时上下文（访问违规后必用） |
| `.exr -1` | 显示异常记录（C++ 异常 / terminate 看 exception object） |
| `!heap -p -a <addr>` | 查地址所属堆块 |
| `!heap -s` / `!heap -stat` | 堆汇总 / 统计 |
| `!peb` | 进程环境块 |
| `bp` / `bl` / `bc <n>` | 设断点 / 列断点 / 清断点 |

### 挂起 / 死锁专用

| 命令 | 用途 |
|------|------|
| `~*k` | 所有线程栈，找等待 / 阻塞状态 |
| `!locks` | 所有临界区锁及 owner（找死锁环） |
| `!cs` | 临界区详情（含 lock count / owning thread） |
| `!runaway` | 各线程 CPU 时间（区分 busy 死循环 vs idle 死锁） |
| `!handle` | 句柄统计（资源耗尽排查） |
| `!cs -l` | 列出有争议的临界区 |

## 按场景命令组合

### 崩溃分析（起点）

```
!analyze -v; k; ~*k
```

### 访问违规（access violation, 0xC0000005）

```
!analyze -v; .ecxr; k; !heap -p -a <faulting_addr>
```

`.ecxr` 切到异常上下文后再 `k`，栈才有意义。看 faulting address：`0` = 空指针 / freed 地址 = UAF / 小偏移 = 结构体成员越界。

### 堆破坏（0xC0000374）

```
!analyze -v; k
```

⚠️ 堆破坏的崩溃点通常**不是**破坏点。需用 PageHeap 复现定位真正的破坏点：

```bash
# 启用 PageHeap（需 gflags，Debugging Tools 自带）
gflags /p /enable <process>.exe /full
# 复现后崩溃点即破坏点
```

### 栈溢出（0xC00000FD）

```
!analyze -v; k
```

看栈深度，找无限递归 / 栈上大对象。

### C++ 异常 / terminate

```
!analyze -v; .exr -1; k
```

`.exr -1` 显示异常对象类型。terminate → abort 的栈，找哪个线程抛了未捕获异常，检查边界 catch。

### 死锁排查

```
~*k; !locks; ~Ns; k
```

1. `~*k` 看所有线程，找 `WaitForSingleObject` / `EnterCriticalSection` 等待状态
2. `!locks` 看每把锁的 owner thread
3. 构造"线程 T1 等锁 L2，锁 L2 被 T2 持有；T2 等锁 L1，L1 被 T1 持有"的等待图，找环 = 死锁
4. `~Ns` 切到死锁线程，`k` 看它在等什么

### 死循环 vs 死锁区分

```
!runaway
```

- CPU 时间高的线程 = busy = 死循环 / 活锁
- 全部 idle = 死锁 / 阻塞

### 资源耗尽

```
!handle; !heap -s; !peb
```

句柄 / 堆 / 内存耗尽排查。

## 输出解读要点

- `!analyze -v` 的 `FAULTING_THREAD` / `EXCEPTION_RECORD` / `MODULE_NAME` 是核心
- 栈帧带行号（如 `my_module.cpp:128`）= 符号已对齐；只有地址 = 符号缺失 → 检查 `_NT_SYMBOL_PATH` 和版本对齐
- `MODULE_NAME` 指出崩溃模块，配合 `!lmi` 拿版本做版本定位（见 [`version-pinning.md`](version-pinning.md)）
- 死锁分析：`!locks` 输出每把锁的 `OwningThread`，对照 `~*k` 找出谁等谁
