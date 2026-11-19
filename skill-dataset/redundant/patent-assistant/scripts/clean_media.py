# -*- coding: utf-8 -*-
"""剥离 docx 中未被 document.xml 引用的孤儿媒体（删除示例段后 python-docx 不回收图片）

用法: python3 clean_media.py <docx文件>
效果: 直接原位瘦身（示例：7.1MB → 0.6MB）
"""
import os, re, shutil, sys, zipfile

def main(path):
    with zipfile.ZipFile(path) as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
        rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8")
        names = z.namelist()

    used_rids = set(re.findall(r'r:(?:embed|id)="(rId\d+)"', doc_xml))
    rel_map = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(media/[^"]+)"', rels_xml))
    used_media = {rel_map[r] for r in used_rids if r in rel_map}
    total_media = len(rel_map)
    print(f"媒体引用: {len(used_media)}/{total_media}")

    if len(used_media) == total_media:
        print("无孤儿媒体，无需清理"); return

    new_rels = rels_xml
    for rid, target in rel_map.items():
        if rid not in used_rids:
            new_rels = re.sub(rf'<Relationship Id="{rid}"[^>]*/>', '', new_rels)

    tmp = path + ".tmp"
    before = os.path.getsize(path)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            if name.startswith("word/media/") and name.replace("word/", "", 1) not in used_media:
                continue
            zout.writestr(name, new_rels if name == "word/_rels/document.xml.rels" else zin.read(name))
    shutil.move(tmp, path)
    print(f"✓ {before//1024}KB → {os.path.getsize(path)//1024}KB")

    # 校验可打开
    from docx import Document
    d = Document(path)
    print(f"✓ 重新打开正常: {len(d.paragraphs)}段 {len(d.tables)}表")

if __name__ == "__main__":
    main(sys.argv[1])
