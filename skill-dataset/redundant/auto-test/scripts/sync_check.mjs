#!/usr/bin/env node
const SCRIPT_VERSION = "0.3.0";
// sync_check: 进 skill 时跑，算 pending（待同步 commit 列表）
//
// 行为（v0.3 精简模式）：
// 1. 读 .auto-test/sync-state.json.lastSyncedCommit (= L)
// 2. git log L..HEAD 拿到所有未同步 commit（仅 SHA）
// 3. 检测 git-ai 是否可用
// 4. 输出 {pending, items: [{commit}], hasGitAi, lastSyncedCommit, lastSyncAt}
//
// diff 文件列表、黑名单过滤、git-ai 对话提取全部推迟到 05-sync 流程按需执行。
//
// 用法：
//   node sync_check.mjs --root <项目根>

import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { join, resolve } from 'node:path';

function parseArgs() {
  const args = process.argv.slice(2);
  let root = '.';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--root' && args[i + 1]) root = args[++i];
  }
  return { root: resolve(root) };
}

function run(cmd, cwd) {
  try {
    const out = execSync(cmd, { cwd, encoding: 'utf8', timeout: 10000 }).trim();
    return { ok: true, out, err: '' };
  } catch (e) {
    return { ok: false, out: '', err: e.message };
  }
}

function hasGitAi() {
  const r = run(process.platform === 'win32' ? 'where git-ai' : 'command -v git-ai', process.cwd());
  return r.ok && !!r.out;
}

function out(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

async function main() {
  const { root } = parseArgs();
  const statePath = join(root, '.auto-test', 'sync-state.json');

  if (!existsSync(statePath)) {
    out({ pending: 0, items: [], hasGitAi: false, lastSyncedCommit: null, lastSyncAt: null, warning: 'sync-state.json missing, run init first', warningCode: 'NOT_INITIALIZED' });
    return 0;
  }

  let state;
  try {
    state = JSON.parse(await readFile(statePath, 'utf8'));
  } catch (e) {
    out({ pending: 0, items: [], hasGitAi: false, lastSyncedCommit: null, lastSyncAt: null, warning: `sync-state.json parse error: ${e.message}`, warningCode: 'STATE_CORRUPTED' });
    return 0;
  }

  const L = state.lastSyncedCommit;
  if (!L) {
    out({ pending: 0, items: [], hasGitAi: false, lastSyncedCommit: null, lastSyncAt: state.lastSyncAt || null, warning: 'lastSyncedCommit missing in sync-state.json', warningCode: 'STATE_CORRUPTED' });
    return 0;
  }

  const head = run('git rev-parse HEAD', root);
  if (!head.ok) {
    out({ pending: 0, items: [], hasGitAi: false, lastSyncedCommit: L, lastSyncAt: state.lastSyncAt || null, warning: 'git rev-parse HEAD failed', warningCode: 'GIT_UNAVAILABLE' });
    return 0;
  }

  if (head.out === L) {
    out({ pending: 0, items: [], hasGitAi: hasGitAi(), lastSyncedCommit: L, lastSyncAt: state.lastSyncAt || null });
    return 0;
  }

  const log = run(`git log ${L}..HEAD --pretty=format:%H`, root);
  if (!log.ok) {
    out({ pending: 0, items: [], hasGitAi: false, lastSyncedCommit: L, lastSyncAt: state.lastSyncAt || null, warning: `git log ${L}..HEAD failed: ${log.err}`, warningCode: 'STATE_AHEAD' });
    return 0;
  }

  const commits = log.out.split('\n').filter(Boolean);
  const items = commits.map((commit) => ({ commit }));

  out({
    pending: items.length,
    items,
    hasGitAi: hasGitAi(),
    lastSyncedCommit: L,
    lastSyncAt: state.lastSyncAt || null,
  });
  return 0;
}

main()
  .then((c) => process.exit(c))
  .catch((e) => {
    process.stderr.write(`[sync_check] error: ${e.message}\n`);
    process.exit(1);
  });
