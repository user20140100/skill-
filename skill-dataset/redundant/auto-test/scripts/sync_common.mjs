#!/usr/bin/env node
const SCRIPT_VERSION = "0.2.1";
// sync_common: 三个 sync 脚本共享的工具函数和黑名单
// 被 sync_check.mjs / sync_collect.mjs / dirty_check.mjs import

import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { join } from 'node:path';

export const DEFAULT_SYNC_IGNORE = [
  '.auto-test/**',
  '.github/**',
  '.gitlab-ci.yml',
  '.vscode/**',
  '.idea/**',
  '.cursor/**',
  '.claude/**',
  'package-lock.json',
  'pnpm-lock.yaml',
  'yarn.lock',
  'bun.lockb',
  '.gitignore',
  '.gitattributes',
  '.editorconfig',
  '.prettierrc*',
  '.prettierignore',
  '.eslintrc*',
  '.eslintignore',
  '.stylelintrc*',
  '.env.example',
  '.nvmrc',
  '.node-version',
  'dist/**',
  'build/**',
  'coverage/**',
  'node_modules/**',
  '**/*.spec.ts',
  '**/*.spec.tsx',
  '**/*.test.ts',
  '**/*.test.tsx',
  'playwright.config.*',
  'vitest.config.*',
  'jest.config.*',
  'e2e/**',
  'tests/**',
  '__tests__/**',
];

export function run(cmd, cwd) {
  try {
    const out = execSync(cmd, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return { ok: true, out: out.trim() };
  } catch (e) {
    const stdout = e.stdout ? String(e.stdout).trim() : '';
    return { ok: false, out: stdout, err: String(e.stderr || e.message || '') };
  }
}

export function globToRegex(glob) {
  let re = '^';
  for (let i = 0; i < glob.length; i++) {
    const c = glob[i];
    if (c === '*') {
      if (glob[i + 1] === '*') {
        re += '.*';
        i++;
        if (glob[i + 1] === '/') i++;
      } else {
        re += '[^/]*';
      }
    } else if (c === '?') {
      re += '[^/]';
    } else if ('.+^$()|{}[]\\'.includes(c)) {
      re += '\\' + c;
    } else {
      re += c;
    }
  }
  re += '$';
  return new RegExp(re);
}

export function matchAny(file, patterns) {
  for (const p of patterns) {
    if (globToRegex(p).test(file)) return true;
  }
  return false;
}

export async function loadSyncIgnore(root) {
  const cfgPath = join(root, '.auto-test', 'config.json');
  let extra = [];
  if (existsSync(cfgPath)) {
    try {
      const cfg = JSON.parse(await readFile(cfgPath, 'utf8'));
      if (Array.isArray(cfg.syncIgnore)) extra = cfg.syncIgnore.filter((s) => typeof s === 'string');
    } catch {
      // ignore parse errors
    }
  }
  return [...DEFAULT_SYNC_IGNORE, ...extra];
}

export function makeDebug(prefix) {
  return (msg) => {
    if (process.env.AUTO_TEST_DEBUG) {
      process.stderr.write(`[${prefix}] ${msg}\n`);
    }
  };
}
