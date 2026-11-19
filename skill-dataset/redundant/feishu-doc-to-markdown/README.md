# feishu-doc-to-markdown

把飞书文档导出为本地 Markdown，并把文档里的图片、画板、表格、源码块一并下载到本地嵌入到Markdown中，使用飞书官方CLI，本企业免审批（包含配置指引）。

## 功能

支持以下文档资源：

- 正文
- 图片
- 画板
- 表格
- 源码块

当前版本不会下载以下内容：

- 附件
- 内嵌电子表格本体；`sheet` 仅会在 Markdown 中转换为提示文本
- 非文档类型的 `wiki` 节点，例如 `sheet`、`bitable` 等


## 工作原理
核心依赖飞书官方 CLI：[lark-cli](https://github.com/larksuite/cli)

1. AI Agent 调用 `lark-cli` 去读取飞书文档内容
2. 把拿到的正文、图片、画板等信息导出到本地
3. 再整理成标准 Markdown，并把资源链接改成本地相对路径

## 使用方法

首次使用需按 AI SKILL 指引完成配置，仅需3分钟。

Claude:
```
/feishu-doc-to-markdown 把飞书文档转为markdown，https://xxx
```

Codex
```
$feishu-doc-to-markdown 把飞书文档转为markdown，https://xxx
```


