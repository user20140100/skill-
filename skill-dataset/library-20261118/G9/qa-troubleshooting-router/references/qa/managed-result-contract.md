# Managed QA Result Contract

本文件仅由 managed Profile 在最终输出前读取。最终输出包含人类可读正文和唯一控制块；控制块不得代替正文。

## QA_RESULT

```text
<!-- QA_RESULT_START -->
{
  "schemaVersion": "qa-skill-result/v1",
  "contractVersion": "knowledge-qa/v1",
  "requestId": "宿主固定 requestId",
  "resultType": "ANSWER|DEGRADED|NEEDS_CONTEXT|REFUSED|FAILED",
  "questionType": "CAPABILITY_INTEGRATION|CAPABILITY_DISCOVERY|SCENARIO_FEASIBILITY|RESPONSIBILITY_ROUTING|OUT_OF_SCOPE|UNKNOWN",
  "answer": "面向用户的答案或澄清说明",
  "citations": [
    {
      "materialId": "本次已注册 materialId",
      "label": "公开来源标签"
    }
  ],
  "routeSummary": "不含内部候选和凭证的范围摘要",
  "refusalReason": "",
  "degradedReason": "",
  "clarificationFields": []
}
<!-- QA_RESULT_END -->
```

## 硬约束

- 必须只有一个 `QA_RESULT_START`/`QA_RESULT_END` 控制块，JSON 必须合法且字段有界。
- `requestId` 必须原样使用宿主值；不得自行生成或替换。
- `ANSWER`、`DEGRADED`、`NEEDS_CONTEXT`、`REFUSED`、`FAILED` 只能选择一个。
- citations 只能引用本次实际注册的 materialId；不得伪造 sourceType、revision、项目或路径。
- `questionType` 必须与本次已验证意图及唯一加载的操作提示词一致；`OUT_OF_SCOPE`、`UNKNOWN` 不得伪装成四类受支持答案。
- `RESPONSIBILITY_ROUTING` 的 `ANSWER`/`DEGRADED` 必须引用本次宿主注册的 `responsibilityMaterialId`；其他项目答案同样必须使用已注册引用。
- 不得包含 capability token、API Key、kbId、credentialId、Authorization、callback secret、Token、工具参数、原始工具结果、绝对路径或 thinking。
- 项目选择、来源和引用由宿主运行证据 canonicalize；控制块中的展示摘要不产生授权。
