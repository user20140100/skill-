---
name: project-prd-serve
description: 启动只读本地服务，通过同一个 baseUrl 和端口按项目名路径查看一个或多个项目的 project-prd 目录、PRD Markdown、规则矩阵、源码证据和 Mermaid 流程图；不为每个 PRD 生成独立前端页面，也不修改 PRD 文件。
version: 1.2.0
author: yangyuebin
triggers:
  - /project-prd-serve
  - 启动 project-prd 服务
  - 查看项目 PRD 页面
  - 打开项目 PRD 可视化页面
  - 浏览 project-prd
requires:
  - python3
---

# Project PRD Serve

启动一个只读的本地 Web 服务，动态读取当前项目的 `.project-prd` 工作区，并用通用 Viewer 展示 PRD。服务不生成每个 PRD 的 HTML 文件，前端资源只属于本 skill。

## 使用前提

- 当前目录是项目根目录，且存在已完成初始化的 `.project-prd/manifest.json`。
- 使用 Python 3.9+。
- 服务默认只监听 `127.0.0.1`，不会向局域网暴露项目内容。

## 启动

```bash
python3 <本 skill 目录>/scripts/serve.py \
  --project-root <项目根目录> \
  --host 127.0.0.1 \
  --port 8765
```

单项目启动后仍可访问 `http://127.0.0.1:8765/`，同时也支持规范化入口 `http://127.0.0.1:8765/<项目目录名>/`。

同时查看多个项目时，重复传入 `--project-root`，所有项目共享同一个 host 和端口：

```bash
python3 <本 skill 目录>/scripts/serve.py \
  --project-root <项目 A 根目录> \
  --project-root <项目 B 根目录> \
  --host 127.0.0.1 \
  --port 8765
```

根入口 `http://127.0.0.1:8765/` 会显示项目列表，各项目入口为：

```text
http://127.0.0.1:8765/<项目目录名>/
```

若多个项目的目录同名，必须显式指定唯一入口名：

```bash
python3 <本 skill 目录>/scripts/serve.py \
  --project demo-app=<项目 A 根目录> \
  --project demo-service=<项目 B 根目录>
```

## 行为边界

- Viewer 运行时读取 `.project-prd/INDEX.md`、`manifest.json` 和 PRD Markdown，不复制或改写 PRD。
- 多项目模式只共享 Viewer 进程与端口；每个项目仍独立读取自己的 `.project-prd`，API 和静态资源均限制在对应项目名前缀内。
- PRD 修改仍必须使用 `project-prd-edit`；本服务不提供写入 API。
- API 只允许读取 `.project-prd` 内的 Markdown、manifest 和受支持图片资源，拒绝路径穿越、越界符号链接及隐藏审计目录访问。
- Markdown 中的相对图片路径按当前 PRD 文件目录解析；支持 SVG、PNG、JPEG、GIF、WebP、AVIF、BMP 和 ICO，外部图片 URL 保持原样。
- PRD 内容优先使用固定版本的 Marked GFM 渲染，支持表格、标题、列表、任务列表、引用、链接、代码块和分隔线；CDN 不可用时回退到内置解析器。
- Mermaid 代码块优先渲染为流程图，渲染失败时保留可展开的 Mermaid 源码。
