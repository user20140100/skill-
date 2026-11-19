---
name: zipkin-trace-lookup
description: >-
  通过 traceId 查询 Zipkin 链路追踪信息，提取错误调用链和关键诊断数据。
  当用户提到 traceId、链路追踪、trace、zipkin、请求链路、调用链、错误排查时使用此 skill。
version: 1.0.0
author: dats
---

# Zipkin Trace 链路查询

## 工作流程

当用户提供 traceId 时，执行以下步骤：

### Step 1: 确定环境

Zipkin 地址按以下优先级获取：
1. 命令行参数 `--zipkin-url`
2. 环境变量（按环境选取，**必须配置**）

| 环境 | 环境变量 |
|------|----------|
| 生产 (pro) | `ZIPKIN_PRO_URL` |
| 测试 (sit/uat/dev) | `ZIPKIN_TEST_URL` |

如果用户没有明确指定环境，**默认使用生产环境**。如果用户提供了页面 URL，根据 URL 中是否包含 `dev`、`test`、`sit`、`uat` 关键字判断。

**环境变量未配置时脚本会报错退出**，需要在 `~/.zshrc` 或 `~/.bashrc` 中配置：

```bash
export ZIPKIN_PRO_URL="<生产环境 Zipkin 地址>"
export ZIPKIN_TEST_URL="<测试环境 Zipkin 地址>"
```

### Step 2: 执行脚本获取链路数据

```bash
python3 scripts/extract_trace.py <traceId> --format json
```

**可选参数**：
- `--zipkin-url <url>`：直接指定 Zipkin 地址
- `--page-url <url>`：通过页面 URL 自动判断环境
- `--format json|text`：输出格式，默认 json

**示例**：

```bash
# 生产环境（默认，读取 ZIPKIN_PRO_URL）
python3 scripts/extract_trace.py 712a9c84d6f62e97

# 通过页面 URL 自动判断环境
python3 scripts/extract_trace.py 712a9c84d6f62e97 --page-url <页面URL>

# 直接指定 Zipkin 地址（跳过环境变量）
python3 scripts/extract_trace.py 712a9c84d6f62e97 --zipkin-url <Zipkin地址>
```

脚本位置：当前 skill 目录下的 `scripts/extract_trace.py`，执行时需要用绝对路径或切换到 skill 目录。

### Step 3: 分析输出结果

脚本返回 JSON 格式的结构化数据，关键字段含义：

| 字段 | 说明 |
|------|------|
| `traceId` | 链路追踪 ID |
| `traceTime` | 请求发生时间 |
| `summary.totalSpans` | 总 Span 数量 |
| `summary.hasErrors` | 是否存在错误 |
| `callTree` | 完整调用树（扁平化列表，含 depth 层级和各节点耗时） |
| `errorChain` | 错误调用链（从叶子节点到根节点，仅有错误时非空） |
| `leafErrorServiceName` | 最底层错误发生的服务名 |
| `leafErrorHttpPath` | 最底层错误的 HTTP 路径 |
| `leafErrorBody` | 最底层错误的请求体 |
| `leafErrorResponse` | 最底层错误的响应体 |
| `leafErrorStackTrace` | 最底层错误的堆栈信息 |
| `rootErrorServiceName` | 最上层入口服务名 |
| `rootErrorHttpPath` | 最上层入口 HTTP 路径 |
| `rootErrorBody` | 最上层入口请求体 |
| `rootErrorResponse` | 最上层入口响应体 |

**callTree 节点字段**：

| 字段 | 说明 |
|------|------|
| `depth` | 调用层级深度（0=根节点） |
| `name` | 操作名称 |
| `serviceName` | 服务名 |
| `durationMs` | 耗时（毫秒） |
| `durationUs` | 耗时（微秒） |
| `httpMethod` | HTTP 方法 |
| `httpPath` | HTTP 路径 |
| `httpStatus` | HTTP 状态码 |
| `hasError` | 是否有错误 |

### Step 4: 向用户呈现分析结果

根据获取到的数据，向用户提供以下信息：

1. **请求概览**：traceId、请求时间、总 Span 数
2. **调用链路耗时**（始终展示）：根据 `callTree` 字段，按层级缩进展示每个节点的服务名、接口路径、耗时。用缩进或树形符号表示层级关系（depth 字段）。标注耗时较长的节点。
3. **错误定位**（仅有错误时）：
   - 错误发生在哪个服务（leafErrorServiceName）
   - 错误对应的接口路径（leafErrorHttpPath）
   - 错误的具体信息（leafErrorStackTrace 或 leafErrorResponse）
4. **错误调用链**（仅有错误时）：从入口服务到错误发生处的完整调用路径
5. **分析建议**：基于耗时分布和错误信息给出初步判断

如果 `summary.hasErrors` 为 false，说明该请求没有错误，仍然展示完整的调用链路耗时信息。

## 注意事项

- 脚本使用 Python 3 标准库，无需安装额外依赖
- 脚本会自动过滤 `statemachinetaskexecutor` 类型的节点（状态机内部执行节点）
- 错误链提取逻辑：优先查找叶子错误节点，然后向上构建完整调用链
- 网络请求超时时间为 30 秒，内部 HTTPS 证书验证已跳过
