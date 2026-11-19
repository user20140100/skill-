# 判读细则与陷阱清单

## 1. 录制伪影对照表（必须剔除，勿计入页面成本）

| 伪影 | 典型表现 | 真实案例 |
|------|----------|----------|
| `CpuProfiler::StartProfiling` | 录制首个 RunTask 虚增 500ms+，成为"最长任务" | 535.6ms / 744.6ms 两次出现 |
| `cpu-started` / `cpu-finished` / `cpu-duration` UserTiming | 数万~数十万条，带 `sampleTraceId` | 12.4 万条（21s）、72.9 万条（62s） |
| 采样中 `mark` / `measure` self time | 大头即 profiler 采样标记开销 | 1.5s（21s 窗口）、14.6s（62s 窗口） |
| `v8::Debugger::AsyncTaskRun` / `AsyncTaskScheduled` | 数千~数万次，DevTools 异步栈仪器化 | 8,433 / 17,040 次 |
| `V8.StackGuard`/`HandleInterrupts`/`InvokeApiInterruptCallbacks` 长切片 | 包裹 profiler 启动中断 | max 值 ≈ 首个任务时长 |

判读要点：最长任务若包含上述结构，剔除后取次长任务作为真实最大值。

## 2. CPU Profile 的 node id 冲突（最危险的误报源）

**机理**：每个被采样线程的 profile 使用独立 node id 空间；`ProfileChunk` 事件的 tid ≠ 被采样线程 tid（曾见主线程 tid=239288 的采样挂在 tid=329148 上，且该 tid 名为 "DedicatedWorker thread"）。跨 tid 合并时 `Map.set` 互相覆盖节点，idle 节点 id 被其他线程的业务函数覆盖。

**已验证的误报形态**（合并视图 → 分 tid 真相）：

| 合并视图虚假热点 | 分 tid 后真相 |
|------------------|---------------|
| `dijkstra` 17.1s、`self.onmessage` 32.1s | 4 个 dijkstra Worker 全部 ~100% idle（<0.5ms） |
| `wasm-function[38]` 60.6s、`postMessage` 54.5s、`__emval_call_void_method` 5.7s | 2 个 WASM Worker ~100% idle（<2ms） |

**防护**：只按 tid 分组合并；主线程 profile 用节点内容特征（含 `requestAnimationFrame`/`readPixels`）识别，勿信 tid 与线程名。

## 3. 判读标准

| 指标 | 健康 | 高危 | 卡死 |
|------|------|------|------|
| 主线程繁忙率（RunTask/窗口） | <50% | 50~85% | >85% |
| 每秒 busy%（采样，剔 idle） | 波动、有空窗 | 持续 60~90% | 持续 95~100% |
| 帧 JS（8~32ms 任务总耗时） | 零星 | 每秒 ~60 个 | 帧均 >16.7ms |
| 每帧 rAF 回调数 | 1 | 2~3 | ≥4 |
| 每帧 `readPixels` | 无 | 偶发 | 每帧（GPU 同步放大器） |
| MinorGC | 占比 <1% | — | 通常非根因 |

## 4. X 事件 vs CPU 采样对账法

- X 事件（`FunctionCall` 等）记录 wall time，含内部 native 调用；
- CPU 采样只记 JS 栈 self time，native 调用（`readPixels`/`texSubImage2D`/WebGL 提交/性能 API）显示为无 JS 父栈的独立节点；
- **对账**：某函数 X 事件 total 远大于其采样 self time 时，差值即 native 开销；在主线程 X 事件里找"unexplained self time 最大者"，即为 native 热点（如 readPixels）的调用方。

## 5. 高危模式清单（卡顿归因常用）

1. **每帧 readPixels**：强制 CPU 等 GPU 排空管线，破坏 CPU/GPU 并行；GPU 越弱等待越久 → "只在部分电脑卡死"的典型放大器。修复：按需触发 / WebGL2 PBO+fenceSync 异步读回 / OffscreenCanvas 移 Worker。
2. **多个 rAF 循环并存**：每帧 3~5 个回调，帧 JS 超 16.7ms 预算。修复：合并调度、dirty flag 按需渲染、不可见时暂停。
3. **three.js 场景图每帧全量更新**：`updateMatrixWorld` 引发 compose/decompose/multiplyMatrices 矩阵计算群，与节点数正相关。修复：静态节点 `matrixAutoUpdate=false`、分层更新、合并节点/InstancedMesh。
4. **每帧 texSubImage2D**：纹理全量上传，弱 GPU 带宽瓶颈。修复：局部更新/跳帧。
5. **持续 95~100% busy%**：主线程饱和，输入事件排队 → 用户感知"卡死无法工作"。

## 6. 真实案例参考（两次验证过的分析）

| 维度 | 案例 A（云端编辑器） | 案例 B（内网白板应用） |
|------|---------------------|------------------------|
| 窗口 / 繁忙率 | 21.1s / 46.1%（高危） | 62.6s / 87.2%，28s 后 95~100%（卡死现场） |
| 头号热点 | `r` @ 1604.js rAF 回调 7.2s（34%） | `r` @ 231.js rAF 回调 47.4s（76%） |
| readPixels | 2.2s（每帧 1.8ms） | 5.7s（每帧 1.55ms） |
| three.js 矩阵计算 | ~1.3s | ~10-12s |
| 掉帧 | 169 次 | 115 次（第 0s 爆发 48 次） |
| 结论 | 高危未饱和 | 持续饱和 = 卡死 |

## 7. 工程注意事项

- 大 JSON：`--max-old-space-size=12288`；禁止 `Math.max(...大数组)`（栈溢出），用循环。
- trace 内可能混有 ts≈0 的元事件：录制窗口用主线程 RunTask 的 min/max，勿用全事件。
- PowerShell `>` 重定向会把 Node UTF-8 输出按 GBK 误码转存 UTF-16（中文乱码）：用 `cmd /c` 重定向，或 spawn 捕获 stdout。
- Windows 打印 PDF：Edge/Chrome headless `--print-to-pdf`；验证 `%PDF` 头 + `%%EOF` 尾。
