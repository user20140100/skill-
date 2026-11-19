---
name: markitdown
description: >-
  使用微软 markitdown 将各类文档(Word/Excel/PPT/PDF/HTML/图片/CSV/JSON 等)转换为
  Markdown。当用户想把文档转成 markdown、提取文档文本内容、转换 docx/xlsx/pptx/pdf/html 文件、读取附件内容时使用。
trigger: >-
  当用户说"转成 markdown"、"markitdown"、"转换文档"、"把 word/pdf/ppt 转
  md"、"提取文档内容"、"读取这个文件的内容"时触发。触发词:markitdown、转 markdown、文档转换、docx to md、pdf to
  md、extract text、提取文本。
author: zhouyujie
version: 0.0.1
---

# markitdown - 文档转 Markdown 工具

微软出品的 markitdown CLI,将多种文件格式转换为 Markdown。支持 Office 文档、PDF、HTML、图片、音频等。

## 前置检查

首次使用前,确认 markitdown 已安装并可执行:

```bash
command -v markitdown >/dev/null 2>&1 && echo "已安装: $(command -v markitdown)" || pip install --user markitdown
```

若已安装会输出路径(本机通常为 `~/Library/Python/3.12/bin/markitdown`)。若提示找不到命令但已安装,需将 `~/Library/Python/3.12/bin` 加入 PATH。

## 默认工作流

当用户提供一个文件或文件路径时,按以下流程转换:

### Step 1: 确认输入文件

确认用户给的文件路径存在且可读。若用户只给文件名,在当前目录或常见位置(桌面、下载、Documents)查找并确认。

### Step 2: 执行转换

默认转换为 Markdown 并保存到文件:

```bash
markitdown "<文件路径>" -o "<输出.md>"
```

若用户只想快速预览不存盘,直接输出到 stdout:

```bash
markitdown "<文件路径>"
```

### Step 3: 输出文件命名

默认取源文件名、扩展名改为 `.md`,保存到与源文件同目录。例:`报告.docx` → `报告.md`。

若用户指定了输出路径或目录,按用户指定保存。若未指定且想保持整洁,可保存到源文件同目录。

### Step 4: 反馈结果

告知用户:
- 输出文件的完整路径
- 内容摘要(开头几行预览,让用户确认转换成功)
- 若内容较长,提示完整内容已写入文件

## 从 stdin 读取(无文件名时)

当输入来自管道或重定向,需用 `-x` 提供扩展名提示:

```bash
cat data.html | markitdown -x html
markitdown < input.xlsx -o output.md
```

## CLI 参考

```bash
markitdown [filename] [options]
```

| 选项 | 说明 |
|------|------|
| `filename` | 输入文件,缺省则从 stdin 读 |
| `-o, --output <file>` | 输出到文件,否则打印到 stdout |
| `-x, --extension <ext>` | stdin 时提示文件扩展名(如 html、pdf、xlsx) |
| `-m, --mime-type <type>` | 提示 MIME 类型 |
| `-c, --charset <charset>` | 提示字符集(如 UTF-8) |
| `-d, --use-docintel` | 用 Azure Document Intelligence 提取(需 endpoint) |
| `-e, --endpoint <url>` | Document Intelligence endpoint |
| `-p, --use-plugins` | 启用第三方插件转换 |
| `--list-plugins` | 列出已安装的第三方插件 |
| `--keep-data-uris` | 保留 base64 图片(默认会截断) |
| `-v, --version` | 查看版本 |
| `-h, --help` | 查看帮助 |

## 支持的格式

- **Word**: .docx
- **PowerPoint**: .pptx
- **Excel**: .xlsx(按 sheet 分段输出)
- **PDF**: .pdf(基础文本提取,扫描件/复杂排版效果有限)
- **HTML**: .html / .htm
- **纯文本/数据**: .txt、.csv、.json、.xml
- **图片**: .jpg / .png 等(需 Document Intelligence 或插件做 OCR)
- **音频**: .mp3 等(需转录服务)
- **压缩包**: .zip(遍历内部文件分别转换)

## 注意事项

- **PDF 效果**:0.1.x 版本对 PDF 是基础文本提取,扫描件、复杂表格、多栏排版效果有限。要更好效果需用 `-d` + `-e` 配合 Azure Document Intelligence。
- **图片内嵌**:默认 base64 data URI 会被截断,需要保留图片数据加 `--keep-data-uris`。
- **中文文件名**:用双引号包裹路径即可正常处理。
- **大文件**:转换结果可能很长,优先用 `-o` 写入文件而非直接打印到 stdout。
- **老版本 .doc/.ppt/.xls**:markitdown 主要支持新版 Office 格式(.docx/.pptx/.xlsx),旧版二进制格式可能需先用其他工具转换。
