# Jira 附件与备注（参考）

## 从工单 KEY 取附件列表

```bash
curl -s -u "USER:TOKEN_OR_PASSWORD" \
  "https://jira.cvte.com/rest/api/2/issue/ODMAFSALE-805?fields=attachment"
```

响应中每个附件含 `id`、`filename`、`content`（下载 URL）、`size`。

## 下载附件内容

对附件对象中的 `content` URL 发起 GET（与上一步相同认证），保存到例如：

`log/ODMAFSALE-805/<原始文件名>.zip`

## 添加评论（备注）

```bash
curl -s -u "USER:TOKEN_OR_PASSWORD" \
  -X POST \
  -H "Content-Type: application/json" \
  "https://jira.cvte.com/rest/api/2/issue/ODMAFSALE-805/comment" \
  -d '{"body":"在此填写 ADF 格式或 wiki 标记文本（取决于 Jira 版本）"}'
```

Jira Server/Data Center 的 `body` 可能是 **wiki markup**；Cloud 多为 **Atlassian Document Format (ADF)**。以当前实例文档为准。

## 解压示例

```bash
mkdir -p log/ODMAFSALE-805/extracted
unzip -o "log/ODMAFSALE-805/your.zip" -d "log/ODMAFSALE-805/extracted"
```

大文件解压前可用 `unzip -l` 预览目录结构。
