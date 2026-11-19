#!/usr/bin/env python3
"""
SVG to Android VectorDrawable XML converter.
Converts SVG files to Android VectorDrawable XML format with proper support for:
- Path data conversion
- fill-rule="evenodd" -> android:fillType="evenOdd"
- Circle and rect elements
- Fill opacity and colors
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ANDROID_NS = "http://schemas.android.com/apk/res/android"


def parse_color(color_str):
    """Parse SVG color to Android color format."""
    if not color_str or color_str == "none":
        return None

    named_colors = {
        "white": "#FFFFFF",
        "black": "#000000",
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "transparent": "#00000000",
    }

    if color_str.lower() in named_colors:
        color_str = named_colors[color_str.lower()]

    rgba_match = re.match(
        r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)",
        color_str,
    )
    if rgba_match:
        r = int(rgba_match.group(1))
        g = int(rgba_match.group(2))
        b = int(rgba_match.group(3))
        a = float(rgba_match.group(4)) if rgba_match.group(4) else 1.0
        return f"#{int(a * 255):02X}{r:02X}{g:02X}{b:02X}"

    if color_str.startswith("#"):
        hex_color = color_str[1:]
        if len(hex_color) == 6:
            return f"#{hex_color}"
        elif len(hex_color) == 3:
            return f"#{hex_color[0] * 2}{hex_color[1] * 2}{hex_color[2] * 2}"
        elif len(hex_color) == 8:
            return f"#{hex_color}"

    return color_str


def circle_to_path(cx, cy, r):
    """Convert circle element to path data."""
    return (
        f"M {cx - r} {cy} A {r} {r} 0 1 1 {cx + r} {cy} A {r} {r} 0 1 1 {cx - r} {cy}"
    )


def rect_to_path(x, y, width, height, rx=0, ry=0):
    """Convert rect element to path data."""
    if rx == 0 and ry == 0:
        return f"M {x} {y} H {x + width} V {y + height} H {x} Z"
    else:
        rx = min(rx, width / 2)
        ry = min(ry, height / 2)
        return (
            f"M {x + rx} {y} H {x + width - rx} "
            f"A {rx} {ry} 0 0 1 {x + width} {y + ry} "
            f"V {y + height - ry} "
            f"A {rx} {ry} 0 0 1 {x + width - rx} {y + height} "
            f"H {x + rx} A {rx} {ry} 0 0 1 {x} {y + height - ry} "
            f"V {y + ry} A {rx} {ry} 0 0 1 {x + rx} {y} Z"
        )


def process_element(elem):
    """Process SVG element and convert to VectorDrawable element."""
    tag = elem.tag.replace(f"{{{SVG_NS}}}", "")
    elements = []

    if tag == "path":
        path_elem = ET.Element("path")
        d = elem.get("d", "")
        path_elem.set("android:pathData", d)

        fill_rule = elem.get("fill-rule", "")
        if fill_rule == "evenodd":
            path_elem.set("android:fillType", "evenOdd")

        fill = elem.get("fill")
        if fill and fill != "none":
            fill_color = parse_color(fill)
            if fill_color:
                path_elem.set("android:fillColor", fill_color)
        else:
            path_elem.set("android:fillColor", "#00000000")

        stroke = elem.get("stroke")
        if stroke and stroke != "none":
            stroke_color = parse_color(stroke)
            path_elem.set("android:strokeColor", stroke_color)
            stroke_width = elem.get("stroke-width", "1")
            path_elem.set("android:strokeWidth", stroke_width)

        fill_opacity = elem.get("fill-opacity")
        if fill_opacity:
            path_elem.set("android:fillAlpha", fill_opacity)

        elements.append(path_elem)

    elif tag == "circle":
        cx = float(elem.get("cx", "0"))
        cy = float(elem.get("cy", "0"))
        r = float(elem.get("r", "0"))

        path_elem = ET.Element("path")
        path_elem.set("android:pathData", circle_to_path(cx, cy, r))

        fill = elem.get("fill")
        if fill and fill != "none":
            fill_color = parse_color(fill)
            if fill_color:
                path_elem.set("android:fillColor", fill_color)

        fill_opacity = elem.get("fill-opacity")
        if fill_opacity:
            path_elem.set("android:fillAlpha", fill_opacity)

        elements.append(path_elem)

    elif tag == "rect":
        x = float(elem.get("x", "0"))
        y = float(elem.get("y", "0"))
        width = float(elem.get("width", "0"))
        height = float(elem.get("height", "0"))
        rx = float(elem.get("rx", "0"))
        ry = float(elem.get("ry", "0"))

        path_elem = ET.Element("path")
        path_elem.set("android:pathData", rect_to_path(x, y, width, height, rx, ry))

        fill = elem.get("fill")
        if fill and fill != "none":
            fill_color = parse_color(fill)
            if fill_color:
                path_elem.set("android:fillColor", fill_color)

        elements.append(path_elem)

    elif tag == "g":
        group_elem = ET.Element("group")

        for child in elem:
            child_elements = process_element(child)
            for ce in child_elements:
                group_elem.append(ce)

        if len(group_elem) > 0:
            elements.append(group_elem)

    elif tag == "defs":
        for child in elem:
            child_elements = process_element(child)
            elements.extend(child_elements)

    return elements


def convert_svg_to_vector(svg_path, output_path):
    """Convert a single SVG file to Android VectorDrawable XML."""
    tree = ET.parse(svg_path)
    root = tree.getroot()

    width = root.get("width", "24")
    height = root.get("height", "24")
    viewbox = root.get("viewBox", f"0 0 {width} {height}")

    vb_parts = viewbox.split()
    vb_width = vb_parts[2] if len(vb_parts) > 2 else width
    vb_height = vb_parts[3] if len(vb_parts) > 3 else height

    vb_width = re.sub(r"[^\d.]", "", str(vb_width))
    vb_height = re.sub(r"[^\d.]", "", str(vb_height))

    vector = ET.Element("vector")
    vector.set("xmlns:android", ANDROID_NS)
    vector.set("android:width", str(int(float(width))) + "dp")
    vector.set("android:height", str(int(float(height))) + "dp")
    vector.set("android:viewportWidth", vb_width)
    vector.set("android:viewportHeight", vb_height)

    for child in root:
        elements = process_element(child)
        for elem in elements:
            vector.append(elem)

    xml_str = ET.tostring(vector, encoding="unicode")

    import xml.dom.minidom

    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="    ")

    lines = [line for line in pretty_xml.split("\n") if line.strip()]
    if lines and lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="utf-8"?>'

    pretty_xml = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    return True


def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python svg_to_vector.py <input_directory> [--delete]")
        print("  --delete: Delete original SVG files after successful conversion")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    delete_after = "--delete" in sys.argv

    if not input_dir.exists():
        print(f"Error: Directory '{input_dir}' does not exist")
        sys.exit(1)

    svg_files = list(input_dir.glob("*.svg"))

    if not svg_files:
        print(f"No SVG files found in '{input_dir}'")
        sys.exit(0)

    print(f"Found {len(svg_files)} SVG files")

    converted = 0
    failed = []

    for svg_file in svg_files:
        vector_name = svg_file.stem + ".xml"
        output_path = input_dir / vector_name

        try:
            convert_svg_to_vector(svg_file, output_path)
            print(f"✓ {svg_file.name} -> {vector_name}")
            converted += 1

            if delete_after:
                svg_file.unlink()
                print(f"  Deleted: {svg_file.name}")

        except Exception as e:
            print(f"✗ {svg_file.name}: {e}")
            failed.append(svg_file.name)

    print(f"\nConverted: {converted}/{len(svg_files)}")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
