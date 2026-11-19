# Managed Result Contract

本文件只定义 `managed-agent-v1` 的子 Agent 和最终机器结果协议，不包含排障方法。证据、推断、复审和降级语义统一来自 `troubleshooting-core.md`。

## AGENT_RESULT

每个 collect、inference、review Agent 的最终返回必须包含且只包含一个标记块。可在标记前给出一句短摘要，标记后不得继续追加证据正文。

`facts` 仅包含相对任务输入新增的来源化原子事实；`gaps` 仅包含仍缺少且会影响任务完成的信息。不得重复问题背景、输入中的既有事实、其他 Agent 原文或完整工具结果。没有新增事实时返回空数组，不复制 known facts 充数。

```text
<!-- AGENT_RESULT_START -->
{
  "schemaVersion": "managed-agent-result/v1",
  "taskId": "collect-db-1",
  "role": "collect",
  "status": "completed",
  "facts": [
    {
      "id": "F1",
      "statement": "实际观测事实",
      "source": {
        "type": "obs-cli-db",
        "anchor": "数据库/表/条件的脱敏锚点",
        "observedAt": "ISO-8601 时间"
      }
    }
  ],
  "directTrigger": "直接触发或空字符串",
  "rootCauseCandidate": "候选根因或空字符串",
  "confidence": "high",
  "gaps": [],
  "nextSuggestion": "下一步建议或空字符串"
}
<!-- AGENT_RESULT_END -->
```

固定枚举：

- `role`: `collect | inference | review`
- `status`: `completed | partial | blocked | invalid`
- `confidence`: `high | medium | low`
- review 额外返回 `reviewStatus: passed | needs_evidence | rejected` 与 `findings[]`

格式非法时主控只允许要求同一 Agent 做一次纯格式修正，不能借修正扩大调查。结果中禁止 token、认证头、obs-cli 配置正文、完整原始日志、无界数据库返回和不必要源码正文。

## MANAGED_RESULT_META

主控最终输出先按 `troubleshooting-core.md` 的公共结果语义写自然语言正文。摘要、排查思路、已确认事实、分析判断、直接触发、根因、限制、复审结果与建议动作全部写在控制块之外；正文将由平台原文保存和展示，不得为了平台解析而压缩成 JSON，也不要求 `BUSINESS_SUMMARY` 标记。

自然语言正文之后必须追加且只追加一个最小控制块，块后不得再输出内容：

```text
<!-- MANAGED_RESULT_META_START -->
{
  "schemaVersion": "managed-result/v2",
  "status": "succeeded"
}
<!-- MANAGED_RESULT_META_END -->
```

最终控制块只表示主控正常完成并返回了可读结果，不表示正文一定得出了 `concluded` 根因。不得在控制块中增加归因、复审、证据、摘要、根因、置信度或限制字段；这些内容属于人类可读原文。

即使最终只能给出 `platform_limit`、`skill_gap` 或 `input_insufficient` 受限结论，只要主控正常完成正文，也使用相同的 `status: "succeeded"` 控制块。进程异常由宿主判定为失败；控制块缺失、重复、未闭合、JSON 非法、schema/status 非法时，宿主保留正文并进入待确认，不得根据正文关键词推断执行成功。
