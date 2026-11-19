(function exposeProjectPrdMarkdown(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.ProjectPrdMarkdown = api;
}(typeof globalThis === "object" ? globalThis : this, () => {
  const externalSourcePattern = /^(?:[a-z][a-z\d+.-]*:|\/\/|\/|#)/i;

  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));

  function inlineMarkdown(value) {
    let html = escapeHtml(value);
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, url) => `<img src="${url}" alt="${alt}">`);
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, url) => `<a href="${url}">${label}</a>`);
    return html;
  }

  function resolveImageSource(source, currentPath, viewerUrl) {
    if (!source || externalSourcePattern.test(source)) return source;
    try {
      const documentUrl = new URL("http://project.local/");
      documentUrl.pathname = `/${currentPath}`;
      const resolved = new URL(source, documentUrl);
      const assetUrl = new URL("api/asset", viewerUrl);
      assetUrl.searchParams.set("path", decodeURIComponent(resolved.pathname.replace(/^\/+/, "")));
      assetUrl.hash = resolved.hash;
      return assetUrl.href;
    } catch (error) {
      console.warn("Markdown image resolve failed", error);
      return source;
    }
  }

  return { inlineMarkdown, resolveImageSource };
}));
