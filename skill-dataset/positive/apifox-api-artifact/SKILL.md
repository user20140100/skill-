---
name: apifox-api-artifact
description: >-
  从 Apifox 协作链接、接口路径、Apifox MCP 或 OpenAPI 导出中读取接口信息，并输出来源无关的 API Interface
  Artifact。只要用户需要“从 Apifox 获取接口结构”“把 Apifox 接口转成统一 artifact”“读取 Apifox 后给 TS 或
  Mockoon 使用”，就使用本 skill。本 skill 不生成 TypeScript、Mockoon 或业务代码。
author: wangxiaoli15274
version: 0.0.1
---

# Apifox API Artifact

## 输出

输出 `API Interface Artifact` JSON 文件，默认落到：

`mockoon/artifacts/api-interface/<method>-<path>.json`

核心结构：

```json
{
    "schema_version": "api-interface-artifact/v1",
    "source": {
        "type": "apifox",
        "url": "",
        "fetched_at": ""
    },
    "interface": {
        "name": "",
        "method": "GET",
        "path": "",
        "description": "",
        "tags": [],
        "service_name": ""
    },
    "request": {
        "schema": null,
        "parameters": {}
    },
    "response": {
        "status_code": 200,
        "schema": null,
        "example": null
    },
    "errors": {
        "biz_errors": []
    },
    "extensions": {
        "raw": {}
    }
}
```

## 执行规则

- Apifox 协作链接优先运行 `scripts/resolve-apifox-api.mjs`。
- 解析失败后再走 MCP / 替代输入流程。
- 不要把访问令牌写入仓库、artifact、TS 文件或 Mockoon 文件。
- 不要编造接口结构；缺字段时标记为 `unknown` 或留空，并在总结里说明。

## 可复用资源

- Apifox 协作链接 resolver：`scripts/resolve-apifox-api.mjs`
- Open API resolver 细节：`references/apifox-openapi-resolver.md`
- MCP 回退流程：`references/apifox-mcp.md`
