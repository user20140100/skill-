const state = { items: [], active: "", showingIndex: true };
const apiUrl = (path) => new URL(`api/${path}`, window.location.href);
const { inlineMarkdown, resolveImageSource } = window.ProjectPrdMarkdown;

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));

function splitFrontmatter(markdown) {
  const match = markdown.match(/^---\s*\n([\s\S]*?)\n---\s*(?:\n|$)/);
  return match ? { metadata: match[1], body: markdown.slice(match[0].length) } : { metadata: "", body: markdown };
}

function fallbackTable(rows) {
  if (!rows.length) return "";
  const cells = (row) => row.replace(/^\s*\|?/, "").replace(/\|?\s*$/, "").split("|").map(cell => cell.trim());
  const header = cells(rows[0]);
  const bodyRows = rows.slice(1).filter(row => !/^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$/.test(row));
  return `<div class="table-scroll"><table><thead><tr>${header.map(cell => `<th>${inlineMarkdown(cell)}</th>`).join("")}</tr></thead><tbody>${bodyRows.map(row => `<tr>${cells(row).map(cell => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function fallbackMarkdownToHtml(markdown) {
  const lines = markdown.replace(/\r/g, "").split("\n");
  const output = [];
  let inCode = false;
  let codeLanguage = "";
  let code = [];
  let inList = false;
  let inOrderedList = false;
  let tableRows = [];
  const flushTable = () => { if (tableRows.length) { output.push(fallbackTable(tableRows)); tableRows = []; } };
  const closeLists = () => { if (inList) { output.push("</ul>"); inList = false; } if (inOrderedList) { output.push("</ol>"); inOrderedList = false; } };
  for (const line of lines) {
    if (/^\s*\|.*\|\s*$/.test(line)) { tableRows.push(line); continue; }
    flushTable();
    if (line.startsWith("```")) {
      if (inCode) {
        const source = code.join("\n");
        if (codeLanguage === "mermaid") {
          output.push(`<section class="mermaid-card"><div class="mermaid" data-mermaid-source="${escapeHtml(source)}"></div><details><summary>查看 Mermaid 源码</summary><pre class="code mermaid-code"><code>${escapeHtml(source)}</code></pre></details></section>`);
        } else output.push(`<pre class="code"><code>${escapeHtml(source)}</code></pre>`);
        inCode = false; code = []; codeLanguage = "";
      } else { inCode = true; codeLanguage = line.slice(3).trim().toLowerCase(); }
      continue;
    }
    if (inCode) { code.push(line); continue; }
    if (!line.trim()) { closeLists(); continue; }
    if (/^\s*([-*_])\s*\1\s*\1/.test(line)) { closeLists(); output.push("<hr>"); continue; }
    if (line.startsWith("###### ")) { closeLists(); output.push(`<h6>${inlineMarkdown(line.slice(7))}</h6>`); continue; }
    if (line.startsWith("##### ")) { closeLists(); output.push(`<h5>${inlineMarkdown(line.slice(6))}</h5>`); continue; }
    if (line.startsWith("#### ")) { closeLists(); output.push(`<h4>${inlineMarkdown(line.slice(5))}</h4>`); continue; }
    if (line.startsWith("### ")) { closeLists(); output.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`); continue; }
    if (line.startsWith("## ")) { closeLists(); output.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`); continue; }
    if (line.startsWith("# ")) { closeLists(); output.push(`<h1>${inlineMarkdown(line.slice(2))}</h1>`); continue; }
    if (/^\s*> ?/.test(line)) { closeLists(); output.push(`<blockquote>${inlineMarkdown(line.replace(/^\s*> ?/, ""))}</blockquote>`); continue; }
    if (/^\s*[-*+] /.test(line)) { if (inOrderedList) { output.push("</ol>"); inOrderedList = false; } if (!inList) { output.push("<ul>"); inList = true; } output.push(`<li>${inlineMarkdown(line.replace(/^\s*[-*+] /, ""))}</li>`); continue; }
    if (/^\s*\d+\. /.test(line)) { if (inList) { output.push("</ul>"); inList = false; } if (!inOrderedList) { output.push("<ol>"); inOrderedList = true; } output.push(`<li>${inlineMarkdown(line.replace(/^\s*\d+\. /, ""))}</li>`); continue; }
    closeLists(); output.push(`<p>${inlineMarkdown(line)}</p>`);
  }
  flushTable(); closeLists();
  if (inCode) output.push(`<pre class="code"><code>${escapeHtml(code.join("\n"))}</code></pre>`);
  return output.join("\n");
}

function markdownToHtml(markdown) {
  if (window.marked) {
    const html = window.marked.parse(markdown, { gfm: true, breaks: false, headerIds: false, mangle: false });
    return window.DOMPurify ? window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true } }) : html;
  }
  return fallbackMarkdownToHtml(markdown);
}

function wrapTables() {
  document.querySelectorAll(".markdown table").forEach((table) => {
    if (table.parentElement?.classList.contains("table-scroll")) return;
    const wrapper = document.createElement("div");
    wrapper.className = "table-scroll";
    table.replaceWith(wrapper);
    wrapper.appendChild(table);
  });
}

function splitIndexCells(row) {
  return row.replace(/^\s*\|?/, "").replace(/\|?\s*$/, "").split("|").map((cell) => cell.trim());
}

function indexChipClass(value) {
  return String(value || "unknown").toLowerCase().replace(/[^a-z0-9-]/g, "") || "unknown";
}

function renderIndexPage(markdown) {
  const lines = markdown.replace(/\r/g, "").split("\n");
  const headerIndex = lines.findIndex((line) => /^\s*\|/.test(line) && line.includes("功能分类") && line.includes("代码入口"));
  if (headerIndex < 0) return `<div class="markdown">${markdownToHtml(markdown)}</div>`;

  const headers = splitIndexCells(lines[headerIndex]);
  const rows = lines.slice(headerIndex + 2)
    .filter((line) => /^\s*\|/.test(line) && !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line))
    .map(splitIndexCells);
  const column = (name) => headers.findIndex((header) => header === name);
  const categoryColumn = column("功能分类");
  const featureColumn = column("细分功能");
  const complexityColumn = column("复杂度");
  const statusColumn = column("状态");
  const sourceColumn = column("代码入口");

  const tableRows = rows.map((row) => {
    const feature = row[featureColumn] || "";
    const link = feature.match(/^\[([\s\S]+?)\]\(([\s\S]+?)\)$/);
    const featureLabel = link ? link[1] : feature;
    const source = (row[sourceColumn] || "").split(/<br\s*\/?\s*>/i).map((entry) => entry.trim()).filter(Boolean);
    const sourceHtml = source.length ? source.map((entry) => `<div>${inlineMarkdown(entry)}</div>`).join("") : "暂无代码入口";
    const complexity = row[complexityColumn] || "unknown";
    const status = row[statusColumn] || "unknown";
    return `<tr>
      <td class="index-category">${inlineMarkdown(row[categoryColumn] || "")}</td>
      <td>${link ? `<button class="index-feature-link" data-path="${escapeHtml(link[2])}">${inlineMarkdown(featureLabel)}</button>` : inlineMarkdown(featureLabel)}</td>
      <td><span class="complexity-chip chip-${indexChipClass(complexity)}">${escapeHtml(complexity)}</span></td>
      <td><span class="status-chip status-${indexChipClass(status)}">${escapeHtml(status)}</span></td>
      <td><details class="index-source"><summary>查看代码入口</summary><div>${sourceHtml}</div></details></td>
    </tr>`;
  }).join("");

  return `<section class="index-dashboard">
    <div class="index-hero"><p class="index-kicker">PROJECT PRD</p><h2>项目需求基线索引</h2><p>按功能分类快速浏览当前项目的需求基线、实现状态与代码入口。</p></div>
    <div class="index-table-wrap"><table class="index-table"><thead><tr><th>功能分类</th><th>细分功能</th><th>复杂度</th><th>状态</th><th>代码入口</th></tr></thead><tbody>${tableRows || '<tr><td colspan="5" class="muted">暂无索引条目</td></tr>'}</tbody></table></div>
  </section>`;
}

function bindIndexLinks() {
  document.querySelectorAll(".index-feature-link").forEach((button) => {
    button.addEventListener("click", () => openPrd(button.dataset.path));
  });
}

function bindMarkdownLinks(currentPath) {
  document.querySelectorAll(".markdown a[href]").forEach((link) => {
    const href = link.getAttribute("href") || "";
    if (!href.toLowerCase().split(/[?#]/, 1)[0].endsWith(".md")) return;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      try {
        const resolved = new URL(href, `http://project.local/${currentPath}`).pathname.replace(/^\/+/, "");
        openPrd(decodeURIComponent(resolved));
      } catch (error) {
        console.warn("Markdown link resolve failed", error);
      }
    });
  });
}

function rewriteMarkdownImages(currentPath) {
  document.querySelectorAll(".markdown img[src]").forEach((image) => {
    const source = image.getAttribute("src") || "";
    image.setAttribute("src", resolveImageSource(source, currentPath, window.location.href));
  });
}

function createMermaidCard(codeNode) {
  const source = codeNode.textContent || "";
  const card = document.createElement("section");
  card.className = "mermaid-card";
  const graph = document.createElement("div");
  graph.className = "mermaid";
  graph.dataset.mermaidSource = source;
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = "查看 Mermaid 源码";
  const pre = document.createElement("pre");
  pre.className = "code mermaid-code";
  const sourceCode = document.createElement("code");
  sourceCode.textContent = source;
  pre.appendChild(sourceCode); details.append(summary, pre); card.append(graph, details);
  codeNode.parentElement.replaceWith(card);
  return graph;
}

async function renderMermaid() {
  const blocks = [...document.querySelectorAll(".mermaid[data-mermaid-source]")];
  document.querySelectorAll("pre > code.language-mermaid, pre > code.lang-mermaid").forEach(codeNode => blocks.push(createMermaidCard(codeNode)));
  if (!blocks.length) return;
  if (!window.mermaid) {
    blocks.forEach(block => { block.textContent = "Mermaid 渲染库未加载，请展开源码查看。"; });
    return;
  }
  blocks.forEach(block => { block.textContent = block.dataset.mermaidSource || block.textContent || ""; });
  window.mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "base", themeVariables: {
    primaryColor: "#eef0ff", primaryTextColor: "#20284a", primaryBorderColor: "#7477e8", lineColor: "#7477e8"
  }});
  try { await window.mermaid.run({ nodes: blocks }); }
  catch (error) { blocks.forEach(block => { block.innerHTML = `<div class="mermaid-error">Mermaid 渲染失败，请展开源码查看。</div>`; }); console.warn("Mermaid render failed", error); }
}

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`请求失败：${response.status}`);
  return response.json();
}

function renderTree() {
  const query = document.querySelector("#search").value.trim().toLowerCase();
  const groups = new Map();
  state.items.filter(item => `${item.title} ${item.name} ${item.prd_id} ${item.category}`.toLowerCase().includes(query))
    .forEach(item => { if (!groups.has(item.category)) groups.set(item.category, []); groups.get(item.category).push(item); });
  document.querySelector("#tree").innerHTML = `<button id="index-link" class="index-link ${state.showingIndex ? "active" : ""}">⌂ <span>PRD 总览</span><small>INDEX</small></button>` + ([...groups.entries()].map(([category, items]) => `
    <section class="group"><h3>${escapeHtml(category)}</h3>${items.map(item => `
      <button class="prd-link ${state.active === item.path ? "active" : ""}" data-path="${escapeHtml(item.path)}">
        <span class="prd-name">${escapeHtml(item.name || item.title)}</span><small class="complexity-chip chip-${escapeHtml(item.complexity || "unknown")}">${escapeHtml(item.complexity || "PRD")}</small>
      </button>`).join("")}</section>`).join("") || '<p class="muted">没有匹配的 PRD。</p>');
  document.querySelector("#index-link").addEventListener("click", openIndex);
  document.querySelectorAll(".prd-link").forEach(button => button.addEventListener("click", () => openPrd(button.dataset.path)));
}

async function renderDocument(path, documentText) {
  const content = document.querySelector("#content");
  const parts = splitFrontmatter(documentText);
  const isIndex = path === "INDEX.md";
  content.innerHTML = `<div class="document-meta"><span>${escapeHtml(path)}</span><button id="refresh">刷新</button></div>${isIndex ? renderIndexPage(parts.body) : `${parts.metadata ? `<details class="metadata"><summary>文档元数据</summary><pre>${escapeHtml(parts.metadata)}</pre></details>` : ""}<div class="markdown">${markdownToHtml(parts.body)}</div>`}`;
  if (isIndex) bindIndexLinks();
  else { wrapTables(); bindMarkdownLinks(path); rewriteMarkdownImages(path); }
  document.querySelector("#refresh").addEventListener("click", () => state.showingIndex ? openIndex() : openPrd(state.active));
  if (!isIndex) await renderMermaid();
}

async function openIndex() {
  state.showingIndex = true; state.active = ""; renderTree();
  const content = document.querySelector("#content"); content.innerHTML = '<div class="loading">正在读取 INDEX…</div>';
  try { const response = await fetch(apiUrl("index")); if (!response.ok) throw new Error("INDEX 读取失败"); await renderDocument("INDEX.md", await response.text()); }
  catch (error) { content.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`; }
}

async function openPrd(path) {
  state.showingIndex = false; state.active = path; renderTree();
  const content = document.querySelector("#content"); content.innerHTML = '<div class="loading">正在读取 PRD…</div>';
  try { const response = await fetch(apiUrl(`prd?path=${encodeURIComponent(path)}`)); if (!response.ok) throw new Error("PRD 读取失败"); await renderDocument(path, await response.text()); }
  catch (error) { content.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`; }
}

async function boot() {
  try {
    const [summary, index] = await Promise.all([getJson(apiUrl("summary")), getJson(apiUrl("prds"))]);
    state.items = index.items || [];
    document.querySelector("#project-title").textContent = `${summary.project_name || "项目"} 项目需求基线`;
    document.title = `${summary.project_name || "项目"} 项目需求基线`;
    document.querySelector("#summary").textContent = `${summary.prd_count || state.items.length} 个 PRD · schema v${summary.format_version || "?"}`;
    renderTree(); openIndex();
  } catch (error) { document.querySelector("#summary").textContent = error.message; }
}

document.querySelector("#search").addEventListener("input", renderTree);
boot();
