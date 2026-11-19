import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const {
  inlineMarkdown,
  resolveImageSource,
} = require("../assets/project-skills/project-prd-serve/assets/web/markdown.js");

test("fallback inline markdown renders image syntax as an img element", () => {
  assert.equal(
    inlineMarkdown("![钢笔对比](../res/ink.svg)"),
    '<img src="../res/ink.svg" alt="钢笔对比">',
  );
});

test("fallback inline markdown keeps ordinary links and escapes image attributes", () => {
  assert.equal(
    inlineMarkdown('![<对比>](../res/a&b.svg) 与 [详情](文档.md)'),
    '<img src="../res/a&amp;b.svg" alt="&lt;对比&gt;"> 与 <a href="文档.md">详情</a>',
  );
});

test("relative image source resolves from the current Chinese PRD path", () => {
  assert.equal(
    resolveImageSource(
      "../res/图.svg#detail",
      "显示渲染/钢笔与压感笔渲染.md",
      "http://127.0.0.1:8765/MXBoard/",
    ),
    "http://127.0.0.1:8765/MXBoard/api/asset?path=res%2F%E5%9B%BE.svg#detail",
  );
});

test("non-relative image sources remain unchanged", () => {
  const sources = [
    "https://example.com/image.png",
    "http://example.com/image.png",
    "//cdn.example.com/image.png",
    "/shared/image.png",
    "data:image/png;base64,AA==",
    "blob:http://127.0.0.1/id",
    "#inline-symbol",
    "",
  ];

  for (const source of sources) {
    assert.equal(
      resolveImageSource(
        source,
        "显示渲染/钢笔.md",
        "http://127.0.0.1:8765/MXBoard/",
      ),
      source,
    );
  }
});
