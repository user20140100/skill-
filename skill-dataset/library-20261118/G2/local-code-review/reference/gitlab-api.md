# GitLab API Reference

需设置环境变量 `GITLAB_TOKEN`（Personal Access Token，需要 `read_api` 权限）。

## 解析 MR URL

```
URL: https://gitlab.gz.cvte.cn/ais/cbb/walle/-/merge_requests/18
→ hostname:      gitlab.gz.cvte.cn
→ project_path:  ais/cbb/walle  →  URL 编码为 ais%2Fcbb%2Fwalle
→ mr_iid:        18
```

## 获取 MR 基本信息（含 project_id）

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://{hostname}/api/v4/projects/{project_path_encoded}/merge_requests/{mr_iid}"
```

返回 JSON 中取 `project_id`，后续用 `project_id` 调用 API（避免路径编码问题）。
也可取 `source_branch`、`target_branch`、`author.name`、`title`、`state`。

## 获取文件列表

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://{hostname}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/diffs" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Total: {len(data)}')
for d in data:
    flag = ' [NEW]' if d.get('new_file') else (' [DEL]' if d.get('deleted_file') else '')
    print(d['new_path'] + flag)
"
```

## 获取完整 diff 内容

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://{hostname}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/diffs" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for d in data:
    print(f'=== FILE: {d[\"new_path\"]} ===')
    print(d['diff'])
    print()
"
```

- `deleted_file: true` 的文件可跳过
- `new_file: true` 的文件是全新文件，重点审查
- 超大 MR（>100 文件）需分页：`?page=1&per_page=20`

## 机械规则扫描（仅扫 `+` 行）

```bash
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://{hostname}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/diffs" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data:
    for line in item['diff'].split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            print(f'{item[\"new_path\"]}: {line[1:]}')
" | grep -n "YOUR_PATTERN_HERE"
```

## Diff 行号解析与锚点构造

GitLab MR diff 锚点格式：

```
#{md5(new_path)}_{old_line}_{new_line}
```

- `md5(new_path)`：对文件路径取 MD5 hex digest
- 新增行（`+`）：`old_line=0`
- 删除行（`-`）：`new_line=0`
- 上下文行：两者均有值

### 从 diff hunk 解析行号

```python
import hashlib, re

def md5(path: str) -> str:
    return hashlib.md5(path.encode()).hexdigest()

def parse_diff_linenos(diff_text: str) -> list[tuple[str, int, int]]:
    """返回 (line_content, old_lineno, new_lineno) 列表。"""
    result = []
    old_n = new_n = 0
    for line in diff_text.splitlines():
        m = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
        if m:
            old_n, new_n = int(m.group(1)), int(m.group(2))
            continue
        if line.startswith('---') or line.startswith('+++'):
            continue
        if line.startswith('+'):
            result.append((line[1:], 0, new_n))
            new_n += 1
        elif line.startswith('-'):
            result.append((line[1:], old_n, 0))
            old_n += 1
        else:
            result.append((line[1:] if line.startswith(' ') else line, old_n, new_n))
            old_n += 1
            new_n += 1
    return result

def diff_anchor(host: str, project: str, iid: int,
                new_path: str, old_line: int, new_line: int) -> str:
    anchor = f"{md5(new_path)}_{old_line}_{new_line}"
    return f"{host}/{project}/-/merge_requests/{iid}/diffs#{anchor}"
```

### 使用示例

```python
url = diff_anchor(
    host="https://gitlab.gz.cvte.cn",
    project="ais/cbb/walle",
    iid=18,
    new_path="src/main.py",
    old_line=0,    # 新增行
    new_line=42,
)
# → https://gitlab.gz.cvte.cn/ais/cbb/walle/-/merge_requests/18/diffs#<md5>_0_42
```
