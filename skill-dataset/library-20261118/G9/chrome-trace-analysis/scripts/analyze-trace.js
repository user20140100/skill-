// Chrome DevTools performance trace 全量分析 (零依赖, Node.js 18+)
// 用法: node --max-old-space-size=12288 analyze-trace.js <trace.json>
// 输入: DevTools Performance 面板导出的 trace (已解压的 .json; .gz 先用 gunzip 解压)
// 输出: 12 个章节的完整分析 (控制台 stdout, 建议重定向到文件)
//
// 注意:
// - 所有线程 ID 自动检测, 无需修改脚本
// - CPU 采样 (ProfileChunk) 严格按 tid 分组合并, 防止跨线程 node id 冲突造成虚假热点
// - 主线程 profile 按采样节点内容特征识别 (含 requestAnimationFrame/readPixels), 不依赖 tid
'use strict';
const fs = require('fs');

const FILE = process.argv[2];
if (!FILE) { console.error('用法: node --max-old-space-size=12288 analyze-trace.js <trace.json>'); process.exit(1); }
console.log('加载:', FILE);
const trace = JSON.parse(fs.readFileSync(FILE, 'utf8'));
const events = trace.traceEvents;
console.log(`总事件数: ${events.length.toLocaleString()}`);

const ms = (us) => (us / 1000).toFixed(1);
const pad = (s, n) => String(s).padStart(n);

// ============ 1. 进程/线程结构 + 最忙渲染主线程 ============
const processNames = {}, threadNames = {};
for (const e of events) {
  if (e.ph === 'M' && e.name === 'process_name') processNames[e.pid] = e.args?.name || '?';
  if (e.ph === 'M' && e.name === 'thread_name') threadNames[e.pid + ':' + e.tid] = e.args?.name || '?';
}
console.log('\n===== 1. 进程与线程 =====');
for (const [pid, name] of Object.entries(processNames)) console.log(`  pid=${pid}  ${name}`);
const loadByThread = {};
for (const e of events) {
  if (e.ph === 'X' && typeof e.dur === 'number') {
    const key = e.pid + ':' + e.tid;
    loadByThread[key] = (loadByThread[key] || 0) + e.dur;
  }
}
console.log('线程负载 TOP 8:');
for (const [k, v] of Object.entries(loadByThread).sort((a, b) => b[1] - a[1]).slice(0, 8)) {
  const [pid] = k.split(':');
  console.log(`  ${pad((v / 1e6).toFixed(2), 8)}s  ${processNames[pid]} / ${threadNames[k] || k}`);
}
const mainCandidates = Object.entries(loadByThread).filter(([k]) => threadNames[k] === 'CrRendererMain');
if (!mainCandidates.length) { console.error('未找到 CrRendererMain'); process.exit(1); }
const MAIN_KEY = mainCandidates.sort((a, b) => b[1] - a[1])[0][0];
const [MPID, MTID] = MAIN_KEY.split(':').map(Number);
console.log('选定渲染主线程:', MAIN_KEY, '(负载含嵌套事件, 仅用于选择)');

// ============ 2. 主线程事件 + 真实窗口 + 繁忙率 ============
const mainEvents = [];
for (const e of events) {
  if (e.ph === 'X' && e.pid === MPID && e.tid === MTID && typeof e.dur === 'number') {
    mainEvents.push({ n: e.name, ts: e.ts, dur: e.dur, args: e.args });
  }
}
mainEvents.sort((a, b) => a.ts - b.ts);
const runTasks = mainEvents.filter(e => e.n === 'RunTask');
if (!runTasks.length) { console.error('主线程无 RunTask 事件'); process.exit(1); }
const w0 = runTasks[0].ts;
let w1 = -Infinity;
for (const t of runTasks) { const x = t.ts + t.dur; if (x > w1) w1 = x; }
const windowSec = (w1 - w0) / 1e6;
const totalTaskTime = runTasks.reduce((s, e) => s + e.dur, 0);
console.log('\n===== 2. 录制窗口与主线程繁忙率 =====');
console.log(`窗口: ${windowSec.toFixed(2)}s | RunTask: ${runTasks.length.toLocaleString()} 个 / ${ms(totalTaskTime)}ms | 主线程繁忙率: ${(totalTaskTime / (w1 - w0) * 100).toFixed(1)}%`);

// ============ 3. RunTask 时长分布 ============
const BK = ['<8ms', '8-16ms', '16-32ms', '32-50ms', '50-100ms', '>100ms'];
const bCnt = {}, bTime = {};
for (const k of BK) { bCnt[k] = 0; bTime[k] = 0; }
for (const t of runTasks) {
  const m = t.dur / 1000;
  const k = m < 8 ? BK[0] : m < 16 ? BK[1] : m < 32 ? BK[2] : m < 50 ? BK[3] : m < 100 ? BK[4] : BK[5];
  bCnt[k]++; bTime[k] += t.dur;
}
console.log('\n===== 3. RunTask 时长分布 (次数 / 总耗时ms) =====');
for (const k of BK) console.log(`  ${k.padEnd(9)} ${pad(bCnt[k], 8)} / ${ms(bTime[k])}`);
console.log('判读: 8-32ms 区间总耗时大 = 每帧 rAF 重负载; 单个 >100ms 需排查伪影');

// ============ 4. 事件类型聚合 TOP 25 ============
const agg = {};
for (const e of mainEvents) {
  if (!agg[e.n]) agg[e.n] = { total: 0, count: 0, max: 0 };
  agg[e.n].total += e.dur; agg[e.n].count++;
  if (e.dur > agg[e.n].max) agg[e.n].max = e.dur;
}
console.log('\n===== 4. 主线程事件聚合 TOP 25 (ms) =====');
for (const [n, s] of Object.entries(agg).sort((a, b) => b[1].total - a[1].total).slice(0, 25)) {
  console.log(`  ${n.padEnd(45)} total=${pad(ms(s.total), 9)} count=${pad(s.count, 7)} max=${ms(s.max)}`);
}

// ============ 5. 长任务分析 (父子树分解) ============
const parentOf = new Int32Array(mainEvents.length).fill(-1);
{
  const stack = [];
  for (let i = 0; i < mainEvents.length; i++) {
    const e = mainEvents[i];
    while (stack.length && mainEvents[stack[stack.length - 1]].ts + mainEvents[stack[stack.length - 1]].dur <= e.ts) stack.pop();
    if (stack.length) parentOf[i] = stack[stack.length - 1];
    stack.push(i);
  }
}
const childrenMap = new Map();
for (let i = 0; i < mainEvents.length; i++) {
  mainEvents[i]._idx = i;
  const p = parentOf[i];
  if (p >= 0) { if (!childrenMap.has(p)) childrenMap.set(p, []); childrenMap.get(p).push(i); }
}
const breakdown = (t) => (childrenMap.get(t._idx) || []).map(i => mainEvents[i]).sort((a, b) => b.dur - a.dur);
const longTasks = runTasks.filter(e => e.dur > 50000).sort((a, b) => b.dur - a.dur);
console.log('\n===== 5. 长任务 (>50ms) =====');
console.log(`长任务数: ${longTasks.length}, 总耗时: ${ms(longTasks.reduce((s, e) => s + e.dur, 0))}ms`);
const fmtExtra = (e) => {
  const d = e.args?.data || {};
  let s = '';
  if (d.url) s += ` url=${d.url.split('/').slice(-2).join('/')}${d.lineNumber !== undefined ? ':' + d.lineNumber : ''}`;
  if (d.functionName) s += ` fn=${d.functionName}`;
  if (d.type) s += ` type=${d.type}`;
  return s;
};
for (const t of longTasks.slice(0, 10)) {
  console.log(`\n[${((t.ts - w0) / 1e6).toFixed(2)}s] RunTask ${ms(t.dur)}ms`);
  for (const c of breakdown(t).slice(0, 5)) console.log(`    ${c.n.padEnd(42)} ${pad(ms(c.dur), 8)}ms${fmtExtra(c)}`);
}
// 长任务来源分类
const catStats = {};
for (const t of longTasks) {
  const rep = breakdown(t)[0];
  const d = rep?.args?.data || {};
  const key = (rep ? rep.n : 'Unknown') + (d.type ? ` (${d.type})` : d.functionName ? ` (${d.functionName})` : '');
  if (!catStats[key]) catStats[key] = { total: 0, count: 0, max: 0 };
  catStats[key].total += t.dur; catStats[key].count++;
  if (t.dur > catStats[key].max) catStats[key].max = t.dur;
}
console.log('\n长任务来源分类:');
for (const [k, s] of Object.entries(catStats).sort((a, b) => b[1].total - a[1].total)) {
  console.log(`  ${k.padEnd(55)} total=${pad(ms(s.total), 8)}ms n=${pad(s.count, 4)} max=${ms(s.max)}ms`);
}

// ============ 6. 脚本 URL 热点 ============
console.log('\n===== 6. FunctionCall 脚本 URL 热点 =====');
const urlStats = {};
for (const e of mainEvents) {
  if (e.n === 'FunctionCall' && e.args?.data?.url) {
    const m = e.args.data.url.match(/^(https?:\/\/[^/]+)([^?]*)/);
    const key = m ? m[1] + m[2] : e.args.data.url;
    if (!urlStats[key]) urlStats[key] = { total: 0, count: 0 };
    urlStats[key].total += e.dur; urlStats[key].count++;
  }
}
for (const [u, s] of Object.entries(urlStats).sort((a, b) => b[1].total - a[1].total).slice(0, 10)) {
  console.log(`  ${pad(ms(s.total), 9)}ms n=${pad(s.count, 6)}  ${u}`);
}

// ============ 7. 函数热点 + rAF 回调统计 ============
console.log('\n===== 7. FunctionCall / Timer / rAF 热点 =====');
const fnStats = {};
for (const e of mainEvents) {
  if (['FunctionCall', 'TimerFire', 'FireAnimationFrame', 'EventDispatch'].includes(e.n)) {
    const d = e.args?.data || {};
    let key = e.n;
    if (e.n === 'FunctionCall') key += `: ${d.functionName || '(anon)'} ${d.url ? d.url.split('/').pop() : ''}${d.lineNumber !== undefined ? ':' + d.lineNumber : ''}`;
    if (e.n === 'EventDispatch') key += `: ${d.type || ''}`;
    if (!fnStats[key]) fnStats[key] = { total: 0, count: 0, max: 0 };
    fnStats[key].total += e.dur; fnStats[key].count++;
    if (e.dur > fnStats[key].max) fnStats[key].max = e.dur;
  }
}
for (const [k, s] of Object.entries(fnStats).sort((a, b) => b[1].total - a[1].total).slice(0, 15)) {
  console.log(`  total=${pad(ms(s.total), 9)}ms n=${pad(s.count, 6)} max=${pad(ms(s.max), 8)}ms  ${k}`);
}
// rAF 回调归因: FunctionCall 向上 6 层内有 FireAnimationFrame
const rafCb = {};
for (let i = 0; i < mainEvents.length; i++) {
  const e = mainEvents[i];
  if (e.n !== 'FunctionCall') continue;
  let cur = i, inRaf = false;
  for (let k = 0; k < 6; k++) { cur = parentOf[cur]; if (cur < 0) break; if (mainEvents[cur].n === 'FireAnimationFrame') { inRaf = true; break; } }
  if (inRaf) {
    const d = e.args?.data || {};
    const key = `${d.functionName || '(anon)'} @ ${(d.url || '').split('/').pop()}:${d.lineNumber}`;
    if (!rafCb[key]) rafCb[key] = { total: 0, count: 0, max: 0 };
    rafCb[key].total += e.dur; rafCb[key].count++;
    if (e.dur > rafCb[key].max) rafCb[key].max = e.dur;
  }
}
console.log('\nrAF 回调归因 (谁注册了每帧回调):');
for (const [k, s] of Object.entries(rafCb).sort((a, b) => b[1].total - a[1].total).slice(0, 8)) {
  console.log(`  total=${pad(ms(s.total), 9)}ms n=${pad(s.count, 6)} max=${pad(ms(s.max), 8)}ms  ${k}`);
}
// Timer TOP 5
console.log('\nTimerFire TOP 5:');
for (const t of mainEvents.filter(e => e.n === 'TimerFire').sort((a, b) => b.dur - a.dur).slice(0, 5)) {
  console.log(`  ${ms(t.dur)}ms @${((t.ts - w0) / 1e6).toFixed(2)}s timerId=${t.args?.data?.timerId}`);
}

// ============ 8. GC / 渲染流水线 汇总 ============
console.log('\n===== 8. GC 与渲染流水线 =====');
for (const n of ['MajorGC', 'MinorGC', 'UpdateLayoutTree', 'Layout', 'PrePaint', 'Paint', 'CompositeLayers', 'Commit', 'EventDispatch', 'HandlePostMessage', 'RunMicrotasks', 'EvaluateScript']) {
  if (agg[n]) console.log(`  ${n.padEnd(22)} total=${pad(ms(agg[n].total), 8)}ms n=${pad(agg[n].count, 6)} max=${ms(agg[n].max)}ms`);
}
const syncLayout = mainEvents.filter(e => (e.n === 'Layout' || e.n === 'UpdateLayoutTree') && e.args?.beginData?.stackTrace?.length > 0);
console.log(`  JS 触发的同步 Layout: ${syncLayout.length} 次`);

// ============ 9. 分 tid CPU Profile ============
console.log('\n===== 9. 分线程 CPU 采样 (ProfileChunk) =====');
const chunksByTid = new Map();
for (const e of events) {
  if (e.name === 'ProfileChunk' && e.pid === MPID) {
    if (!chunksByTid.has(e.tid)) chunksByTid.set(e.tid, []);
    chunksByTid.get(e.tid).push(e);
  }
}
const profiles = []; // {tid, nodeMap, selfById, totalDelta, busyPerSec, topFns, hasMainFeat}
for (const [tid, chunks] of chunksByTid) {
  chunks.sort((a, b) => a.ts - b.ts);
  const nodeMap = new Map(), selfById = new Map();
  const samples = [], deltas = [];
  for (const c of chunks) {
    const d = c.args?.data;
    if (!d) continue;
    if (d.cpuProfile?.nodes) for (const n of d.cpuProfile.nodes) nodeMap.set(n.id, n);
    if (d.cpuProfile?.samples) samples.push(...d.cpuProfile.samples);
    if (d.timeDeltas) deltas.push(...d.timeDeltas);
  }
  let totalDelta = 0; for (const d of deltas) totalDelta += d;
  for (let i = 0; i < samples.length && i < deltas.length; i++) selfById.set(samples[i], (selfById.get(samples[i]) || 0) + deltas[i]);
  const fnAgg = new Map();
  let hasMainFeat = false;
  for (const [id, t] of selfById) {
    const node = nodeMap.get(id); if (!node) continue;
    const cf = node.callFrame;
    if (cf.functionName === 'requestAnimationFrame' || (cf.functionName || '').includes('readPixels')) hasMainFeat = true;
    let url = (cf.url || '');
    url = url.startsWith('blob:') ? url.slice(0, 30) : url.split('/').slice(-2).join('/');
    const key = `${cf.functionName || '(anon)'} @ ${url}:${cf.lineNumber}`;
    fnAgg.set(key, (fnAgg.get(key) || 0) + t);
  }
  // 每秒 busy (剔除 idle/root)
  const idleIds = new Set();
  for (const [id, node] of nodeMap) { const f = node.callFrame.functionName; if (f === '(idle)' || f === '(root)') idleIds.add(id); }
  const busyBySec = new Map();
  const tStart = chunks[0]?.ts || 0;
  for (const c of chunks) {
    const d = c.args?.data;
    if (!d?.timeDeltas || !d.cpuProfile?.samples) continue;
    let t = c.ts;
    for (let i = 0; i < d.timeDeltas.length && i < d.cpuProfile.samples.length; i++) {
      const sec = Math.floor((t - tStart) / 1e6);
      if (!idleIds.has(d.cpuProfile.samples[i])) busyBySec.set(sec, (busyBySec.get(sec) || 0) + d.timeDeltas[i]);
      t += d.timeDeltas[i];
    }
  }
  profiles.push({ tid, totalDelta, fnAgg, busyBySec, hasMainFeat, threadName: threadNames[MPID + ':' + tid] || '?' });
}
for (const p of profiles.sort((a, b) => b.totalDelta - a.totalDelta)) {
  console.log(`\n--- tid=${p.tid} (${p.threadName}) 采样=${(p.totalDelta / 1e6).toFixed(2)}s 主线程特征=${p.hasMainFeat} ---`);
  for (const [k, t] of [...p.fnAgg.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12)) {
    console.log(`  ${pad(ms(t), 9)}ms (${pad((t / p.totalDelta * 100).toFixed(1), 5)}%)  ${k}`);
  }
}
// 主线程 profile: 含特征节点且采样最长; 找不到则取最长
let mainProf = profiles.filter(p => p.hasMainFeat).sort((a, b) => b.totalDelta - a.totalDelta)[0] || profiles.sort((a, b) => b.totalDelta - a.totalDelta)[0];
if (mainProf) {
  console.log(`\n===== 主线程每秒 CPU busy% (profile tid=${mainProf.tid}, 剔除 idle) =====`);
  const parts = [];
  for (const [s, v] of [...mainProf.busyBySec.entries()].sort((a, b) => a[0] - b[0])) parts.push(`${s}s:${Math.round(v / 10000)}%`);
  console.log(parts.join(' '));
  console.log('判读: 持续 95-100% = 主线程饱和卡死; >50% 长期 = 高危');
}

// ============ 10. Worker / postMessage ============
console.log('\n===== 10. Worker / postMessage 事件 =====');
const wAgg = {};
for (const e of events) {
  const n = e.name || '';
  if (n.toLowerCase().includes('worker') || n === 'HandlePostMessage' || n === 'SchedulePostMessage') {
    const key = `${n} [${threadNames[e.pid + ':' + e.tid] || e.tid}]`;
    if (!wAgg[key]) wAgg[key] = { total: 0, count: 0, max: 0 };
    if (e.ph === 'X') { wAgg[key].total += e.dur; if (e.dur > wAgg[key].max) wAgg[key].max = e.dur; }
    wAgg[key].count++;
  }
}
for (const [k, s] of Object.entries(wAgg).sort((a, b) => b[1].total - a[1].total).slice(0, 8)) {
  console.log(`  ${k.padEnd(58)} total=${pad(ms(s.total), 8)}ms n=${pad(s.count, 5)} max=${ms(s.max)}ms`);
}

// ============ 11. 掉帧分布 ============
console.log('\n===== 11. 掉帧 (DroppedFrame) =====');
const dropped = events.filter(e => e.name === 'DroppedFrame');
console.log(`总掉帧: ${dropped.length} 次`);
if (dropped.length) {
  const base = dropped[0].ts, bySec = {};
  for (const d of dropped) { const s = Math.floor((d.ts - base) / 1e6); bySec[s] = (bySec[s] || 0) + 1; }
  console.log('每秒掉帧:', JSON.stringify(bySec));
}

// ============ 12. UserTiming 伪影甄别 ============
console.log('\n===== 12. UserTiming 事件甄别 (识别 profiler 伪影) =====');
const utNames = {};
let utCount = 0, utTimelineCount = 0;
for (const e of events) {
  if (e.pid !== MPID) continue;
  if ((e.cat || '').includes('blink.user_timing')) {
    utCount++;
    const key = e.name + '|' + e.ph;
    utNames[key] = (utNames[key] || 0) + 1;
  } else if (e.name === 'UserTiming::Measure' || e.name === 'UserTiming::Mark') {
    utTimelineCount++;
  }
}
console.log(`blink.user_timing 总数: ${utCount.toLocaleString()} | devtools.timeline UserTiming::Measure/Mark: ${utTimelineCount.toLocaleString()}`);
for (const [k, v] of Object.entries(utNames).sort((a, b) => b[1] - a[1]).slice(0, 6)) console.log(`  ${pad(v, 8)}  ${k}`);
console.log('判读: cpu-started/cpu-finished/cpu-duration 为 CPU Profiler 采样标记(伪影), 其 mark/measure 开销须从页面成本中剔除');

console.log('\n分析完成。判读规则与报告模板见 skill 的 SKILL.md / reference.md');
