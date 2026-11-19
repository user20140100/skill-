---
name: json-format
description: 处理 JSON 文件的格式化、压缩、转义和去转义操作，支持自然语言和命令行两种调用方式
version: 2.1.0
author: sulianzhang
tags:
  - json
argument-hint: <operation> <file-path> [output-path] 或自然语言描述
---

# JSON 处理工具

对 JSON 文件执行格式化（校验）、压缩、转义、去转义操作。

## 使用方式

### 方式一：命令行格式（精确控制）

```
/json-format <operation> <file-path> [output-path]
```

### 方式二：自然语言（灵活表达）

```
/json-format 把 data.json 压缩一下
/json-format 格式化当前目录的 config.json
/json-format 将 api-response.json 转义后保存到 escaped.txt
/json-format 帮我校验 package.json 的语法
```

### 支持的操作

| 操作 | 别名 | 说明 |
|------|------|------|
| `format` | `validate` | 校验语法并美化输出（2 空格缩进） |
| `compress` | `minify` | 移除所有空白，生成紧凑格式 |
| `escape` | - | 将 JSON 转为可嵌入字符串的转义格式 |
| `unescape` | - | 将转义字符串还原为正常 JSON |

## 实现步骤

当用户调用此 SKILL 时，执行以下步骤：

### 步骤 1：解析用户输入

判断用户输入的格式类型：

**情况 A：命令行格式**（第一个参数是操作关键词）
- 第一个参数是 `format`/`validate`/`compress`/`minify`/`escape`/`unescape` 之一
- 直接提取：`operation`、`file-path`、`output-path`（可选）

**情况 B：自然语言格式**（包含描述性文本）
- 用户输入包含自然语言描述，如"把...压缩"、"格式化..."、"转义..."等
- 需要从自然语言中提取：
  - **操作意图**：识别关键词映射到操作类型
  - **文件路径**：提取文件名或路径
  - **输出路径**：提取"保存到"、"输出到"等后面的路径（可选）

#### 自然语言关键词映射表

| 用户可能说的话 | 映射操作 |
|---------------|---------|
| 格式化、美化、整理、校验、验证、检查语法 | `format` |
| 压缩、精简、minify、单行、去空格 | `compress` |
| 转义、escape、嵌入代码、字符串化 | `escape` |
| 去转义、还原、unescape、反转义 | `unescape` |

#### 文件路径提取规则

- 查找常见文件扩展名：`.json`、`.txt`
- 查找路径模式：`/`、`./`、`../`、文件名
- 如果用户说"当前"、"这个"但未指定文件，询问用户具体文件路径

#### 输出路径提取规则

- 查找"保存到"、"输出到"、"写入"、"存到"等关键词后的路径
- 如果未提及输出路径，则不指定（输出到控制台）

### 步骤 2：确认解析结果（仅自然语言模式）

如果是自然语言输入，向用户确认解析结果：

```
理解您的需求：
- 操作：compress（压缩）
- 输入文件：data.json
- 输出文件：（输出到控制台）

是否正确？
```

如果用户确认，继续执行；如果用户纠正，根据反馈调整参数。

### 步骤 3：获取 skill 目录路径

使用 Bash 工具定位当前 SKILL.md 文件所在目录：

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

如果在 Claude Code 环境中无法获取，使用以下备选方案：
- 检查 `~/.claude/skills/json-format/` 目录
- 检查当前工作目录下的 `skills/json-format/` 目录

### 步骤 4：调用独立 CLI 脚本

使用 Bash 工具执行 `json-format.js` 脚本，传递解析后的参数：

```bash
node "$SKILL_DIR/json-format.js" <operation> <file-path> [output-path]
```

将解析后的参数传递给脚本：
- `<operation>`：操作类型（format/compress/escape/unescape）
- `<file-path>`：输入文件路径
- `[output-path]`：输出文件路径（可选）

### 步骤 5：处理脚本输出

脚本会将结果输出到 stdout 或写入文件：

**情况 A：用户指定了 output-path**
- 脚本自动写入文件
- 向用户显示脚本输出的统计信息（行数、字节数）

**情况 B：用户未指定 output-path**
- 脚本将结果输出到 stdout
- 直接向用户显示结果内容

### 步骤 6：错误处理

如果脚本执行失败（退出码非 0），捕获 stderr 输出并向用户报告错误信息。

常见错误类型：
- 操作类型无效
- 输入文件不存在
- JSON 语法错误
- 转义/去转义失败

## 使用示例

### 命令行格式

```
# 格式化并校验
/json-format format data.json
/json-format validate data.json formatted.json

# 压缩
/json-format compress data.json
/json-format minify data.json data.min.json

# 转义（输出可嵌入代码的字符串）
/json-format escape config.json
/json-format escape config.json escaped.txt

# 去除转义还原
/json-format unescape escaped.txt
/json-format unescape escaped.txt config.json
```

### 自然语言格式

```
# 格式化
/json-format 把 data.json 格式化一下
/json-format 帮我美化 config.json
/json-format 检查 package.json 的语法

# 压缩
/json-format 压缩 data.json
/json-format 把 config.json 变成单行
/json-format 将 api.json 精简后保存到 api.min.json

# 转义
/json-format 把 config.json 转义
/json-format 将 data.json 转义后保存到 escaped.txt
/json-format 把这个 JSON 文件转成可以嵌入代码的格式：settings.json

# 去转义
/json-format 还原 escaped.txt
/json-format 把 escaped.txt 去转义后保存到 config.json
/json-format 反转义这个文件：data.escaped.txt
```

## 技术说明

此 skill 通过调用独立的 `json-format.js` CLI 脚本实现，该脚本：
- 完全独立运行，无需 Claude Code 环境
- 使用 Node.js 原生 API，无外部依赖
- 可直接通过 `node json-format.js` 命令行使用
- 支持相对路径和绝对路径
- 错误信息输出到 stderr，结果输出到 stdout

自然语言解析由 Claude 在 SKILL 层面完成，解析后调用相同的 CLI 脚本。
