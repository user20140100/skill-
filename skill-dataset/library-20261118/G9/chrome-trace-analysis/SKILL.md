---
name: chrome-trace-analysis
description: >-
  深度分析 Chrome DevTools Performance 录制文件（.json / .json.gz），定位 CPU 热点与页面卡顿/卡死根因。涵盖
  gunzip 解压、最忙渲染主线程识别、RunTask 任务树分解、长任务拆解、按 tid 分组的 CPU 采样归因（防止跨线程 node id 冲突把
  WASM/Worker 误判为热点）、录制伪影剔除（CpuProfiler 启动开销、cpu-started/cpu-duration UserTiming
  采样标记、AsyncTaskRun 仪器化）、X 事件与 CPU 采样对账定位 native 调用（readPixels/texSubImage2D）、每秒
  busy% 饱和度判定，以及 Markdown + PDF 报告生成。当用户提供 Performance 录制/trace
  文件（Trace-*.json、*.json.gz）或要求分析页面性能、CPU 占用、长任务、掉帧、页面卡顿/卡死时使用。
author: zhangkai13699
version: 0.0.3
---

# Chrome Performance Trace 深度分析

从 DevTools Performance 录制文件中定位 CPU 热点与卡顿根因，输出结论可执行的报告。

## 工作流程

```
Task Progress:
- [ ] 0. 引导用户录制并导出 trace (若用户尚未提供文件)
- [ ] 1. 解压 trace (.gz → .json)
- [ ] 2. 运行 analyze-trace.js 全量分析
- [ ] 3. 按"判读铁律"剔除伪影、识别误报
- [ ] 4. 撰写 Markdown 报告
- [ ] 5. 生成 PDF (可选)
```

### Step 0: 录制与导出（用户尚未提供 trace 文件时，发此引导）

1. Chrome 打开目标页面 → 按 `F12` 打开 DevTools → 切换到 **Performance（性能）** 面板；
2. 点击左上角 **● Record**（或 `Ctrl+E`）开始录制，正常操作页面**复现卡顿场景**，建议 10~30 秒；
3. 点击 **Stop** 停止，等待火焰图加载完成；
4. 点击面板左上角 **Save profile（⬇ 下载图标）** 导出，得到 `Trace-YYYYMMDDTHHMMSS.json.gz`（旧版 Chrome 导出为 `.json`）；
5. 把文件路径发给 agent 即可，`.gz` 无需手动解压。

录制提示：
- 录制期间关闭无关标签页与扩展，减少干扰；仅录目标场景，文件体积与录制时长正相关（20s ≈ 35MB gz，60s ≈ 50MB gz）。
- 若勾选了 **CPU throttling**（如 4x slowdown）模拟弱机，提供文件时请一并说明——判读时需区分节流放大与真实开销。

### Step 1: 解压

```bash
node -e "const fs=require('fs'),zlib=require('zlib');fs.createReadStream('IN.json.gz').pipe(zlib.createGunzip()).pipe(fs.createWriteStream('OUT.json')).on('finish',()=>console.log('done'))"
```

### Step 2: 全量分析

```bash
node --max-old-space-size=12288 scripts/analyze-trace.js <trace.json>
```

- 227MB JSON ≈ 8GB 堆；500MB+ 用 12288。输出建议经 `cmd /c "... > out.txt"` 重定向（**不要用 PowerShell `>`**，会把 UTF-8 输出按 GBK 误码转存 UTF-16，中文全乱）。
- 一次运行输出 12 个章节：进程线程 / 窗口繁忙率 / RunTask 分布 / 事件聚合 / 长任务分解 / 脚本 URL 热点 / 函数与 rAF 归因 / GC 与渲染 / 分 tid CPU 采样 / Worker / 掉帧 / UserTiming 伪影甄别。
- 所有线程 ID 自动检测；主线程采样 profile 按节点内容特征识别。

### Step 3: 判读铁律（违反会得出错误结论）

1. **剔除录制伪影**——`CpuProfiler::StartProfiling`（首个任务虚增 500ms+）、`cpu-started/cpu-finished/cpu-duration` UserTiming（数十万条，profiler 采样标记）、采样中 `mark`/`measure` 的大头、`v8::Debugger::AsyncTaskRun`。详见 [reference.md](reference.md)。
2. **CPU 采样只信分 tid 结果**——跨 tid 合并 profile 会因 node id 冲突产生 WASM/Worker/dijkstra 虚假热点（两个真实案例验证，详见 reference.md）。脚本已分 tid，若自行二次加工必须保持分组。
3. **对账定位 native 调用**——X 事件 wall time − 采样 JS self time = native 调用耗时。`readPixels`/`texSubImage2D`/WebGL 提交不产生 timeline 事件，只在采样中可见。
4. **卡顿判据**——每秒 busy% 持续 95~100% = 主线程饱和（卡死直接证据）；帧 JS > 16.7ms 且每秒 ~60 个此类任务 = 帧预算击穿；每帧 `readPixels` = 弱 GPU 设备放大器（解释"只在部分电脑卡死"）。
5. **排除法先行**——GC <1%、Layout/Paint 占比小、Worker 全 idle 时明确写入"已排除嫌疑"，防止优化走偏。

### Step 4: 报告（Markdown 模板）

```markdown
# 性能日志分析报告
| 项目 | 说明 |（文件/站点/窗口/现象/方法）
## 结论摘要（TL;DR）——元凶 + 一句话机制
## 一、整体健康度指标（繁忙率/掉帧/长任务/每秒 busy% 代码块/RunTask 分布表）
## 二、CPU 消耗任务排名（来源 URL+次数+单次分布+内部构成对账表）
## 三、卡顿归因（按危险度排序 + 机制解释 + 已排除嫌疑表）
## 四、优化建议 P0~P3（每条对应一个归因）
## 附录：方法说明 + 录制伪影清单
```

完整填充范例（含每秒 busy% 饱和判读、对账表、嫌疑排除表、多 trace 对比写法）见 [examples.md](examples.md)。

### Step 5: PDF（可选）

```bash
node scripts/md2html.js <report.md> <report.html>
# Windows 自带 Edge / Chrome headless 打印:
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 --print-to-pdf="<report.pdf>" "file:///<report.html>"
```

验证 PDF：文件头 `%PDF`、尾 `%%EOF`、页数符合预期。

## Additional resources

- 完整判读标准、伪影对照表、误报案例机理、高危模式清单、真实案例数据：[reference.md](reference.md)
- 完整分析报告范例（内网白板应用卡死现场，report-2 全文 + 判读导读）：[examples.md](examples.md)
