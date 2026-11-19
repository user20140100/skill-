#!/usr/bin/env node
const SCRIPT_VERSION = "0.1.0";

import { readFile, readdir, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, relative, basename, dirname } from 'node:path';
import { makeDebug } from './sync_common.mjs';

const debug = makeDebug('report_gen');

function parseArgs() {
  const args = process.argv.slice(2);
  let root = process.cwd();
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--root' && args[i + 1]) root = args[++i];
  }
  return { root };
}

async function scanRuns(root) {
  const runsDir = join(root, '.auto-test', 'runs');
  if (!existsSync(runsDir)) return [];

  const entries = await readdir(runsDir, { withFileTypes: true });
  const runs = [];

  for (const entry of entries) {
    if (!entry.isDirectory() || !entry.name.startsWith('run-')) continue;
    const summaryPath = join(runsDir, entry.name, 'summary.json');
    if (!existsSync(summaryPath)) continue;
    try {
      const data = JSON.parse(await readFile(summaryPath, 'utf8'));
      const ts = parseInt(entry.name.replace('run-', ''), 10) || 0;
      runs.push({
        runId: data.runId || entry.name,
        ts,
        passed: Array.isArray(data.passed) ? data.passed : [],
        failed: Array.isArray(data.failed) ? data.failed : [],
        fixmed: Array.isArray(data.fixmed) ? data.fixmed : [],
        escalated: Array.isArray(data.escalated) ? data.escalated : [],
      });
    } catch (e) {
      debug(`skip ${entry.name}: ${e.message}`);
    }
  }

  runs.sort((a, b) => a.ts - b.ts);
  return runs;
}

async function scanNl(root) {
  const nlDir = join(root, '.auto-test', 'case', 'nl');
  if (!existsSync(nlDir)) return [];

  const cases = [];
  const routes = await readdir(nlDir, { withFileTypes: true });

  for (const route of routes) {
    if (!route.isDirectory()) continue;
    const routeKey = route.name;
    const files = await readdir(join(nlDir, routeKey));

    for (const file of files) {
      if (!file.endsWith('.md')) continue;
      const content = await readFile(join(nlDir, routeKey, file), 'utf8');
      const fm = parseFrontmatter(content);
      cases.push({
        caseId: file.replace('.md', ''),
        routeKey,
        pendingCode: fm.pendingCode === true || fm.pendingCode === 'true',
        deprecated: fm.deprecated === true || fm.deprecated === 'true',
        manualPin: fm.manualPin === true || fm.manualPin === 'true',
        hasSpec: !!fm.specRef,
      });
    }
  }
  return cases;
}

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const fm = {};
  for (const line of match[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx < 0) continue;
    const key = line.slice(0, idx).trim();
    let val = line.slice(idx + 1).trim();
    if (val === 'true') val = true;
    else if (val === 'false') val = false;
    fm[key] = val;
  }
  return fm;
}

function computeHistory(runs, nlCases) {
  const runHistory = runs.map(r => ({
    runId: r.runId,
    ts: r.ts,
    passedCount: r.passed.length,
    failedCount: r.failed.length,
    fixmedCount: r.fixmed.length,
    escalatedCount: r.escalated.length,
    total: r.passed.length + r.failed.length + r.fixmed.length + r.escalated.length,
    passRate: r.passed.length / Math.max(1, r.passed.length + r.failed.length + r.fixmed.length + r.escalated.length),
  }));

  // Module coverage
  const routeMap = {};
  for (const c of nlCases) {
    if (!routeMap[c.routeKey]) {
      routeMap[c.routeKey] = { routeKey: c.routeKey, nlCount: 0, specCount: 0, activeCount: 0, lastPassCount: 0 };
    }
    routeMap[c.routeKey].nlCount++;
    if (c.hasSpec) routeMap[c.routeKey].specCount++;
    if (!c.pendingCode && !c.deprecated) routeMap[c.routeKey].activeCount++;
  }

  // Last run pass count per route
  if (runs.length > 0) {
    const lastRun = runs[runs.length - 1];
    for (const item of lastRun.passed) {
      const routeKey = extractRouteKey(item.caseId);
      if (routeKey && routeMap[routeKey]) routeMap[routeKey].lastPassCount++;
    }
  }

  const moduleCoverage = Object.values(routeMap);

  // Flaky detection: cases that alternate pass/fail ≥2 times in last 10 runs
  const recentRuns = runs.slice(-10);
  const caseHistory = {};
  for (const run of recentRuns) {
    for (const item of run.passed) {
      if (!caseHistory[item.caseId]) caseHistory[item.caseId] = [];
      caseHistory[item.caseId].push('pass');
    }
    for (const item of run.failed) {
      if (!caseHistory[item.caseId]) caseHistory[item.caseId] = [];
      caseHistory[item.caseId].push('fail');
    }
    for (const item of run.fixmed) {
      if (!caseHistory[item.caseId]) caseHistory[item.caseId] = [];
      caseHistory[item.caseId].push('fixme');
    }
    for (const item of run.escalated) {
      if (!caseHistory[item.caseId]) caseHistory[item.caseId] = [];
      caseHistory[item.caseId].push('escalated');
    }
  }

  const flaky = [];
  for (const [caseId, history] of Object.entries(caseHistory)) {
    let alternations = 0;
    for (let i = 1; i < history.length; i++) {
      if (history[i] !== history[i - 1]) alternations++;
    }
    if (alternations >= 2) flaky.push({ caseId, alternations, history });
  }
  flaky.sort((a, b) => b.alternations - a.alternations);

  // Failure Top-N
  const failCount = {};
  for (const run of recentRuns) {
    for (const item of run.failed) {
      failCount[item.caseId] = (failCount[item.caseId] || 0) + 1;
    }
  }
  const failTopN = Object.entries(failCount)
    .map(([caseId, count]) => ({ caseId, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  return { runHistory, moduleCoverage, flaky, failTopN, generatedAt: new Date().toISOString() };
}

function extractRouteKey(caseId) {
  const parts = caseId.split('/');
  return parts.length > 1 ? parts[0] : caseId.split('-').slice(0, -1).join('-') || caseId;
}

async function main() {
  const { root } = parseArgs();
  debug(`root=${root}`);

  const runs = await scanRuns(root);
  const nlCases = await scanNl(root);

  if (runs.length === 0) {
    const result = { error: 'NO_RUNS', message: '没有找到任何 runs/run-*/summary.json' };
    process.stdout.write(JSON.stringify(result, null, 2));
    process.exit(0);
  }

  const history = computeHistory(runs, nlCases);

  const outDir = join(root, '.auto-test', 'reports');
  if (!existsSync(outDir)) await mkdir(outDir, { recursive: true });

  const outPath = join(outDir, 'history.json');
  await writeFile(outPath, JSON.stringify(history, null, 2), 'utf8');

  process.stdout.write(JSON.stringify({ ok: true, runs: runs.length, output: outPath }, null, 2));
}

main().catch(e => {
  process.stderr.write(`[report_gen] fatal: ${e.message}\n`);
  process.exit(1);
});
