#!/usr/bin/env node
const SCRIPT_VERSION = "0.2.1";
// dirty_check: 检测工作区未提交的源码变更（staged + unstaged + untracked）
//
// 用途：在用户尚未 commit 时，判断是否有源码变更可以增量同步到测试资产
// 用法：node dirty_check.mjs --root <项目根>
// 输出：JSON 到 stdout
//
// 环境变量：
//   AUTO_TEST_DEBUG=1  打印调试信息到 stderr

import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { run, matchAny, loadSyncIgnore, makeDebug } from './sync_common.mjs';

const debug = makeDebug('dirty_check');
const MAX_DIFF_BYTES = 50 * 1024;

function parseArgs() {
  const args = process.argv.slice(2);
  let root = '.';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--root' && args[i + 1]) root = args[++i];
  }
  return { root: resolve(root) };
}

async function main() {
  const { root } = parseArgs();
  const autoTest = join(root, '.auto-test');

  if (!existsSync(autoTest)) {
    process.stdout.write(JSON.stringify({ hasDirtyChanges: false, warning: 'NOT_INITIALIZED' }) + '\n');
    return 0;
  }

  const headCheck = run('git rev-parse HEAD', root);
  if (!headCheck.ok) {
    process.stdout.write(JSON.stringify({ hasDirtyChanges: false, warning: 'GIT_UNAVAILABLE' }) + '\n');
    return 0;
  }

  const ignore = await loadSyncIgnore(root);

  const stagedRaw = run('git diff --cached --name-only', root);
  const unstagedRaw = run('git diff --name-only', root);
  const untrackedRaw = run('git ls-files --others --exclude-standard', root);

  const filterFiles = (raw) => {
    if (!raw.ok || !raw.out) return [];
    return raw.out.split('\n').filter(Boolean).filter((f) => !matchAny(f, ignore));
  };

  const staged = filterFiles(stagedRaw);
  const unstaged = filterFiles(unstagedRaw);
  const untracked = filterFiles(untrackedRaw);

  const totalFiles = new Set([...staged, ...unstaged, ...untracked]).size;

  if (totalFiles === 0) {
    process.stdout.write(JSON.stringify({ hasDirtyChanges: false, staged: [], unstaged: [], untracked: [], totalFiles: 0 }) + '\n');
    return 0;
  }

  let diff = '';
  const diffResult = run('git diff HEAD', root);
  if (diffResult.ok) {
    diff = diffResult.out.length > MAX_DIFF_BYTES
      ? diffResult.out.slice(0, MAX_DIFF_BYTES) + '\n... [truncated at 50KB]'
      : diffResult.out;
  }

  if (untracked.length && diff.length < MAX_DIFF_BYTES) {
    for (const f of untracked) {
      if (diff.length >= MAX_DIFF_BYTES) break;
      const content = run(`git diff --no-index /dev/null "${f}"`, root);
      if (content.out) {
        diff += '\n' + content.out;
      }
    }
    if (diff.length > MAX_DIFF_BYTES) {
      diff = diff.slice(0, MAX_DIFF_BYTES) + '\n... [truncated at 50KB]';
    }
  }

  debug(`totalFiles=${totalFiles} staged=${staged.length} unstaged=${unstaged.length} untracked=${untracked.length}`);

  const result = {
    hasDirtyChanges: true,
    staged,
    unstaged,
    untracked,
    totalFiles,
    diff,
  };

  process.stdout.write(JSON.stringify(result) + '\n');
  return 0;
}

main()
  .then((c) => process.exit(c))
  .catch((e) => {
    process.stderr.write(`[dirty_check] error: ${e.message}\n`);
    process.stdout.write(JSON.stringify({ hasDirtyChanges: false, error: e.message }) + '\n');
    process.exit(0);
  });
