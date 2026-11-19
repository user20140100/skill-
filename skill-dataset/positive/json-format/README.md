# json-format

> 独立 CLI 工具 + Claude Code Skill · JSON 文件处理工具

对 JSON 文件执行**格式化（校验）**、**压缩**、**转义**、**去转义**四种操作，无需离开终端，无需额外工具。

**两种使用方式**：
- **独立 CLI**：直接通过 `node json-format.js` 命令使用，无需 Claude Code
- **Claude Code Skill**：在 Claude Code 中通过 `/json-format` 调用，支持命令行和自然语言两种格式

---

## 适用场景

| 场景 | 推荐操作 |
|------|----------|
| 接收到一行压缩的 JSON，想看清楚结构 | `format` |
| 提交接口返回数据前，想验证 JSON 语法是否合法 | `validate` |
| 需要把 JSON 写入环境变量、数据库字段或配置字符串 | `compress` + `escape` |
| 从代码或日志中复制出转义的 JSON 字符串，想还原查看 | `unescape` |
| 准备发布前，想压缩 JSON 文件减小体积 | `compress` / `minify` |
| 写单元测试需要内联 JSON 字符串 | `escape` |
| 收到同事发的转义 JSON，需要还原为可读格式 | `unescape` → `format` |

---

## 安装

### 前置条件

- 已安装 Node.js（`node --version` 验证，系统通常自带）
- （可选）已安装 [Claude Code](https://claude.ai/code) CLI（仅在使用 Skill 方式时需要）

### 方式一：独立 CLI 使用（无需 Claude Code）

直接下载或克隆本项目，即可使用：

```bash
# 下载项目
git clone <repository-url>
cd skills/json-format

# 直接使用（无需安装）
node json-format.js format data.json

# 或添加到 PATH 以便全局使用
chmod +x json-format.js
ln -s "$(pwd)/json-format.js" /usr/local/bin/json-format
# 之后可以直接运行
json-format format data.json
```

### 方式二：作为 Claude Code Skill 安装

**项目级（仅在当前项目中可用）**

将 `skills/json-format/` 目录复制到你的项目的 `.claude/skills/` 目录下：

```bash
# 在你的项目根目录执行
mkdir -p .claude/skills
cp -r /path/to/skills/json-format .claude/skills/
```

**全局（在所有项目中可用）**

将目录复制到全局 skills 目录：

```bash
cp -r /path/to/skills/json-format ~/.claude/skills/
```

安装完成后，在 Claude Code 中执行 `/json-format` 即可调用。

---

## 使用说明

### 独立 CLI 模式

**命令格式**：

```bash
node json-format.js <operation> <file-path> [output-path]
# 或（如果已添加到 PATH）
json-format <operation> <file-path> [output-path]
```

**参数**：

| 参数 | 是否必需 | 说明 |
|------|----------|------|
| `operation` | 必需 | 操作类型：`format`/`validate`/`compress`/`minify`/`escape`/`unescape` |
| `file-path` | 必需 | 输入文件的路径（相对路径或绝对路径） |
| `output-path` | 可选 | 输出文件路径；不填则输出到控制台（stdout） |

**示例**：

```bash
# 格式化并输出到控制台
node json-format.js format data.json

# 格式化并保存到新文件
node json-format.js format data.json data.formatted.json

# 压缩
node json-format.js compress data.json data.min.json

# 转义
node json-format.js escape config.json config.escaped.txt

# 去转义
node json-format.js unescape config.escaped.txt config.json

# 查看帮助
node json-format.js --help
```

### Claude Code Skill 模式

Claude Code Skill 支持两种调用格式：

#### 格式一：命令行格式（精确控制）

```
/json-format <operation> <file-path> [output-path]
```

**参数**：

| 参数 | 是否必需 | 说明 |
|------|----------|------|
| `operation` | 必需 | 操作类型，见下表 |
| `file-path` | 必需 | 输入文件的路径（相对路径或绝对路径） |
| `output-path` | 可选 | 输出文件路径；不填则输出到控制台 |

**示例**：

```
# 格式化
/json-format format data.json

# 压缩并保存
/json-format compress data.json data.min.json
```

#### 格式二：自然语言格式（灵活表达）

直接用自然语言描述你的需求，Claude 会自动解析并执行：

```
/json-format 把 data.json 压缩一下
/json-format 格式化当前目录的 config.json
/json-format 将 api-response.json 转义后保存到 escaped.txt
/json-format 帮我校验 package.json 的语法
/json-format 把这个 JSON 文件变成单行：settings.json
/json-format 还原 escaped.txt 的内容
```

**自然语言关键词识别**：

| 你可以说 | 对应操作 |
|---------|---------|
| 格式化、美化、整理、校验、验证、检查语法 | `format` |
| 压缩、精简、minify、单行、去空格 | `compress` |
| 转义、escape、嵌入代码、字符串化 | `escape` |
| 去转义、还原、unescape、反转义 | `unescape` |

Claude 会自动从你的描述中提取：
- 操作类型（根据关键词）
- 输入文件路径（识别 `.json`、`.txt` 等文件）
- 输出文件路径（识别"保存到"、"输出到"等关键词）

### 支持的操作

| 操作 | 别名 | 说明 |
|------|------|------|
| `format` | `validate` | 校验 JSON 语法，并美化输出（2 空格缩进） |
| `compress` | `minify` | 移除所有空白字符，生成紧凑的单行格式 |
| `escape` | — | 将 JSON 转为可嵌入字符串的转义格式（纯转义字符串，不含外层引号） |
| `unescape` | — | 将转义字符串还原为正常 JSON，自动格式化输出 |

---

## 使用示例

### 独立 CLI 示例

#### 格式化 / 校验

```bash
# 格式化后输出到控制台
node json-format.js format data.json

# 格式化并保存到新文件
node json-format.js format data.json data.formatted.json

# validate 是 format 的别名
node json-format.js validate data.json
```

```

**输入** `data.json`：
```json
{"name":"张三","age":30,"tags":["dev","pm"]}
```

**输出**：
```json
{
  "name": "张三",
  "age": 30,
  "tags": [
    "dev",
    "pm"
  ]
}
```

#### 压缩

```bash
# 压缩后输出到控制台
node json-format.js compress data.json

# 压缩并保存到新文件
node json-format.js minify data.json data.min.json
```

**输入**（格式化后的多行 JSON）→ **输出**（单行紧凑格式）：
```json
{"name":"张三","age":30,"tags":["dev","pm"]}
```

#### 转义

```bash
# 转义后输出到控制台（适合复制粘贴到代码中）
node json-format.js escape config.json

# 转义并保存到文件
node json-format.js escape config.json config.escaped.txt
```

**输入** `config.json`：
```json
{
  "host": "localhost",
  "port": 8080
}
```

**输出**（可直接放入代码字符串变量中）：
```
{\n  \"host\": \"localhost\",\n  \"port\": 8080\n}
```

#### 去转义

```bash
# 还原转义字符串并输出到控制台
node json-format.js unescape config.escaped.txt

# 还原并保存到文件
node json-format.js unescape config.escaped.txt config.json
```

**输入**（转义字符串）→ **输出**（还原的格式化 JSON）：
```json
{
  "host": "localhost",
  "port": 8080
}
```

### Claude Code Skill 示例

#### 命令行格式

**格式化**：
```
/json-format format data.json
/json-format format data.json data.formatted.json
```

**压缩**：
```
/json-format compress data.json
/json-format minify data.json data.min.json
```

**转义**：
```
/json-format escape config.json
/json-format escape config.json config.escaped.txt
```

**去转义**：
```
/json-format unescape config.escaped.txt
/json-format unescape config.escaped.txt config.json
```

#### 自然语言格式

**格式化**：
```
/json-format 把 data.json 格式化一下
/json-format 帮我美化 config.json
/json-format 检查 package.json 的语法
/json-format 整理一下 api-response.json
```

**压缩**：
```
/json-format 压缩 data.json
/json-format 把 config.json 变成单行
/json-format 将 api.json 精简后保存到 api.min.json
/json-format 去掉 settings.json 的空格
```

**转义**：
```
/json-format 把 config.json 转义
/json-format 将 data.json 转义后保存到 escaped.txt
/json-format 把这个 JSON 文件转成可以嵌入代码的格式：settings.json
/json-format 字符串化 api-config.json
```

**去转义**：
```
/json-format 还原 escaped.txt
/json-format 把 escaped.txt 去转义后保存到 config.json
/json-format 反转义这个文件：data.escaped.txt
/json-format 把 log-output.txt 还原成正常 JSON
```

---

## 使用技巧

### 技巧 1：自然语言让操作更直观

不需要记住命令参数，直接说出你的需求：

```
# 传统方式
/json-format compress data.json data.min.json

# 自然语言方式
/json-format 把 data.json 压缩后保存到 data.min.json
```

### 技巧 2：组合操作——压缩后再转义

需要把 JSON 嵌入环境变量时，通常希望它是单行且转义的：

```bash
# CLI 模式
node json-format.js compress config.json config.min.json
node json-format.js escape config.min.json

# Skill 命令行格式
/json-format compress config.json config.min.json
/json-format escape config.min.json

# Skill 自然语言格式
/json-format 先把 config.json 压缩，然后转义
```

### 技巧 3：用 validate 做快速语法检查

在提交代码或配置前，快速确认 JSON 是否合法：

```bash
# CLI 模式
node json-format.js validate package.json

# Skill 命令行格式
/json-format validate package.json

# Skill 自然语言格式
/json-format 检查 package.json 的语法
/json-format 验证一下 config.json 是否合法
```

如果语法有误，会报告具体的错误位置和原因（如 `Unexpected token ',' at position 42`），帮助你快速定位问题。

### 技巧 4：转义结果直接复制到代码

`escape` 输出的是**纯转义字符串**（不含外层引号），可以直接粘贴到语言的字符串字面量中：

```python
# Python
json_str = "{\n  \"name\": \"张三\"\n}"

# JavaScript
const jsonStr = "{\n  \"name\": \"张三\"\n}";
```

### 技巧 5：unescape 支持两种格式输入

从代码或日志中复制出的转义字符串，可能有引号也可能没有，`unescape` 操作对两种格式都兼容：

```bash
# 有外层引号的文件内容："{\"name\":\"张三\"}"
# 无外层引号的文件内容：{\"name\":\"张三\"}
# 两种都可以正常处理
node json-format.js unescape escaped.txt

# 自然语言也可以
/json-format 还原 escaped.txt
```

### 技巧 6：CLI 模式管道操作

独立 CLI 支持标准输入输出，可以与其他命令组合：

```bash
# 格式化后通过管道传递给其他工具
node json-format.js format data.json | less

# 从 API 获取 JSON 并格式化
curl https://api.example.com/data | node json-format.js format /dev/stdin
```

### 技巧 7：通过相对路径处理深层目录文件

```bash
# CLI 模式
node json-format.js format src/config/app.json
node json-format.js compress dist/assets/data.json dist/assets/data.min.json

# Skill 命令行格式
/json-format format src/config/app.json
/json-format compress dist/assets/data.json dist/assets/data.min.json

# Skill 自然语言格式
/json-format 格式化 src/config/app.json
/json-format 压缩 dist/assets/data.json 并保存到 dist/assets/data.min.json
```

---

## 技术说明

### 架构设计

- **核心逻辑**：所有 JSON 处理逻辑实现在 `json-format.js` 独立脚本中
- **零依赖**：仅使用 Node.js 原生 API（`fs`、`path`、`JSON`）
- **三种模式**：
  - 独立 CLI：直接运行脚本，结果输出到 stdout 或文件
  - Claude Code Skill（命令行格式）：SKILL.md 调用 `json-format.js` 脚本
  - Claude Code Skill（自然语言格式）：Claude 解析自然语言后调用 `json-format.js` 脚本

### 自然语言解析

自然语言解析由 Claude 在 SKILL 层面完成：
1. 识别操作意图（格式化、压缩、转义、去转义）
2. 提取文件路径（输入和输出）
3. 向用户确认解析结果
4. 调用相同的 CLI 脚本执行操作

### 为什么这样设计？

1. **通用性**：核心脚本无需 Claude Code 也能使用，适合脚本化、CI/CD 集成
2. **可维护性**：核心逻辑集中在一个文件，易于测试和更新
3. **灵活性**：支持精确的命令行控制，也支持自然语言的便捷表达
4. **一致性**：无论哪种调用方式，底层都是同一个脚本，行为完全一致

---

## 错误说明

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `Unexpected token ...` | JSON 语法错误 | 根据提示的位置修复语法 |
| 文件不存在 | 路径有误 | 检查路径是否正确，注意相对路径的基准目录 |
| 操作类型无效 | 拼写错误 | 使用 `format`/`compress`/`escape`/`unescape` 之一 |
| unescape 后非有效 JSON | 输入内容不是合法的转义 JSON | 确认输入文件来源于 `escape` 操作的结果 |

---

## 文件说明

```
skills/json-format/
├── json-format.js    # 独立 CLI 脚本（核心实现，可单独使用）
├── SKILL.md          # Claude Code Skill 定义文件（调用 json-format.js）
├── README.md         # 本说明文档
└── examples/
    └── sample.json   # 示例 JSON 文件，可用于测试
```

### 快速测试

**独立 CLI 模式**：

```bash
cd skills/json-format

# 使用示例文件测试格式化
node json-format.js format examples/sample.json

# 使用示例文件测试压缩
node json-format.js compress examples/sample.json

# 使用示例文件测试转义
node json-format.js escape examples/sample.json
```

**Claude Code Skill 模式**：

```
# 使用示例文件测试格式化
/json-format format skills/json-format/examples/sample.json

# 使用示例文件测试压缩
/json-format compress skills/json-format/examples/sample.json
```

---

## 版本历史

| 版本 | 说明 |
|------|------|
| 2.1.0 | 新增自然语言调用支持，可以用"把 data.json 压缩"等自然语言调用 skill |
| 2.0.0 | 重构为独立 CLI + Skill 双模式架构，核心逻辑抽取到 json-format.js |
| 1.0.0 | 初始版本，支持 format / compress / escape / unescape |
