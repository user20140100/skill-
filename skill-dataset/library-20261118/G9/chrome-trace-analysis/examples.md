# 完整分析案例：内网白板应用卡死现场

> 本案例为一次真实分析的完整报告（report-2），展示报告模板如何被填充。重点示范：
> 1. **每秒 busy% 饱和区判读**——第 28s 起持续 95~100% 是"卡死"的直接证据（铁律 4）；
> 2. **跨 tid 合并误报的识别与排除**——`wasm-function[38]` 60.6s / `postMessage` 54.5s / `__emval` 5.7s 看似元凶，分 tid 后证实 Worker 全 idle（铁律 2）；
> 3. **X 事件 vs 采样对账**——`r` 回调 47.4s wall time 中 JS self 仅 0.75s，差值定位到 readPixels + three.js 矩阵计算 + WebGL 提交（铁律 3）；
> 4. **与案例 A（同体系、46% 繁忙）的对比写法**——说明同一根因在不同负载下从"高危"恶化为"卡死"。

---

# Web 站点性能日志深度分析报告（Trace-20260930T120554）

| 项目 | 说明 |
|------|------|
| 分析文件 | `Trace-20260930T120554.json.gz`（51.5 MB 压缩 / 508.5 MB 解压，2,112,780 条事件） |
| 站点 | `http://10.137.113.198/dts/app/`（内网 DTS 白板应用）+ `cisp-ops/1.13.0` + 3D 地图 `gis3d-library/media/1.14.33` |
| 录制时长 | 62.6 秒（有效窗口） |
| 问题现象 | 部分电脑设备上页面卡死、无法工作 |
| 分析方法 | Node.js 离线解析 trace 事件流（RunTask 任务树分解 + CPU Profile 分线程采样归因） |

---

## 结论摘要（TL;DR）

**本段日志就是"卡死"现场**：主线程整体繁忙率 **87.2%**，且从**第 28 秒起持续 95~100% 完全饱和直至录制结束**——主线程没有任何空隙处理用户输入，页面必然表现为"卡死无法工作"。

**元凶**与第一段日志（Trace-20260930T113352）同源：`dts/app` 白板应用（`231.4c9ff49f0b528e04bef5.js`）的 `r` 函数通过 requestAnimationFrame **每帧执行重负载回调**，独吞主线程 **47.4 秒（76%）**。其内部三大开销：three.js 场景图矩阵计算（~10-12s）、WebGL `readPixels` 每帧同步回读（5.7s）、WebGL 命令提交等 native 执行（6.9s）。

---

## 一、整体健康度指标

| 指标 | 数值 | 评估 |
|------|------|------|
| 主线程繁忙率 | **87.2%** | ⛔ 严重过载 |
| 主线程第 28s 后繁忙率 | **95~100% 持续 34 秒** | ⛔ 卡死状态 |
| 掉帧次数（DroppedFrame） | **115 次**（第 0 秒集中爆发 48 次） | ⛔ |
| RunTask 总数 / 总耗时 | 163,136 次 / 54,560 ms（62.6s 窗口） | — |
| 动画帧数 / rAF 回调数 | 3,654 帧 / 13,755 次（**每帧 ~3.8 个回调**） | ⚠️ 多循环并存 |
| >50ms 长任务 | 8 个（含 1 个 759ms 录制伪影），真实最长 **88.8ms**（TimerFire） | — |
| GC | MinorGC 235 次共 187ms；MajorGC 4 次共 109ms（max 38.3ms） | ✅ 占比 <1%，非瓶颈 |
| Layout / Paint | 503ms / 45ms | ✅ 非瓶颈 |

**主线程每秒繁忙率（CPU 采样，已剔除 idle）**：

```
 1s:85%  2s:77%  3s:82%  4s:74%  5s:72%  6s:73%  7s:70%  8s:70%  9s:69% 10s:75%
11s:74% 12s:81% 13s:76% 14s:69% 15s:76% 16s:84% 17s:88% 18s:80% 19s:70% 20s:81%
21s:72% 22s:71% 23s:70% 24s:68% 25s:64% 26s:66% 27s:68% | 28s:96% 29s:95% 30s:96%
31s:95% 32s:97% 33s:97% 34s:97% 35s:97% 36s:98% 37s:98% 38s:98% 39s:97% 40s:98%
41s:99% 42s:99% 43s:98% 44s:99% 45s:98% 46s:100% 47s:98% 48s:99% 49s:100% 50s:99%
51s:100% 52s:98% 53s:99% 54s:98% 55s:100% 56s:99% 57s:99% 58s:98% 59s:100% 60s:98%
```

> **竖线右侧（第 28 秒起）为完全饱和区**：主线程 95~100% 满载，输入事件无法被及时处理——这就是用户感知到"页面卡死"的直接证据。前 27 秒的 64~88% 也已处于高危区间（健康值应 <50%）。

**RunTask 时长分布**：

| 区间 | 次数 | 总耗时 | 说明 |
|------|------|--------|------|
| <8ms | 159,478 | 1,886ms | 零碎小任务 |
| 8~16ms | 2,886 | **36,465ms** | ⛔ 每帧 rAF 任务，帧均 12.6ms |
| 16~32ms | 752 | **14,527ms** | ⛔ 超帧预算任务，帧均 19.3ms |
| 32~50ms | 12 | 468ms | |
| 50~100ms | 7 | 455ms | 含 TimerFire 88.8ms |
| >100ms | 1 | 759ms | 录制伪影（见附录 B） |

---

## 二、问题 1：哪些任务非常耗费 CPU？

按真实耗时排序（已剔除录制伪影，详见附录 B）：

### 1. `r` 函数（rAF 每帧回调）—— 47.4 秒，占主线程 76% ⛔

- **来源**：`http://10.137.113.198/dts/app/asset/js/231.4c9ff49f0b528e04bef5.js`
- **调用次数**：17,497 次 FunctionCall（其中 **12,915 次为 rAF 回调**，3,654 帧 × 每帧 ~3.5 个）
- **单次耗时**：常态 ~3.7ms，最长 744.5ms（含 Profiler 启动伪影）
- **特征**：自身 JS 执行仅 0.75s，其余 46s+ 全部消耗在其调用的 native/渲染路径上（见下表对账）

**`r` 回调内部开销对账（X 事件 wall time vs CPU 采样）**：

| 构成 | 耗时 | 占主线程 | 性质 |
|------|------|----------|------|
| three.js 场景图矩阵计算 | ~10-12s | ~18% | `setFromRotationMatrix`/`decompose`/`copy`/`compose`/`multiplyMatrices`/`setFromEuler` 等 @ `1.14.33/index.js:5853` |
| WebGL `readPixels` | 5.67s | 9.1% | 每帧 ~1.55ms，GPU→CPU 同步回读 |
| (program) native 执行 | 6.9s | 11% | WebGL 命令提交、V8 内部等 |
| three.js 绘制提交 `R_.renderBufferDirect` | 0.8s | 1.3% | 实际 draw call |
| `r` 自身 JS | 0.75s | 1.2% | 业务逻辑 |
| performance.mark/measure | ~15.4s | — | **录制伪影，生产环境不存在** |

### 2. three.js 场景图每帧全量矩阵更新 —— ~10-12 秒（含于 r 内）⛔

- **来源**：`gis3d-library/media/1.14.33/index.js`（three.js 系 3D GIS 地图）
- 热点函数群：`setFromRotationMatrix` 1.63s、`v` 1.35s、`decompose` 1.19s、`copy` 1.09s、`compose` 0.68s、`multiplyMatrices` 0.68s、`setFromEuler` 0.72s、`Wt` 0.69s、`Br` 0.59s、`applyMatrix4` 0.31s…
- 这是典型的 **`updateMatrixWorld` 每帧对全场景节点做矩阵分解/合成**的开销——场景节点越多越慢，且每帧无条件执行

### 3. WebGL `readPixels` —— 5.7 秒（9.1%）⛔

- 每帧 ~1.55ms 的 GPU 同步回读（5,667ms ÷ 3,654 帧），在 r 回调路径内
- 不产生 timeline 事件，仅 CPU 采样可见（与第一段日志同一问题模式）

### 4. 其他（量小，非瓶颈）

| 项 | 耗时 | 说明 |
|----|------|------|
| 输入事件 | 384ms / 480 次 | click 单次 max 35.2ms |
| UpdateLayoutTree | 503ms / 3,953 次 | max 25.1ms |
| Commit（渲染提交） | 541ms / 3,643 次 | max 38.8ms（单次） |
| TimerFire | 207ms / 928 次 | **单次 max 88.8ms @第 4.2s**（启动期长任务） |
| RunMicrotasks | 349ms / 4,136 次 | max 38.6ms |
| GC | ~300ms | MinorGC 187ms + MajorGC 109ms |
| cisp-ops 主应用 JS | ~530ms | `main.2c1a3a40`/`react-base`/`18462` 等 |

---

## 三、问题 2：哪些任务最可能导致页面卡顿/卡死？

按危险度排序：

### ⛔ 危险度 1：每帧 3~4 个 rAF 回调的持续重负载（主线程饱和）

- 每帧 JS 执行 12.6~19.3ms（见 RunTask 分布），**已超过 60fps 的 16.7ms 帧预算**；主线程全程 87% 繁忙、第 28s 后 100% 饱和；
- 在性能更弱的设备上（低功耗 CPU 等效 2~4 倍降速），帧 JS 膨胀到 40~70ms → 任务无限积压 → **输入事件排队数秒，页面卡死**；
- 掉帧数据印证：第 0 秒爆发 48 次掉帧（启动期），28s 后持续散点掉帧。

### ⛔ 危险度 2：`readPixels` 每帧同步回读

- 强制 CPU 每帧阻塞等待 GPU 排空渲染管线，破坏 CPU/GPU 并行；
- 弱 GPU/集显设备上等待时间成倍放大——**设备越差惩罚越重**，是"只在部分电脑上卡死"的关键放大器。

### ⛔ 危险度 3：three.js 场景图每帧全量矩阵更新

- 场景节点矩阵分解/合成是纯 CPU 密集计算，节点规模 × 每帧执行 = 与场景复杂度正相关的持续负载；
- 低端 CPU 上该部分可膨胀至每帧 20ms+，单独即可击穿帧预算。

### ⚠️ 危险度 4：启动期长任务 + 掉帧爆发

- `TimerFire` 88.8ms（第 4.2s）、`v8.callFunction` 68.3ms（第 4.3s）、Commit 38.8ms 单次；
- 第 0 秒掉帧 48 次——启动阶段即明显卡顿，弱设备上启动期白屏/无响应时间更长。

### ✅ 已排除的嫌疑（避免误判方向）

| 嫌疑 | 证据 | 结论 |
|------|------|------|
| WASM `wasm-function[38]` 60.6s / `postMessage` 54.5s / `__emval` 5.7s | 分线程采样显示 2 个 WASM Worker 线程 ~100% idle | **跨线程 profile 合并的 node id 冲突误报**（见附录 A），无关 |
| dijkstra 寻路 Worker ×4 | 4 个 Worker 线程采样 ~100% idle（<0.5ms） | 空闲，无关 |
| GC 停顿 | 合计 ~300ms（占 0.5%），MajorGC max 38ms | 健康，无关 |
| Layout/Paint 抖动 | 合计 <550ms，JS 同步 Layout 259 次但单次小 | 非瓶颈 |
| 759ms 最长任务 | 内部为 `CpuProfiler::StartProfiling` 535ms+ | 录制伪影，非页面开销 |
| performance.mark ~15.4s | 901,723 条 UserTiming 事件全为 `cpu-started/cpu-duration` 采样标记 | 录制伪影，生产环境不存在 |

---

## 四、与第一段日志（Trace-20260930T113352）对比

| 维度 | Trace 1（云端 dws.seewo.com） | Trace 2（内网 10.137.113.198 dts/app） |
|------|------|------|
| 窗口 / 主线程繁忙率 | 21.1s / **46.1%** | 62.6s / **87.2%（28s 后 100%）** |
| 头号热点 | `r` @ 1604.js（7.2s，34%） | `r` @ 231.js（47.4s，76%） |
| readPixels | 2.2s（每帧 1.8ms） | 5.7s（每帧 1.55ms） |
| three.js 矩阵计算 | ~1.3s | **~10-12s（显著恶化）** |
| 每帧 rAF 回调数 | ~4.7 个 | ~3.5 个 |
| 状态判断 | 高危但未饱和 | **已卡死（28s 后完全饱和）** |

**结论**：两段日志是同一技术体系（dws 白板 + gis3d 3D 地图）在不同部署/场景下的表现。Trace 2 的 3D 场景明显更重（矩阵计算 10 倍于 Trace 1），主线程从"高危"恶化为"饱和卡死"。**根因一致：rAF 每帧重负载渲染循环 + readPixels 每帧同步 + 场景图每帧全量更新**。

---

## 五、优化建议（按预期收益排序）

### P0：消除每帧 `readPixels`

排查 `dts/app` 231.js 中 r 回调内 readPixels 的用途（拾取/取色/画面合成？），按需触发或 WebGL2 PBO + `fenceSync` 异步读回；亦可 OffscreenCanvas 移入 Worker。

### P0：three.js 场景图更新优化

- 静态节点设置 `matrixAutoUpdate = false`，避免每帧全量 `updateMatrixWorld`；
- 场景分层：仅对变化子树调用 `updateMatrixWorld(true)`；
- 精简节点数量（合并静态网格 `BufferGeometryUtils.mergeGeometries`、InstancedMesh 替代大量重复节点）。

### P1：按需渲染 / 限帧

- 内容无变化时跳过渲染（dirty flag），页面不可见时暂停 rAF；
- 多个 rAF 循环（每帧 ~3.5 个回调）合并为统一调度；
- 低端设备限帧 30fps（帧预算直接翻倍）。

### P2：低端设备降级

- 通过 `navigator.hardwareConcurrency`、`WEBGL_debug_renderer_info`、运行时帧率探测识别低端设备；
- 降级手段：关闭/延迟加载 3D GIS、降低渲染分辨率（`setPixelRatio`）、简化场景。

### P3：验证方式

本次数据含较重 Profiler 录制开销（mark/measure ~15.4s、AsyncTask 仪器化），优化效果以真实用户监控（RUM / Web-Vitals：INP、长任务率）为准。

---

## 附录 A：分析方法与产物

- 分析脚本：`analyze-trace.js`（本 skill scripts 目录，一次运行输出 12 章节）
- 关键方法：**ProfileChunk 必须按 tid 分组合并**——本段日志若跨线程合并，会把主线程的 readPixels/mark 等耗时错误归属为 WASM Worker 的 `wasm-function[38]`/`postMessage`/`__emval`（node id 冲突），得出"WASM 是元凶"的错误结论；分线程后证实 8 个 Worker/子线程全部 ~100% idle。
- X 事件 wall time 与 CPU 采样 self time 对账：差异即 native 调用（readPixels/WebGL 提交不产生 timeline 事件）。

## 附录 B：录制伪影清单（不应计入页面开销）

| 伪影 | 表现 |
|------|------|
| CpuProfiler::StartProfiling | 首个任务虚增 535ms+（"759ms 最长任务"即由此构成，发生于第 0.1s） |
| cpu-started / cpu-finished / cpu-duration | 901,723 条 UserTiming 事件，Profiler 采样标记 |
| performance.mark/measure 采样开销 | ~15.4s self time 的绝大部分 |
| v8::Debugger::AsyncTaskRun | 17,040 次，DevTools 异步栈仪器化开销 |
