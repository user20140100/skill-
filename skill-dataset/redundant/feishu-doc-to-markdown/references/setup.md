# 环境准备

本文件描述 `feishu-doc-to-markdown` 技能依赖的安装、配置与登录步骤。

官方参考：

- `lark-cli` Quick Start (AI Agent): `https://github.com/larksuite/cli/tree/main?tab=readme-ov-file#quick-start-ai-agent`

## 前置条件

开始前确认：

- 已安装 `Node.js`，并且 `npm` / `npx` 可用
- 已安装 `Python 3`，因为要运行 `scripts/export_feishu_doc.py`
- 当前 AI Agent 环境可加载 `lark-cli` 对应 skill

本文中的 `<python>` 表示当前平台可用的 Python 命令：

- Windows：使用python
- macOS / Linux：优先用 `python3`，没有时再用 `python`

## 首次使用

### 1. 安装 `lark-cli`

推荐使用 npm：

```text
npm install -g @larksuite/cli
```

### 2. 安装 `lark-cli` 配套 skills

```text
npx skills add larksuite/cli -y -g
```

本技能常用依赖：

- `lark-shared`
- `lark-doc`
- `lark-wiki`

这些 skill 都来自同一个 `lark-cli` skill 包；其中 `lark-shared` 会被其他 `lark-*` skill 复用。

### 3. 初始化配置

AI Agent 场景优先使用：

```text
lark-cli config init --new
```

该命令应由 Agent 以后台方式发起。命令会输出浏览器授权链接；Agent 需要提取链接并发给用户，由用户在浏览器中完成配置。

### 4. 登录授权

推荐先执行：

```text
lark-cli auth login --domain docs,wiki
```

该命令同样应由 Agent 以后台方式发起，并把授权链接发给用户。

如果后续执行命令时提示缺少 scope，再根据报错里的 `permission_violations`、`hint` 或 `console_url` 做增量授权或权限开通；详细规则以 `lark-shared` 为准。

### 5. 验证环境

至少验证：

```text
lark-cli auth status
<python> --version
```

如果 `lark-cli auth status` 显示未登录，或 `<python> --version` 不可用，不要继续导出流程，先修复环境。

## 常见失败点

- `lark-cli` 未安装：执行 `npm install -g @larksuite/cli`
- 配套 skills 未安装：执行 `npx skills add larksuite/cli -y -g`
- 只安装了 CLI，但没有初始化配置：执行 `lark-cli config init --new`
- 已初始化但未登录：执行 `lark-cli auth login --domain docs,wiki`
- 用了 `--as bot` 导致看不到用户文档：优先改用 `--as user`
