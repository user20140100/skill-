// 零依赖 Markdown -> 打印样式 HTML (针对本报告语法)
const fs = require('fs');

const IN = process.argv[2] || 'd:/workspace/trace-analysis/performance-analysis-report.md';
const OUT = process.argv[3] || 'd:/workspace/trace-analysis/report.html';
const md = fs.readFileSync(IN, 'utf8');

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// 内联: 行内代码/粗体/链接
function inline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `${codes.length - 1}`; });
  s = escapeHtml(s);
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, t, u) => {
    // file:// 链接在 PDF 中只显示文本
    return u.startsWith('file://') ? `<span class="filelink">${t}</span>` : `<a href="${u}">${t}</a>`;
  });
  s = s.replace(/(\d+)/g, (_, i) => `<code>${escapeHtml(codes[+i])}</code>`);
  return s;
}

const lines = md.split(/\r?\n/);
const html = [];
let i = 0;

while (i < lines.length) {
  const line = lines[i];

  // 代码块
  if (line.startsWith('```')) {
    const buf = [];
    i++;
    while (i < lines.length && !lines[i].startsWith('```')) { buf.push(lines[i]); i++; }
    i++;
    html.push(`<pre>${escapeHtml(buf.join('\n'))}</pre>`);
    continue;
  }
  // 表格
  if (line.trim().startsWith('|')) {
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) { rows.push(lines[i]); i++; }
    const parseRow = (r) => r.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
    const head = parseRow(rows[0]);
    const body = rows.slice(2);
    let t = '<table><thead><tr>' + head.map(c => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>';
    for (const r of body) t += '<tr>' + parseRow(r).map(c => `<td>${inline(c)}</td>`).join('') + '</tr>';
    t += '</tbody></table>';
    html.push(t);
    continue;
  }
  // 标题
  const h = line.match(/^(#{1,4})\s+(.*)$/);
  if (h) {
    const lv = h[1].length;
    html.push(`<h${lv}>${inline(h[2])}</h${lv}>`);
    i++;
    continue;
  }
  // 分隔线
  if (/^---+\s*$/.test(line)) { html.push('<hr>'); i++; continue; }
  // 引用
  if (line.startsWith('>')) {
    const buf = [];
    while (i < lines.length && lines[i].startsWith('>')) { buf.push(lines[i].replace(/^>\s?/, '')); i++; }
    html.push(`<blockquote>${buf.map(l => `<p>${inline(l)}</p>`).join('')}</blockquote>`);
    continue;
  }
  // 列表 (支持一级嵌套)
  if (/^\s*(-|\d+\.)\s+/.test(line)) {
    const items = [];
    while (i < lines.length && /^\s*(-|\d+\.)\s+/.test(lines[i])) {
      const m = lines[i].match(/^(\s*)(-|\d+\.)\s+(.*)$/);
      items.push({ indent: m[1].length, ordered: /\d/.test(m[2][0]), text: m[3] });
      i++;
    }
    let out = '', stack = [];
    for (const it of items) {
      const lv = it.indent >= 2 ? 1 : 0;
      const tag = it.ordered ? 'ol' : 'ul';
      while (stack.length > lv + 1) { out += `</${stack.pop()}>`; }
      if (stack.length === lv) { out += `<${tag}>`; stack.push(tag); }
      else if (stack[stack.length - 1] !== tag) { out += `</${stack.pop()}><${tag}>`; stack.push(tag); }
      out += `<li>${inline(it.text)}</li>`;
    }
    while (stack.length) out += `</${stack.pop()}>`;
    html.push(out);
    continue;
  }
  // 空行
  if (line.trim() === '') { i++; continue; }
  // 段落
  html.push(`<p>${inline(line)}</p>`);
  i++;
}

const doc = `<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>Web 站点性能日志深度分析报告</title>
<style>
  @page { size: A4; margin: 18mm 16mm; }
  * { box-sizing: border-box; }
  body { font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif; font-size: 10.5pt; line-height: 1.65; color: #1a1a2e; margin: 0; }
  h1 { font-size: 20pt; color: #0d1b3e; border-bottom: 3px solid #2563eb; padding-bottom: 10px; margin: 0 0 18px; }
  h2 { font-size: 14.5pt; color: #0d1b3e; border-left: 5px solid #2563eb; padding-left: 10px; margin: 26px 0 12px; page-break-after: avoid; }
  h3 { font-size: 12pt; color: #1e3a6e; margin: 18px 0 8px; page-break-after: avoid; }
  h4 { font-size: 11pt; margin: 14px 0 6px; page-break-after: avoid; }
  p { margin: 6px 0; }
  table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; page-break-inside: avoid; }
  th { background: #2563eb; color: #fff; padding: 6px 9px; text-align: left; font-weight: 600; }
  td { border: 1px solid #cbd5e1; padding: 5px 9px; }
  tr:nth-child(even) td { background: #f1f5f9; }
  code { background: #eef2ff; color: #b91c1c; padding: 1px 5px; border-radius: 3px; font-family: Consolas, "Courier New", monospace; font-size: 9pt; }
  pre { background: #0f172a; color: #e2e8f0; padding: 12px 14px; border-radius: 6px; font-family: Consolas, monospace; font-size: 9pt; line-height: 1.5; white-space: pre-wrap; word-break: break-all; page-break-inside: avoid; }
  blockquote { border-left: 4px solid #f59e0b; background: #fffbeb; margin: 10px 0; padding: 8px 14px; color: #78350f; }
  blockquote p { margin: 3px 0; }
  ul, ol { margin: 6px 0; padding-left: 24px; }
  li { margin: 3px 0; }
  hr { border: none; border-top: 1px solid #cbd5e1; margin: 20px 0; }
  strong { color: #0d1b3e; }
  a { color: #2563eb; text-decoration: none; }
  .filelink { color: #2563eb; font-family: Consolas, monospace; font-size: 9pt; }
</style></head><body>
${html.join('\n')}
</body></html>`;

fs.writeFileSync(OUT, doc, 'utf8');
console.log('HTML 生成完成:', OUT, (doc.length / 1024).toFixed(1), 'KB');
