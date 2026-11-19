#!/usr/bin/env python3
"""
Android VectorDrawable XML to SVG converter.
Converts Android VectorDrawable XML files back to standard SVG format with proper support for:
- path data passthrough
- android:fillType="evenOdd" -> fill-rule="evenodd"
- group elements with transforms
- Fill colors, stroke, alpha
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom
from pathlib import Path

ANDROID_NS = "http://schemas.android.com/apk/res/android"
SVG_NS = "http://www.w3.org/2000/svg"


def android_color_to_svg(color_str):
    """Convert Android color (#AARRGGBB or #RRGGBB) to SVG rgba/hex."""
    if not color_str:
        return None, None
    color_str = color_str.strip()
    if color_str.startswith("#"):
        hex_part = color_str[1:]
        if len(hex_part) == 8:
            # #AARRGGBB
            a = int(hex_part[0:2], 16)
            r = int(hex_part[2:4], 16)
            g = int(hex_part[4:6], 16)
            b = int(hex_part[6:8], 16)
            alpha = round(a / 255, 4)
            return f"#{hex_part[2:8].upper()}", alpha if alpha < 1.0 else None
        elif len(hex_part) == 6:
            return f"#{hex_part.upper()}", None
        elif len(hex_part) == 3:
            return f"#{hex_part[0] * 2}{hex_part[1] * 2}{hex_part[2] * 2}".upper(), None
    return color_str, None


def a(name):
    """Helper to build android namespace attribute key."""
    return f"{{{ANDROID_NS}}}{name}"


def process_vector_path(elem):
    """Convert a VectorDrawable <path> element to an SVG <path> element."""
    svg_path = ET.Element("path")

    path_data = elem.get(a("pathData"), "")
    if path_data:
        svg_path.set("d", path_data)

    fill_color = elem.get(a("fillColor"))
    if fill_color:
        color, alpha_from_color = android_color_to_svg(fill_color)
        if color and color.upper() not in ("#00000000",):
            svg_path.set("fill", color)
            if alpha_from_color is not None:
                svg_path.set("fill-opacity", str(alpha_from_color))
        else:
            svg_path.set("fill", "none")
    else:
        svg_path.set("fill", "none")

    fill_alpha = elem.get(a("fillAlpha"))
    if fill_alpha:
        svg_path.set("fill-opacity", fill_alpha)

    fill_type = elem.get(a("fillType"))
    if fill_type and fill_type.lower() in ("evenodd", "evenOdd"):
        svg_path.set("fill-rule", "evenodd")

    stroke_color = elem.get(a("strokeColor"))
    if stroke_color:
        stroke, _ = android_color_to_svg(stroke_color)
        if stroke:
            svg_path.set("stroke", stroke)

    stroke_width = elem.get(a("strokeWidth"))
    if stroke_width:
        svg_path.set("stroke-width", stroke_width)

    stroke_alpha = elem.get(a("strokeAlpha"))
    if stroke_alpha:
        svg_path.set("stroke-opacity", stroke_alpha)

    stroke_linecap = elem.get(a("strokeLineCap"))
    if stroke_linecap:
        svg_path.set("stroke-linecap", stroke_linecap.lower())

    stroke_linejoin = elem.get(a("strokeLineJoin"))
    if stroke_linejoin:
        svg_path.set("stroke-linejoin", stroke_linejoin.lower())

    return svg_path


def process_vector_group(elem):
    """Convert a VectorDrawable <group> element to an SVG <g> element."""
    svg_g = ET.Element("g")

    transforms = []
    translate_x = elem.get(a("translateX"))
    translate_y = elem.get(a("translateY"))
    if translate_x or translate_y:
        tx = translate_x or "0"
        ty = translate_y or "0"
        transforms.append(f"translate({tx},{ty})")

    scale_x = elem.get(a("scaleX"))
    scale_y = elem.get(a("scaleY"))
    if scale_x or scale_y:
        sx = scale_x or "1"
        sy = scale_y or "1"
        transforms.append(f"scale({sx},{sy})")

    rotation = elem.get(a("rotation"))
    if rotation:
        pivot_x = elem.get(a("pivotX"), "0")
        pivot_y = elem.get(a("pivotY"), "0")
        transforms.append(f"rotate({rotation},{pivot_x},{pivot_y})")

    if transforms:
        svg_g.set("transform", " ".join(transforms))

    for child in elem:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "path":
            svg_g.append(process_vector_path(child))
        elif tag == "group":
            svg_g.append(process_vector_group(child))
        elif tag == "clip-path":
            # clip-path in VectorDrawable: wrap in a <clipPath>
            clip_id = f"clip_{id(child)}"
            clip_elem = ET.Element("clipPath")
            clip_elem.set("id", clip_id)
            clip_path_data = child.get(a("pathData"), "")
            if clip_path_data:
                clip_path_elem = ET.Element("path")
                clip_path_elem.set("d", clip_path_data)
                clip_elem.append(clip_path_elem)
            svg_g.append(clip_elem)

    return svg_g


def convert_vector_to_svg(xml_path, output_path):
    """Convert a single Android VectorDrawable XML file to SVG."""
    ET.register_namespace("android", ANDROID_NS)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Support both bare <vector> and namespace-qualified
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag != "vector":
        raise ValueError(f"Root element is <{tag}>, expected <vector>")

    # Extract dimensions
    width_str = root.get(a("width"), "24dp")
    height_str = root.get(a("height"), "24dp")
    viewport_width = root.get(a("viewportWidth"), "24")
    viewport_height = root.get(a("viewportHeight"), "24")

    # Strip dp/px/sp units
    width = re.sub(r"[^\d.]", "", width_str) or "24"
    height = re.sub(r"[^\d.]", "", height_str) or "24"

    svg = ET.Element("svg")
    svg.set("xmlns", SVG_NS)
    svg.set("width", width)
    svg.set("height", height)
    svg.set("viewBox", f"0 0 {viewport_width} {viewport_height}")

    defs = ET.Element("defs")
    has_defs = False

    for child in root:
        child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if child_tag == "path":
            svg.append(process_vector_path(child))
        elif child_tag == "group":
            svg.append(process_vector_group(child))
        elif child_tag == "clip-path":
            clip_id = f"clip_{id(child)}"
            clip_elem = ET.Element("clipPath")
            clip_elem.set("id", clip_id)
            clip_path_data = child.get(a("pathData"), "")
            if clip_path_data:
                cp = ET.Element("path")
                cp.set("d", clip_path_data)
                clip_elem.append(cp)
            defs.append(clip_elem)
            has_defs = True

    if has_defs:
        svg.insert(0, defs)

    xml_str = ET.tostring(svg, encoding="unicode")
    dom = xml.dom.minidom.parseString(xml_str)
    pretty = dom.toprettyxml(indent="    ")

    lines = [line for line in pretty.split("\n") if line.strip()]
    if lines and lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="utf-8"?>'
    pretty = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty)

    return True


def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python vector_to_svg.py <input_directory> [--delete]")
        print("  --delete: Delete original XML files after successful conversion")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    delete_after = "--delete" in sys.argv

    if not input_dir.exists():
        print(f"Error: Directory '{input_dir}' does not exist")
        sys.exit(1)

    xml_files = list(input_dir.glob("*.xml"))

    if not xml_files:
        print(f"No XML files found in '{input_dir}'")
        sys.exit(0)

    print(f"Found {len(xml_files)} XML files")

    converted = 0
    skipped = 0
    failed = []

    for xml_file in xml_files:
        svg_name = xml_file.stem + ".svg"
        output_path = input_dir / svg_name

        try:
            convert_vector_to_svg(xml_file, output_path)
            print(f"✓ {xml_file.name} -> {svg_name}")
            converted += 1

            if delete_after:
                xml_file.unlink()
                print(f"  Deleted: {xml_file.name}")

        except ValueError as e:
            print(f"⚠ {xml_file.name}: skipped ({e})")
            skipped += 1
        except Exception as e:
            print(f"✗ {xml_file.name}: {e}")
            failed.append(xml_file.name)

    total = len(xml_files)
    print(f"\nConverted: {converted}/{total - skipped}")
    if skipped:
        print(f"Skipped (not VectorDrawable): {skipped}")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
