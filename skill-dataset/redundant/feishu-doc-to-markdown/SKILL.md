---
name: feishu-doc-to-markdown
description: 把飞书文档导出为本地 Markdown，并把文档里的图片、画板、表格、源码块一并下载到本地嵌入到Markdown中，使用飞书官方CLI，本企业免审批（包含配置指引）。
author: litao
version: 1.0.0
---

# 飞书文档转 Markdown

## 概览

把飞书文档与相关资源(图片、白板)导出成本地 Markdown

- `标题名.md`
- `assets/标题名/`

先完成 `lark-cli` 与相关 skill 的安装、配置和登录，再用 `lark-cli` 拉取文档并下载媒体资源，最后用 `scripts/export_feishu_doc.py` 把飞书风格的 Markdown 规范化为标准 Markdown。

## 前置条件

- 首次使用前，先完成 `lark-cli` 安装、配套 skill 安装、配置初始化和登录授权
- 详细步骤见 `references/setup.md`
- 如果当前环境未完成这些准备，不要直接开始导出
- 运行命令时，使用当前系统可用的 Python 命令，并以相对路径或当前环境中的实际技能目录路径调用 `scripts/export_feishu_doc.py`

## 相关 skill

开始执行前，优先按下面顺序理解依赖：

1. `lark-shared`：必读，用于处理配置、认证、`--as user` / `--as bot`、权限不足问题
2. `lark-doc`：必读，用于 `docs +fetch` 和 `docs +media-download`
3. `lark-wiki`：当输入是 `wiki` 链接时再读

对于文档导出，默认优先使用 `--as user`，因为大多数用户文档和知识库节点都属于用户侧资源。

## 工作流

### 1. 先确认环境已完成安装和登录

在真正导出前，先确认：

- `lark-cli` 命令存在
- `lark-cli` 配套 skills 已安装
- 已按 `references/setup.md` 完成 `config init --new`
- 已按 `references/setup.md` 完成 `auth login --recommend` 或等效授权
- `lark-cli auth status` 能返回可用身份

如果这些条件不满足，先返回到“前置条件”部分补齐。

### 2. 确认源文档

- 如果是 `wiki` 链接，先用 `lark-cli wiki spaces get_node --params '{"token":"..."}' --as user` 解析出真实文档 token。
- 只有当 `obj_type` 是 `docx` 或 `doc` 时才继续。
- 如果本来就是 `docx` / `doc` 链接，直接使用 URL 或 token。

如果在认证或权限上失败，回看 `lark-shared`、`lark-doc`、`lark-wiki` 这三个 skill。

### 3. 拉取文档 JSON

运行：

```text
lark-cli docs +fetch --doc "<url-or-token>" --as user > ./temp/doc-fetch.json
```

这里需要的是原始 `docs +fetch` JSON，而不只是抽取出来的 Markdown 文本。
第一次抓取时先落到 `./temp/doc-fetch.json` 即可；后续转换脚本会根据文档标题把它规范成 `./temp/标题名.doc-fetch.json`。

### 4. 生成转换清单

使用当前系统可用的 Python 命令执行本技能目录中的 `scripts/export_feishu_doc.py`：

```text
<python> <skill-dir>/scripts/export_feishu_doc.py --input ./temp/doc-fetch.json --output-dir .
```

其中：

- Windows 常见的 Python 命令是 `py -3` 或 `python`
- macOS / Linux 常见的 Python 命令是 `python3` 或 `python`
- `<skill-dir>` 需要替换成当前技能目录的实际路径，或改成当前环境下可直接访问脚本的相对路径

脚本会输出：

- `标题名.md`
- `temp/标题名.doc-fetch.json`
- `temp/标题名.export.json`
- 如果不存在则创建 `assets/标题名/`

其中 `temp/标题名.export.json` 会按顺序记录媒体项，字段包括：

- `type`：`image` 或 `whiteboard`
- `token`
- `stem`
- `relative_path`

后续下载时要以这个 manifest 为准。

### 5. 按预期文件名下载媒体资源

普通图片：

```text
lark-cli docs +media-download --token "<image-token>" --output "./assets/<标题名>/<image-stem>" --as user
```

白板：

```text
lark-cli docs +media-download --type whiteboard --token "<whiteboard-token>" --output "./assets/<标题名>/<whiteboard-stem>" --as user
```

输出路径必须保持为当前目录下的相对路径，这样 `lark-cli` 才能正确接受。

### 6. 下载后再次运行转换脚本

媒体资源下载完成后，再执行一次相同的 `export_feishu_doc.py` 命令。脚本会扫描 `assets/标题名/` 下真实落盘的扩展名，并把 Markdown 里的图片链接重写为正确的相对路径；同时会继续保证临时文件位于 `./temp/` 下。

## 输出规则

- 默认使用抓取到的文档标题作为输出文件名。
- 需要清理常见文件系统不安全字符，至少覆盖 Windows 非法文件名字符，同时尽量保持标题可读。
- Markdown 中的图片链接必须始终使用相对路径，不能写成绝对路径。
- 导出的 Markdown 文件和 `assets/` 目录必须并排放置。
- 临时产物统一放在 `./temp/`，包括 `标题名.doc-fetch.json` 和 `标题名.export.json`。

## 支持的转换

如果需要查看精确的标签映射，读取 `references/mapping.md`。

当前版本支持：

- `mention-doc` -> 飞书超链接
- `lark-table` -> Markdown 表格
- `<image .../>` -> Markdown 图片引用
- `<whiteboard .../>` -> Markdown 图片引用
- 像 `<text ...>` 这样的简单包裹标签 -> 仅保留内部文本

常见安装、配置和登录问题见 `references/setup.md`。

## 验证

导出后先检查是否还有未转换的飞书标签：

```text
rg -n "<(whiteboard|image|mention-doc|text|lark-table|lark-tr|lark-td)\b" "./标题名.md"
```

期望结果：没有匹配。

再检查图片引用是否都能落到真实文件：

```text
<python> -c "import pathlib,re; root=pathlib.Path('.'); text=pathlib.Path('./标题名.md').read_text(encoding='utf-8'); refs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text); missing=[ref for ref in refs if not (root / ref).exists()]; print({'image_refs': len(refs), 'missing': len(missing)})"
```

期望结果：`missing` 为 `0`。

## 备注

- 这个技能暂时不处理附件，也不支持批量导出。
- 如果 `wiki` 节点最终解析成 `sheet`、`bitable` 等非文档类型，应停止当前流程，改用对应技能，不要强行导出成 Markdown。
- 如果转换后仍残留未支持的飞书标签，检查原始抓取 JSON，并在交付前扩展 `scripts/export_feishu_doc.py`。
