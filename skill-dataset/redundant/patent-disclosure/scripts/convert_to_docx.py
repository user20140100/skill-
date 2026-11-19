#!/usr/bin/env python3
"""
专利交底书 Markdown → DOCX 转换工具

将 Markdown 中的 Mermaid 代码块渲染为图片，然后通过 pandoc 转为 docx。

依赖：
  - Python 3.8+，Pillow 库 (pip install Pillow)
  - pandoc CLI (brew install pandoc / apt install pandoc)

用法：
  python3 convert_to_docx.py <input.md>
  python3 convert_to_docx.py <input.md> --output output.docx
"""

import argparse
import base64
import json
import ipaddress
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import zlib
from PIL import Image, ImageDraw, ImageFont


DEFAULT_MERMAID_INK_BASE = "https://mermaid.ink/img/"
MAX_IMAGE_BYTES = 10 * 1024 * 1024

FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]


def is_local_hostname(hostname: str) -> bool:
    if hostname in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_loopback or ip.is_private or ip.is_link_local
    except ValueError:
        return hostname.endswith(".local")


def validate_mermaid_base_url(base_url: str, allow_external: bool) -> str:
    if not base_url.endswith("/"):
        base_url += "/"
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print("! Mermaid 渲染服务地址必须是 http(s) URL")
        sys.exit(1)
    hostname = parsed.hostname or ""
    if not is_local_hostname(hostname) and not allow_external:
        print("! 检测到外部 Mermaid 渲染服务。专利交底书可能包含未公开技术细节。")
        print("  若确认允许外发图表内容，请添加 --allow-external-rendering；更推荐使用 --mermaid-base-url 指向本地或自托管服务。")
        sys.exit(1)
    return base_url


def is_valid_image(data: bytes) -> bool:
    return data.startswith(b"\x89PNG\r\n\x1a\n") or data.startswith(b"\xff\xd8\xff")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def encode_mermaid_pako(code: str, base_url: str) -> str:
    state = {"code": code, "mermaid": {"theme": "default"}}
    compressed = zlib.compress(json.dumps(state).encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"{base_url}pako:{encoded}"


def encode_mermaid_b64(code: str, base_url: str) -> str:
    encoded = base64.urlsafe_b64encode(code.encode("utf-8")).decode("ascii").rstrip("=")
    return f"{base_url}base64:{encoded}"


def download_image(url: str, filepath: str, timeout: int = 60) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "patent-disclosure-converter/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                print(f"  ! unexpected content type: {content_type or 'unknown'}")
                return False
            data = resp.read(MAX_IMAGE_BYTES + 1)
            if len(data) > MAX_IMAGE_BYTES:
                print("  ! image response too large")
                return False
            if not is_valid_image(data):
                print("  ! response body is not a supported image")
                return False
            with open(filepath, "wb") as f:
                f.write(data)
        return True
    except Exception as e:
        print(f"  ! download failed: {type(e).__name__}")
        return False


def render_mermaid(code: str, filepath: str, base_url: str) -> bool:
    for url in (encode_mermaid_pako(code, base_url), encode_mermaid_b64(code, base_url)):
        if download_image(url, filepath):
            return True
    return False


def render_ascii_art(text: str, filepath: str, font_size: int = 14) -> bool:
    try:
        font = load_font(font_size)
        lines = text.split("\n")

        def cw(ch: str) -> int:
            cp = ord(ch)
            if (0x4E00 <= cp <= 0x9FFF or 0x3000 <= cp <= 0x303F or
                    0xFF00 <= cp <= 0xFFEF or 0x2500 <= cp <= 0x257F):
                return int(font_size * 1.9)
            return font_size

        lh = int(font_size * 1.4)
        pad = 20
        mll = max((sum(cw(ch) for ch in line) for line in lines), default=0)
        img = Image.new("RGB", (mll + pad * 2, len(lines) * lh + pad * 2), "white")
        draw = ImageDraw.Draw(img)
        y = pad
        for line in lines:
            x = pad
            for ch in line:
                draw.text((x, y), ch, fill="black", font=font)
                x += cw(ch)
            y += lh
        img.save(filepath, "PNG", dpi=(150, 150))
        return True
    except Exception as e:
        print(f"  ! ascii render failed: {e}")
        return False


def extract_code_blocks(md: str):
    pat = r"^```(\w*)\n(.*?)^```\s*$"
    return [(m.start(), m.end(), m.group(1) or "", m.group(2)) for m in re.finditer(pat, md, re.DOTALL | re.MULTILINE)]


def pandoc_convert(temp_md: str, output_docx: str) -> bool:
    result = subprocess.run(
        ["pandoc", temp_md, "-o", output_docx, "--from", "markdown", "--to", "docx"],
        capture_output=True, text=True, cwd=os.path.dirname(temp_md),
    )
    if result.returncode != 0:
        print("! pandoc failed")
        if result.stderr:
            print(result.stderr[:1000])
        return False
    if result.stderr:
        print(f"  pandoc warnings:\n{result.stderr}")
    return True


def main():
    parser = argparse.ArgumentParser(description="专利交底书 Markdown → DOCX 转换")
    parser.add_argument("input", help="输入 Markdown 文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出 DOCX 文件路径")
    parser.add_argument("--diagram-dir", default=None, help="图片输出目录")
    parser.add_argument("--font-size", type=int, default=14, help="ASCII 图字号（默认 14）")
    parser.add_argument(
        "--mermaid-base-url",
        default=os.environ.get("MERMAID_INK_BASE", DEFAULT_MERMAID_INK_BASE),
        help="Mermaid 渲染服务地址；可用 MERMAID_INK_BASE 指向自托管服务",
    )
    parser.add_argument(
        "--allow-external-rendering",
        action="store_true",
        help="允许将 Mermaid 图发送到外部渲染服务（默认禁止外发，需显式确认）",
    )
    args = parser.parse_args()

    input_md = os.path.abspath(args.input)
    if not os.path.isfile(input_md):
        print(f"! 文件不存在: {input_md}")
        sys.exit(1)

    input_dir = os.path.dirname(input_md)
    stem = os.path.splitext(os.path.basename(input_md))[0]

    output_docx = args.output or os.path.join(input_dir, f"{stem}.docx")
    diagram_dir = args.diagram_dir or os.path.join(input_dir, "diagrams")
    os.makedirs(diagram_dir, exist_ok=True)

    with open(input_md, "r", encoding="utf-8") as f:
        md_content = f.read()

    blocks = extract_code_blocks(md_content)
    has_mermaid = any(lang == "mermaid" for _, _, lang, _ in blocks)
    mermaid_base_url = args.mermaid_base_url
    if has_mermaid:
        mermaid_base_url = validate_mermaid_base_url(args.mermaid_base_url, args.allow_external_rendering)
        if not is_local_hostname(urllib.parse.urlparse(mermaid_base_url).hostname or ""):
            print(f"! Mermaid 图会发送到外部服务渲染: {urllib.parse.urlparse(mermaid_base_url).netloc}")

    print(f"发现 {len(blocks)} 个代码块")

    replacements = []
    mcnt = 0
    acnt = 0

    for start, end, lang, content in blocks:
        if lang == "mermaid":
            mcnt += 1
            fname = f"mermaid_{mcnt}.png"
            fpath = os.path.join(diagram_dir, fname)
            print(f"[mermaid#{mcnt}] rendering...", end=" ")
            if render_mermaid(content.strip(), fpath, mermaid_base_url):
                print("OK")
                replacements.append((start, end, fname, f"图{mcnt}"))
            else:
                print("FAIL, kept as code block")
        elif not lang:
            # ASCII box-drawing check
            box_chars = {"┌", "└", "├", "┼", "─", "│", "┘", "┬", "┴", "┐",
                         "▼", "▲", "◄", "►", "║", "╔", "╗", "╚", "╝", "═",
                         "╠", "╣", "╩", "╬"}
            if any(c in content for c in box_chars):
                acnt += 1
                fname = f"ascii_{acnt}.png"
                fpath = os.path.join(diagram_dir, fname)
                print(f"[ascii#{acnt}] rendering...", end=" ")
                if render_ascii_art(content.strip(), fpath, args.font_size):
                    print("OK")
                    replacements.append((start, end, fname, f"架构图{acnt}"))
                else:
                    print("FAIL, kept as code block")

    print(f"\n汇总: {mcnt} mermaid + {acnt} ascii")

    # Replace code blocks with image references
    diagram_rel = os.path.relpath(diagram_dir, input_dir)
    modified = md_content
    for start, end, fname, caption in reversed(replacements):
        ref = f"\n![{caption}]({diagram_rel}/{fname})\n*{caption}*\n"
        modified = modified[:start] + ref + modified[end:]

    ok = False
    temp_md = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=f"_{stem}.md", dir=input_dir, delete=False,
    )
    temp_md_path = temp_md.name
    try:
        with temp_md:
            temp_md.write(modified)

        print("\n转换为 docx...")
        ok = pandoc_convert(temp_md_path, output_docx)
    finally:
        if os.path.exists(temp_md_path):
            os.remove(temp_md_path)

    if ok and os.path.exists(output_docx):
        print(f"\nOK: {output_docx} ({os.path.getsize(output_docx) / 1024:.0f}KB)")
        print(f"   图片目录: {diagram_dir}")
    else:
        print("\n! 转换失败")
        sys.exit(1)


if __name__ == "__main__":
    main()