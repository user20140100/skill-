// diff-analysis-report 固化片段：飞书文档滚动收集（粘贴进 mcp playwright 的 browser_evaluate 执行）
// 用法：先 browser_navigate 打开飞书文档，再将本文件除首行注释外的整个函数体粘贴为 evaluate 的 function
// 说明：滚动容器 .bear-web-x-container；按 data-block-id 去重；可配合 filename 参数把结果落盘再 Read
async () => {
  const sc = document.querySelector('.bear-web-x-container');
  if (!sc) return 'NO_SCROLLER';
  const seen = new Map();
  const collect = () => {
    document.querySelectorAll('[data-block-id]').forEach(el => {
      const id = el.getAttribute('data-block-id');
      if (!seen.has(id)) {
        const t = (el.innerText || '').trim();
        if (t) seen.set(id, t);
      }
    });
  };
  sc.scrollTop = 0;
  await new Promise(r => setTimeout(r, 500));
  collect();
  let prev = -1;
  for (let i = 0; i < 120; i++) {
    sc.scrollBy(0, 500);
    await new Promise(r => setTimeout(r, 250));
    collect();
    if (sc.scrollTop === prev) break;
    prev = sc.scrollTop;
  }
  await new Promise(r => setTimeout(r, 500));
  collect();
  const lines = [];
  seen.forEach(v => lines.push(v));
  return 'TOTAL_BLOCKS=' + seen.size + '\nSCROLL_END=' + sc.scrollTop + '/' + sc.scrollHeight + '\n---DOC---\n' + lines.join('\n');
}
