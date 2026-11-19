#!/usr/bin/env python3
"""
Convert a `lark-cli docs +fetch` JSON payload into Markdown.

The script expects any downloaded media to already exist under:
  <output-dir>/assets/<sanitized-title>/

With stems:
  image-01.*
  whiteboard-01.*
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlsplit

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency at runtime
    Image = None


INVALID_FILENAME_CHARS = '<>:"/\\|?*'
WHITEBOARD_WHITE_THRESHOLD = 245
WHITEBOARD_CROP_PADDING = 24


@dataclass
class ExportResult:
    title: str
    markdown_path: Path
    assets_dir: Path
    fetch_path: Path
    manifest_path: Path
    image_count: int
    whiteboard_count: int
    media: list[dict[str, str]]
    source_url: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Feishu docs +fetch JSON into local Markdown."
    )
    parser.add_argument("--input", required=True, help="Path to docs +fetch JSON output.")
    parser.add_argument("--output-dir", required=True, help="Directory for Markdown output.")
    parser.add_argument(
        "--title",
        help="Override document title for output file and assets directory naming.",
    )
    parser.add_argument(
        "--source-url",
        help="Optional Feishu source URL to include near the top of the Markdown output.",
    )
    return parser.parse_args()


def sanitize_name(value: str) -> str:
    cleaned = "".join("_" if ch in INVALID_FILENAME_CHARS else ch for ch in value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".")
    return cleaned or "untitled"


def ensure_temp_fetch_path(input_path: Path, temp_dir: Path, title: str) -> Path:
    target_path = temp_dir / f"{title}.doc-fetch.json"
    if input_path.resolve() == target_path.resolve():
        return target_path
    target_path.write_text(input_path.read_text(encoding="utf-8"), encoding="utf-8")
    input_path.unlink()
    return target_path


def load_fetch_payload(path: Path) -> tuple[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not payload.get("ok"):
        raise ValueError("input JSON does not contain a successful docs +fetch response")
    data = payload.get("data") or {}
    title = data.get("title")
    markdown = data.get("markdown")
    if not title or markdown is None:
        raise ValueError("input JSON is missing data.title or data.markdown")
    return str(title), str(markdown)


def normalize_cell_text(text: str) -> str:
    text = unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"</?(?:grid|column)\b[^>]*>", " ", text)
    text = re.sub(r'\s*\{align="[^"]+"\}', "", text)

    lines: list[str] = []
    for raw_line in text.split("\n"):
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        line = re.sub(r"^-\s*(\[\s*(?:[xX]|)\s*\])", r"\1", line)
        line = re.sub(r"\[\s*[xX]\s*\]", "[√]", line)
        lines.append(line.replace("|", r"\|"))

    return "<br>".join(lines)


def element_text(element: ET.Element) -> str:
    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in element:
        parts.append(element_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def sanitize_table_xml(raw_table: str) -> str:
    parts = re.split(r"(<\/?lark-(?:table|tr|td)\b[^>]*>)", raw_table)
    sanitized: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("<") and part.endswith(">"):
            sanitized.append(part)
            continue
        sanitized.append(escape(part, quote=False))
    return "".join(sanitized)


def table_to_markdown(raw_table: str) -> str:
    wrapped = f"<root>{sanitize_table_xml(raw_table)}</root>"
    root = ET.fromstring(wrapped)
    table = root.find("lark-table")
    if table is None:
        return raw_table

    rows: list[list[str]] = []
    for tr in table.findall("lark-tr"):
        row: list[str] = []
        for td in tr.findall("lark-td"):
            row.append(normalize_cell_text(element_text(td)))
        rows.append(row)

    if not rows:
        return ""

    col_count = max(len(row) for row in rows)
    padded_rows = [row + [""] * (col_count - len(row)) for row in rows]
    header = padded_rows[0]
    separator = ["---"] * col_count

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in padded_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def resolve_base_url(source_url: str | None) -> str | None:
    if not source_url:
        return None
    parsed = urlsplit(source_url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def convert_mentions(markdown: str, source_url: str | None) -> str:
    pattern = re.compile(
        r'<mention-doc\s+token="([^"]+)"\s+type="([^"]+)"\s*>(.*?)</mention-doc>',
        re.S,
    )
    base_url = resolve_base_url(source_url)

    path_map = {
        "wiki": "wiki",
        "docx": "docx",
        "doc": "doc",
        "sheet": "sheets",
        "slides": "slides",
        "mindnote": "mindnote",
        "bitable": "base",
    }

    def repl(match: re.Match[str]) -> str:
        token, doc_type, label = match.groups()
        target = path_map.get(doc_type)
        text = label.strip()
        if not target or not base_url:
            return text
        return f"[{text}]({base_url}/{target}/{token})"

    return pattern.sub(repl, markdown)


def convert_embedded_sheets(markdown: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return "> 不支持的内嵌电子表格"

    return re.sub(r'<sheet\s+token="([^"]+)"\s*/>', repl, markdown)


def strip_wrappers(markdown: str) -> str:
    markdown = re.sub(
        r"<text\b[^>]*>(.*?)</text>",
        lambda match: match.group(1),
        markdown,
        flags=re.S,
    )
    markdown = re.sub(r"</?(?:view)\b[^>]*>", "", markdown)
    return markdown


def resolve_asset_reference(
    assets_dir: Path, stem: str, fallback_name: str, output_dir: Path
) -> str:
    matches = sorted(assets_dir.glob(f"{stem}.*"))
    if matches:
        chosen = matches[0]
    else:
        chosen = assets_dir / fallback_name
    return chosen.relative_to(output_dir).as_posix()


def crop_whiteboard_asset(
    path: Path,
    padding: int = WHITEBOARD_CROP_PADDING,
    white_threshold: int = WHITEBOARD_WHITE_THRESHOLD,
) -> bool:
    if Image is None or not path.exists():
        return False

    with Image.open(path) as image:
        source = image.convert("RGB")
        grayscale = source.convert("L")
        mask = grayscale.point(
            lambda value: 255 if value < white_threshold else 0, mode="1"
        )
        bbox = mask.getbbox()
        if bbox is None:
            return False

        left, top, right, bottom = bbox
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(source.width, right + padding)
        bottom = min(source.height, bottom + padding)

        if (left, top, right, bottom) == (0, 0, source.width, source.height):
            return False

        cropped = source.crop((left, top, right, bottom))
        save_kwargs: dict[str, object] = {}
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            save_kwargs.update({"quality": 95, "subsampling": 0})
        cropped.save(path, **save_kwargs)
        return True


def crop_whiteboard_assets(assets_dir: Path, media: list[dict[str, str]]) -> int:
    cropped_count = 0
    for item in media:
        if item.get("type") != "whiteboard":
            continue
        stem = item.get("stem")
        if not stem:
            continue
        for asset_path in sorted(assets_dir.glob(f"{stem}.*")):
            if crop_whiteboard_asset(asset_path):
                cropped_count += 1
                break
    return cropped_count


def rewrite_media(
    markdown: str, output_dir: Path, assets_dir: Path
) -> tuple[str, int, int, list[dict[str, str]]]:
    image_index = {"value": 0}
    whiteboard_index = {"value": 0}
    media: list[dict[str, str]] = []

    def image_repl(match: re.Match[str]) -> str:
        image_index["value"] += 1
        idx = image_index["value"]
        token_match = re.search(r'token="([^"]+)"', match.group(0))
        token = token_match.group(1) if token_match else ""
        stem = f"image-{idx:02d}"
        rel_path = resolve_asset_reference(
            assets_dir=assets_dir,
            stem=stem,
            fallback_name=f"{stem}.png",
            output_dir=output_dir,
        )
        media.append(
            {
                "type": "image",
                "token": token,
                "stem": stem,
                "relative_path": rel_path,
            }
        )
        return f"![Image {idx}]({rel_path})"

    def whiteboard_repl(match: re.Match[str]) -> str:
        whiteboard_index["value"] += 1
        idx = whiteboard_index["value"]
        token_match = re.search(r'token="([^"]+)"', match.group(0))
        token = token_match.group(1) if token_match else ""
        stem = f"whiteboard-{idx:02d}"
        rel_path = resolve_asset_reference(
            assets_dir=assets_dir,
            stem=stem,
            fallback_name=f"{stem}.jpg",
            output_dir=output_dir,
        )
        media.append(
            {
                "type": "whiteboard",
                "token": token,
                "stem": stem,
                "relative_path": rel_path,
            }
        )
        return f"![Whiteboard {idx}]({rel_path})"

    markdown = re.sub(r'<image\b[^>]*/>', image_repl, markdown)
    markdown = re.sub(r'<whiteboard\b[^>]*/>', whiteboard_repl, markdown)
    return markdown, image_index["value"], whiteboard_index["value"], media


def convert_markdown(
    markdown: str, output_dir: Path, assets_dir: Path, source_url: str | None
) -> tuple[str, int, int, list[dict[str, str]]]:
    markdown = convert_mentions(markdown, source_url=source_url)
    markdown = convert_embedded_sheets(markdown)
    markdown = re.sub(
        r"<lark-table\b[^>]*>.*?</lark-table>",
        lambda match: table_to_markdown(match.group(0)),
        markdown,
        flags=re.S,
    )
    markdown = strip_wrappers(markdown)
    markdown, image_count, whiteboard_count, media = rewrite_media(
        markdown, output_dir, assets_dir
    )
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"
    return markdown, image_count, whiteboard_count, media


def export_document(
    input_path: Path, output_dir: Path, title_override: str | None, source_url: str | None
) -> ExportResult:
    raw_title, raw_markdown = load_fetch_payload(input_path)
    title = sanitize_name(title_override or raw_title)

    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets" / title
    assets_dir.mkdir(parents=True, exist_ok=True)
    fetch_path = ensure_temp_fetch_path(input_path=input_path, temp_dir=temp_dir, title=title)

    body, image_count, whiteboard_count, media = convert_markdown(
        raw_markdown, output_dir, assets_dir, source_url=source_url
    )
    crop_whiteboard_assets(assets_dir, media)
    markdown_path = output_dir / f"{title}.md"

    header_lines = [f"# {title}", ""]
    if source_url:
        header_lines.extend([f"> Source: {source_url}", ""])
    final_markdown = "\n".join(header_lines) + body
    markdown_path.write_text(final_markdown, encoding="utf-8")

    manifest = {
        "title": title,
        "markdown_path": str(markdown_path),
        "assets_dir": str(assets_dir),
        "fetch_path": str(fetch_path),
        "image_count": image_count,
        "whiteboard_count": whiteboard_count,
        "media": media,
        "source_url": source_url,
    }
    manifest_path = temp_dir / f"{title}.export.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return ExportResult(
        title=title,
        markdown_path=markdown_path,
        assets_dir=assets_dir,
        fetch_path=fetch_path,
        manifest_path=manifest_path,
        image_count=image_count,
        whiteboard_count=whiteboard_count,
        media=media,
        source_url=source_url,
    )


def main() -> None:
    args = parse_args()
    result = export_document(
        input_path=Path(args.input),
        output_dir=Path(args.output_dir),
        title_override=args.title,
        source_url=args.source_url,
    )
    print(
        json.dumps(
            {
                "title": result.title,
                "markdown_path": str(result.markdown_path),
                "assets_dir": str(result.assets_dir),
                "fetch_path": str(result.fetch_path),
                "manifest_path": str(result.manifest_path),
                "image_count": result.image_count,
                "whiteboard_count": result.whiteboard_count,
                "media": result.media,
                "source_url": result.source_url,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
