# 环境自检与安装

> Step 0 的参考。检测 mcp-windbg / CDB / Python / 符号路径，缺失则安装，并决定走 MCP 还是 CDB CLI。

## 依赖关系

mcp-windbg 是 CDB 的 MCP 封装，底层调用 `cdb.exe`。完整依赖链：

```
Claude Code ──MCP──> mcp-windbg ──subprocess──> cdb.exe ──> dump 文件 / 活进程
```

因此需要：
1. **CDB**（Debugging Tools for Windows）— 必需，MCP 和 CLI 兜底都依赖
2. **Python >=3.10** — mcp-windbg 运行时
3. **mcp-windbg 包** — MCP 封装
4. **符号路径** — 解析栈帧符号
5. **（可选）procdump** — 活进程取 dump 的补充工具

## 检测脚本

一次性检测全部依赖：

```bash
echo "=== Python (找 3.10+) ==="
py -0 2>&1
py -3.11 --version 2>&1 || echo "py -3.11 不可用"

echo "=== mcp-windbg ==="
py -3.11 -m pip show mcp-windbg 2>&1 | head -3 || echo "mcp-windbg 未安装"

echo "=== CDB ==="
for p in "/d/Windows Kits/10/Debuggers/x64/cdb.exe" \
         "/c/Program Files (x86)/Windows Kits/10/Debuggers/x64/cdb.exe" \
         "/c/Program Files/Windows Kits/10/Debuggers/x64/cdb.exe"; do
  [ -f "$p" ] && echo "FOUND: $p"
done
which cdb 2>/dev/null && echo "cdb in PATH"

echo "=== procdump（可选，活进程取 dump）==="
which procdump 2>/dev/null || echo "procdump 未安装（可选，见下文）"

echo "=== 符号路径 ==="
echo "_NT_SYMBOL_PATH=${_NT_SYMBOL_PATH:-<未设置>}"
```

## 缺失处理

### Python <3.10

mcp-windbg 要求 Python >=3.10。本机默认 `python` 可能是 3.9（不满足）。用 py launcher 找 3.10+：

```bash
py -0          # 列出所有已装 Python
py -3.11 ...   # 用 3.11 跑后续命令
```

若系统无 3.10+，需先装 Python 3.11+（用户动作，skill 无法自动完成）。

### mcp-windbg 未安装

用 3.11 安装（不要用默认 3.9，会因 requires-python 失败）：

```bash
py -3.11 -m pip install mcp-windbg
```

验证：

```bash
py -3.11 -m mcp_windbg --help
```

### CDB 未找到

CDB 来自 Debugging Tools for Windows。安装方式：
- Windows SDK 安装时勾选 "Debugging Tools for Windows"
- 或 Microsoft Store 装 WinDbg（含 cdb）

常见路径：`D:\Windows Kits\10\Debuggers\x64\cdb.exe`、`C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe`

### procdump 未安装（可选）

活进程取 hang dump 的补充工具。**非必需**——mcp-windbg 的 `open_windbg_remote` + `send_ctrl_break` 可直接打断活进程，Task Manager 也能零依赖生成转储。装 procdump 只为更灵活的命令行取 dump：

```bash
winget install Sysinternals.Procdump
```

## MCP 注册（用 MCP 工具的前提）

mcp-windbg 是 MCP server，要在 Claude Code 注册才能调用其工具。

### 注册到 ~/.claude.json

在 `mcpServers` 加：

```json
{
  "mcp_windbg": {
    "command": "py",
    "args": ["-3.11", "-m", "mcp_windbg"],
    "env": {
      "_NT_SYMBOL_PATH": "srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
    }
  }
}
```

或用 Claude Code CLI：

```bash
claude mcp add mcp_windbg -- py -3.11 -m mcp_windbg --symbols-path "srv*C:\Symbols*https://msdl.microsoft.com/download/symbols"
```

### ⚠️ 注册后必须重启 Claude Code 会话

MCP server 只在会话启动时加载。注册后需退出并重开 Claude Code，`mcp_windbg` 工具才会出现。

## 模式判定：MCP vs CDB CLI

会话内决定走哪条路：

| 条件 | 模式 | 说明 |
|------|------|------|
| `mcp_windbg` 工具已加载（会话内有 `open_windbg_dump` 等） | **MCP 模式**（推荐） | 工具调用，会话内可保持 dump 打开，多命令交互；支持活进程 remote |
| MCP 未注册 / 未重启 | **CDB CLI 兜底** | `cdb -z dump -c "cmds; q"` 或 `cdb -p <pid>`，当次可用 |

两条路用的 CDB 命令完全一样，只是调用方式不同。详见 [`windbg-tooling.md`](windbg-tooling.md)。

## 符号路径配置

`_NT_SYMBOL_PATH` 环境变量决定符号解析。推荐：

```
srv*C:\Symbols*https://msdl.microsoft.com/download/symbols;<project_pdb_dir>
```

- `srv*C:\Symbols*https://...` — 微软符号服务器，缓存到 `C:\Symbols`
- `<project_pdb_dir>` — 目标项目 PDB 目录（构建产物）

### 项目 PDB 位置（通用规则）

- 自构建项目：构建产物目录（如 `build/`、`build/install/`、`out/build/`），PDB 与 exe 同目录
- 包管理器依赖：包缓存目录（如 Conan `~/.conan2/`、vcpkg `buildtrees/`），或本地 editable 目录
- 归档符号：CI / 发布归档的 PDB 目录

设置示例（PowerShell，当前会话）：

```powershell
$env:_NT_SYMBOL_PATH = "srv*C:\Symbols*https://msdl.microsoft.com/download/symbols;C:\path\to\your-app\build\bin"
```

或注册到 MCP env（见上文 JSON），随 mcp-windbg 启动注入。

## 限制说明

- **MCP 工具当次会话不可用**：注册 mcp-windbg 后必须重启会话。首次配置时，本 skill 只能用 CDB CLI 兜底验证流程。
- **CDB CLI 无状态**：每次 `cdb -c "cmds; q"` 是独立进程，不能像 MCP 那样保持会话。复杂多步分析建议用 MCP，或 `cdb -z dump` / `cdb -p <pid>` 进交互模式。
- **活进程附加需同权限**：`cdb -p <pid>` 或 `open_windbg_remote` 附加活进程时，CDB 进程要与目标进程同权限（管理员附加管理员进程等）。
