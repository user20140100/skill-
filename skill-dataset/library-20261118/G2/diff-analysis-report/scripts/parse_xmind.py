"""diff-analysis-report 固化脚本：解析 xmind 为缩进文本树（兼容新旧格式）。

用法: python -I parse_xmind.py <xmind路径> <输出txt路径>
- 老格式 zip 内 content.xml（ElementTree 遍历 topic 树）；新格式 content.json
- 输出 UTF-8 直写文件（-I 隔离模式会忽略 PYTHONIOENCODING，勿依赖 stdout）
- 首行输出 zip 条目与格式标记；末尾输出 ### leaf_cases=N（含【预期结果】的叶子用例数）
"""
import sys
import zipfile
import json
import xml.etree.ElementTree as ET


def walk_json(topic, depth, lines):
    if isinstance(topic, dict):
        title = topic.get("title", "")
        lines.append("  " * depth + "- " + str(title).replace("\n", " "))
        labels = topic.get("labels") or []
        notes = (topic.get("notes") or {})
        if labels:
            lines.append("  " * (depth + 1) + "[labels] " + " | ".join(str(x) for x in labels))
        plain = None
        if isinstance(notes, dict):
            plain = notes.get("plain")
            if isinstance(plain, dict):
                plain = plain.get("content")
        if plain:
            lines.append("  " * (depth + 1) + "[note] " + str(plain).replace("\n", " "))
        children = topic.get("children") or {}
        for key in ("attached", "detached"):
            for child in children.get(key) or []:
                walk_json(child, depth + 1, lines)
    elif isinstance(topic, list):
        for t in topic:
            walk_json(t, depth, lines)


def walk_xml(node, depth, lines):
    tag = node.tag.split("}")[-1]
    if tag == "topic":
        lines.append("  " * depth + "- [topic]")
        for child in node:
            walk_xml(child, depth + 1, lines)
        return
    if tag == "title":
        text = "".join(node.itertext()).strip()
        if lines and lines[-1].strip() == "- [topic]":
            lines[-1] = "  " * (depth - 1) + "- " + text.replace("\n", " ")
        else:
            lines.append("  " * depth + "title: " + text.replace("\n", " "))
        return
    if tag == "label":
        text = "".join(node.itertext()).strip()
        if text:
            lines.append("  " * depth + "[label] " + text.replace("\n", " "))
        return
    if tag == "notes":
        text = "".join(node.itertext()).strip()
        if text:
            lines.append("  " * depth + "[note] " + text.replace("\n", " "))
        return
    for child in node:
        walk_xml(child, depth, lines)


def main():
    xmind_path, out_path = sys.argv[1], sys.argv[2]
    lines = []
    with zipfile.ZipFile(xmind_path) as z:
        names = z.namelist()
        lines.append("### zip entries: " + ", ".join(names))
        if "content.json" in names:
            data = json.loads(z.read("content.json").decode("utf-8"))
            lines.append("### format: content.json")
            for sheet in data:
                lines.append("### sheet: " + str(sheet.get("id", "")))
                root = sheet.get("rootTopic")
                walk_json(root, 0, lines)
        elif "content.xml" in names:
            xml_bytes = z.read("content.xml")
            lines.append("### format: content.xml")
            root = ET.fromstring(xml_bytes)
            walk_xml(root, 0, lines)
        else:
            lines.append("### ERROR: no content.json/content.xml found")
    leaf = sum(1 for ln in lines if "【预期结果】" in ln)
    lines.append("### leaf_cases=%d" % leaf)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    sys.exit(0 if not any(ln.startswith("### ERROR") for ln in lines) else 2)


if __name__ == "__main__":
    main()
