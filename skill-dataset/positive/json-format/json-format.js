#!/usr/bin/env node

'use strict';

const fs = require('fs');
const path = require('path');

// ── 帮助信息 ──────────────────────────────────────────────────────────────────

const USAGE = `
用法:
  json-format <operation> <file-path> [output-path]

操作类型:
  format   / validate  校验 JSON 语法，并美化输出（2 空格缩进）
  compress / minify    移除所有空白，生成紧凑单行格式
  escape               将 JSON 转为可嵌入字符串的转义格式（不含外层引号）
  unescape             将转义字符串还原为正常 JSON，自动格式化

参数:
  <file-path>          输入文件路径（相对路径或绝对路径）
  [output-path]        输出文件路径（可选；不填则输出到 stdout）

示例:
  json-format format   data.json
  json-format format   data.json  data.formatted.json
  json-format compress data.json  data.min.json
  json-format escape   config.json
  json-format escape   config.json  config.escaped.txt
  json-format unescape config.escaped.txt  config.json
`.trim();

const VALID_OPS = new Set(['format', 'validate', 'compress', 'minify', 'escape', 'unescape']);

// ── 参数解析 ──────────────────────────────────────────────────────────────────

const [, , operation, inputPath, outputPath] = process.argv;

if (!operation || operation === '--help' || operation === '-h') {
  console.log(USAGE);
  process.exit(0);
}

if (!VALID_OPS.has(operation)) {
  die(`不支持的操作: "${operation}"\n支持的操作: format / validate / compress / minify / escape / unescape`);
}

if (!inputPath) {
  die(`缺少参数: <file-path>\n\n${USAGE}`);
}

// ── 读取输入文件 ──────────────────────────────────────────────────────────────

let input;
try {
  input = fs.readFileSync(resolvePath(inputPath), 'utf8');
} catch (e) {
  if (e.code === 'ENOENT') {
    die(`文件不存在: ${inputPath}`);
  }
  die(`无法读取文件: ${inputPath}\n${e.message}`);
}

// ── 执行操作 ──────────────────────────────────────────────────────────────────

let result;

switch (operation) {
  case 'format':
  case 'validate': {
    const obj = parseJson(input, inputPath);
    result = JSON.stringify(obj, null, 2);
    break;
  }

  case 'compress':
  case 'minify': {
    const obj = parseJson(input, inputPath);
    result = JSON.stringify(obj);
    break;
  }

  case 'escape': {
    parseJson(input, inputPath); // 先验证语法
    // 去掉 JSON.stringify 自动添加的外层引号，输出纯转义字符串
    result = JSON.stringify(input).slice(1, -1);
    break;
  }

  case 'unescape': {
    const raw = input.trim();
    // 兼容有无外层引号两种格式
    const quoted = raw.startsWith('"') ? raw : `"${raw}"`;
    let unescaped;
    try {
      unescaped = JSON.parse(quoted);
    } catch (e) {
      die(`无法去除转义，内容格式不合法:\n${e.message}`);
    }
    // 验证还原后是否为有效 JSON
    const obj = parseJson(unescaped, inputPath, '去转义后的内容不是合法 JSON');
    result = JSON.stringify(obj, null, 2);
    break;
  }
}

// ── 输出结果 ──────────────────────────────────────────────────────────────────

if (outputPath) {
  const resolved = resolvePath(outputPath);
  try {
    fs.writeFileSync(resolved, result + '\n', 'utf8');
  } catch (e) {
    die(`写入文件失败: ${outputPath}\n${e.message}`);
  }
  // 统计信息输出到 stderr，不污染 stdout
  const lines = result.split('\n').length;
  const bytes = Buffer.byteLength(result, 'utf8');
  process.stderr.write(`已写入: ${outputPath}  (${lines} 行, ${bytes} 字节)\n`);
} else {
  process.stdout.write(result + '\n');
}

// ── 工具函数 ──────────────────────────────────────────────────────────────────

function parseJson(text, filePath, customMsg) {
  try {
    return JSON.parse(text);
  } catch (e) {
    die(customMsg || `${filePath} JSON 语法错误:\n${e.message}`);
  }
}

function resolvePath(p) {
  return path.isAbsolute(p) ? p : path.resolve(process.cwd(), p);
}

function die(msg) {
  process.stderr.write(`错误: ${msg}\n`);
  process.exit(1);
}
