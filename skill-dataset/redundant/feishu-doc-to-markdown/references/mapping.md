# Mapping

## Supported inputs

- Feishu `wiki` URLs that resolve to `docx` or `doc`
- Direct Feishu `docx` / `doc` URLs

## Output contract

For document title `Example Title`, export:

- `Example Title.md`
- `assets/Example Title/`

Use relative Markdown references for every downloaded asset.

## Media naming

The converter expects ordered stems:

- normal images: `image-01`, `image-02`, ...
- whiteboards: `whiteboard-01`, `whiteboard-02`, ...

`lark-cli docs +media-download` adds the final extension based on the content type, so download using the stem only:

```powershell
lark-cli docs +media-download --token "<token>" --output "./assets/<标题名>/image-01" --as user
lark-cli docs +media-download --type whiteboard --token "<token>" --output "./assets/<标题名>/whiteboard-01" --as user
```

## Tag conversion

| Feishu tag | Markdown result |
| --- | --- |
| `mention-doc` | Feishu hyperlink |
| `sheet` | `> 不支持的内嵌电子表格` |
| `lark-table` | Markdown table |
| `image` | `![Image N](relative/path)` |
| `whiteboard` | `![Whiteboard N](relative/path)` |
| `text` | inner text only |
| `view` | removed wrapper |

## Verification checklist

- `标题名.md` exists
- `assets/标题名/` exists
- no unsupported Feishu tags remain in the Markdown
- every Markdown image reference points to a local file
- `标题名.export.json` lists the same ordered media tokens that were downloaded
