#!/usr/bin/env node
const SCRIPT_VERSION = "0.3.0";
// sync_collect: post-commit hook 调用，记录 commit 到 .auto-test/sync-log.jsonl
//
// 行为（v0.3 精简模式）：
// 1. 检查 .auto-test 目录存在
// 2. 拿 HEAD commit 的改动文件
// 3. 应用 syncIgnore 黑名单过滤（过滤掉 .auto-test/、lockfile、CI 配置、测试文件等）
// 4. 过滤后无文件 → 静默退出（commit 全是与生产测试无关的内容）
// 5. 过滤后有文件 → append {date, commit} 到 sync-log.jsonl
//
// 语义分析（git-ai 对话、diff 内容）推迟到进入 skill 时由 05-sync 按需执行。
//
// 用法：
//   node sync_collect.mjs --root <项目根>

import { appendFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { run, matchAny, loadSyncIgnore, makeDebug } from './sync_common.mjs';

const debug = makeDebug('sync_collect');

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
  if (!existsSync(join(root, '.auto-test'))) {
    debug('no .auto-test, skip');
    return 0;
  }

  const head = run('git rev-parse HEAD', root);
  if (!head.ok) {
    debug('git rev-parse HEAD failed');
    return 0;
  }
  const commit = head.out;

  let diffOut = run(`git diff --name-only ${commit}~1..${commit}`, root);
  if (!diffOut.ok) {
    diffOut = run(`git show --name-only --pretty= ${commit}`, root);
    if (!diffOut.ok) {
      debug('cannot get diff files');
      return 0;
    }
  }
  const diffFiles = diffOut.out.split('\n').filter(Boolean);
  if (!diffFiles.length) {
    debug('no diff files');
    return 0;
  }

  const ignore = await loadSyncIgnore(root);
  const kept = diffFiles.filter((f) => !matchAny(f, ignore));
  if (!kept.length) {
    debug(`all ${diffFiles.length} files ignored by syncIgnore, skip`);
    return 0;
  }

  const record = {
    date: new Date().toISOString().slice(0, 10),
    commit,
  };

  await appendFile(
    join(root, '.auto-test', 'sync-log.jsonl'),
    JSON.stringify(record) + '\n',
    'utf8'
  );
  debug(`recorded ${commit.slice(0, 8)} kept=${kept.length}/${diffFiles.length}`);
  return 0;
}

main()
  .then((c) => process.exit(c))
  .catch((e) => {
    process.stderr.write(`[sync_collect] error: ${e.message}\n`);
    process.exit(0);
  });
