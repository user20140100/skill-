# -*- coding: utf-8 -*-
"""patent-assistant：多模板交底书构建库

支持 6 类公司模板：
  software  软件类      （四段式：背景(一)(二)/方案(一)(二)/创新点/替换）
  hardware  硬件电路类  （问题并入背景(一)；方案要求电路图+工作原理）
  structure 结构类      （背景无(一)(二)子标题；要求结构总图+爆炸图）
  algorithm 算法类      （原生docx；背景技术/方案核心部分/含公式表格）
  gui       外观-软件界面（编号字段填写，无应用状态）
  appearance 外观-一般   （编号字段填写，无发明名称/应用状态）

发明类4种用 DocBuilder（锚点+插删），外观2种用 AppearanceBuilder（字段追加）。
"""
import copy, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "微软雅黑"; MONO = "Consolas"
SIZE = Pt(10.5); IMGW = Cm(14.2)
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")

# 各模板锚点前缀规格
ANCHOR_SPECS = {
    "software": {
        "NAME":   ["发明名称："],
        "STATUS": ["该技术的当前应用状态为："],
        "SEARCH": ["智慧芽检索记录"],
        "BG1":    ["（一）现有技术方案"],
        "BG2":    ["（二）现有技术存在"],
        "SOL":    ["三、本发明方案部分"],
        "SOL1":   ["（一）请给出方案的具体描述"],
        "SOL2":   ["（二）请用一个实际应用"],
        "INNOV":  ["四、请给出关键创新点"],
        "ALT":    ["五、是否有其他可替换方案"],
        "DEL_PAIRS": [("BG1", "BG2"), ("BG2", "SOL"), ("SOL1", "SOL2"),
                      ("SOL2", "INNOV"), ("INNOV", "ALT")],
        "DEL_TAIL_AFTER": "ALT",
    },
    "hardware": {
        "NAME":   ["发明名称："],
        "STATUS": ["该技术的当前应用状态为："],
        "SEARCH": ["智慧芽检索记录"],
        "BG1":    ["（一）原来的技术方案"],
        "BG2":    ["三、本发明方案部分"],            # 背景内容（含问题）插它前
        "SOL":    ["三、本发明方案部分"],
        "SOL1":   ["（一）请给出方案的具体描述，给出具体的电路图"],
        "SOL2":   ["请用一个实际应用的例子"],
        "INNOV":  ["四、请给出关键创新点"],
        "ALT":    ["五、其他可替换方案"],
        "DEL_PAIRS": [("BG1", "SOL"), ("SOL1", "SOL2"),
                      ("SOL2", "INNOV"), ("INNOV", "ALT")],
        "DEL_TAIL_AFTER": "ALT",
    },
    "structure": {
        "NAME":   ["发明名称："],
        "STATUS": ["该技术的当前应用状态为："],
        "SEARCH": ["智慧芽检索记录"],
        "BG1":    ["原来的技术方案是怎么样的"],
        "BG2":    ["三、本发明方案部分"],
        "SOL":    ["三、本发明方案部分"],
        "SOL1":   ["（一）请给出方案的具体描述，给出具体的结构总图"],
        "SOL2":   ["请用一个实际应用的例子"],
        "INNOV":  ["四、请给出关键创新点"],
        "ALT":    ["四、其他可替换方案"],             # 模板编号如此，保留
        "DEL_PAIRS": [("BG1", "SOL"), ("SOL1", "SOL2"),
                      ("SOL2", "INNOV"), ("INNOV", "ALT")],
        "DEL_TAIL_AFTER": "ALT",
    },
    "algorithm": {
        "NAME":   ["发明名称："],
        "STATUS": ["该技术的当前应用状态为："],
        "SEARCH": ["智慧芽检索记录"],
        "BG1":    ["（一）现有技术的简介"],
        "BG2":    ["（二）现有技术存在什么样的问题"],
        "SOL":    ["三、本发明技术方案"],
        "SOL1":   ["四、请给出关键创新点的说明"],    # 方案内容插 INNOV 前
        "SOL2":   ["四、请给出关键创新点的说明"],
        "INNOV":  ["四、请给出关键创新点的说明"],
        "ALT":    ["其他可替换方案"],
        "DEL_PAIRS": [("BG1", "BG2"), ("BG2", "SOL"), ("SOL示例", "INNOV"), ("INNOV", "ALT")],
        "DEL_TAIL_AFTER": "ALT",
    },
}

# 外观类字段前缀
GUI_FIELDS = {
    "name": "1. 本外观设计产品的名称",
    "purpose": "2. 本外观设计产品的用途",
    "points": "3. 本外观设计产品的设计要点",
    "omit_views": "4. 省略视图",
    "best_view": "5. 最能表明本外观设计设计要点的图片或照片",
    "basic_design": "6. 指定基本设计",
    "ui_purpose": "7. 界面用途",
    "design1_main": "8.设计1主视图界面为",
    "design2_main": "9.设计2主视图界面为",
}
APPEARANCE_FIELDS = {
    "name": "1. 本外观设计产品的名称",
    "purpose": "2. 本外观设计产品的用途",
    "points": "3. 本外观设计产品的设计要点",
    "views": "4. 外观设计视图",
    "best_view": "5. 最能表明本外观设计设计要点的图片或照片",
    "basic_design": "6. 指定基本设计",
    "ui_purpose": "7. 界面用途",
}


def _set_run(r, text=None, bold=None, size=SIZE, color=None, name=FONT):
    if text is not None: r.text = text
    r.font.name = name; r.font.size = size
    rPr = r._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:eastAsia'), FONT if name == MONO else name)
    rf.set(qn('w:ascii'), name); rf.set(qn('w:hAnsi'), name)
    if bold is not None: r.font.bold = bold
    if color: r.font.color.rgb = color


def _add_md_runs(p, text, size=SIZE, base_bold=False):
    """解析 **加粗** 标记生成 run 序列"""
    pos = 0
    for m in BOLD_RE.finditer(text):
        if m.start() > pos:
            _set_run(p.add_run(), text[pos:m.start()], bold=base_bold, size=size)
        _set_run(p.add_run(), m.group(1), bold=True, size=size)
        pos = m.end()
    if pos < len(text):
        _set_run(p.add_run(), text[pos:], bold=base_bold, size=size)


def _set_cell_borders(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        e = OxmlElement(f'w:{edge}')
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:color'), '000000')
        borders.append(e)
    tcPr.append(borders)


class _Base:
    """共用：段落/代码/图/表格插入"""
    doc = None

    def _new_par(self, anchor, style="正文 A"):
        p = anchor.insert_paragraph_before("")
        try: p.style = self.doc.styles[style]
        except KeyError: pass
        return p

    def P(self, anchor, text, bold=False, size=SIZE, space_after=4):
        p = self._new_par(anchor)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.25
        _add_md_runs(p, text, size=size, base_bold=bold)
        return p

    def CODE(self, anchor, lines, size=Pt(9)):
        for ln in lines.split("\n"):
            p = self._new_par(anchor)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.left_indent = Cm(0.5)
            _set_run(p.add_run(), ln if ln else " ", size=size, name=MONO,
                     color=RGBColor(0x30, 0x30, 0x30))
        self._new_par(anchor).paragraph_format.space_after = Pt(6)

    def IMG(self, anchor, path, caption, width=IMGW):
        p = self._new_par(anchor); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(path, width=width)
        c = self._new_par(anchor); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_after = Pt(8)
        _set_run(c.add_run(), caption, size=Pt(9), color=RGBColor(0x40, 0x40, 0x40))

    def EMPTY(self, anchor):
        return self._new_par(anchor)

    def table(self, anchor, header, rows, cell_size=Pt(9.5)):
        t = self.doc.add_table(rows=1 + len(rows), cols=len(header))
        anchor._p.addprevious(t._tbl)
        self._fill_row(t.rows[0], header, bold=True, size=cell_size)
        for i, row in enumerate(rows):
            self._fill_row(t.rows[i + 1], row, size=cell_size)
        return t

    def _fill_row(self, row, values, bold=False, size=Pt(9.5)):
        for cell, v in zip(row.cells, values):
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            _add_md_runs(p, v, size=size, base_bold=bold)
            _set_cell_borders(cell)

    def after(self, anchor):
        """返回 AfterInserter：内容按序插在 anchor 之后"""
        return AfterInserter(self, anchor)


class DocBuilder(_Base):
    """发明类模板（software/hardware/structure/algorithm）构建器"""

    def __init__(self, src_docx, out_docx, ttype="software"):
        assert ttype in ANCHOR_SPECS, f"未知模板类型: {ttype}"
        self.doc = Document(src_docx)
        self.out = out_docx
        self.ttype = ttype
        spec = ANCHOR_SPECS[ttype]
        paras = self.doc.paragraphs

        def find(prefixes):
            for p in paras:
                t = p.text.strip()
                if any(t.startswith(pre) for pre in prefixes):
                    return p
            raise RuntimeError(f"[{ttype}] 锚点未找到: {prefixes}")

        class A: pass
        self.A = A()
        for key in ("NAME", "STATUS", "SEARCH", "BG1", "BG2", "SOL",
                    "SOL1", "SOL2", "INNOV", "ALT"):
            if key in spec:
                setattr(self.A, key, find(spec[key]))
        self._spec = spec

    def fill_name(self, name):
        if hasattr(self.A, "NAME"):
            _set_run(self.A.NAME.add_run(), name, bold=True)

    def fill_status(self, letter):
        if hasattr(self.A, "STATUS"):
            _set_run(self.A.STATUS.add_run(), letter, bold=True)

    def fill_search_table(self, rows_data):
        """智慧芽表：[(检索关键词, 检索结果, 不同点), ...]"""
        tbl = self.doc.tables[0]
        while len(tbl.rows) < 1 + len(rows_data):
            tbl._tbl.append(copy.deepcopy(tbl.rows[-1]._tr))
        for i, (k, r, d) in enumerate(rows_data):
            c = tbl.rows[i + 1].cells
            for cell, v, b in zip(c, (k, r, d), (True, False, False)):
                cell.text = ""
                p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(1)
                _add_md_runs(p, v, size=Pt(9.5), base_bold=b)
                _set_cell_borders(cell)

    def delete_examples(self):
        """按模板规格删除全部示例区（勿手写，易漏）。
        锚点 key 支持 "X示例" 形式：X 锚点之后第一个 示例：/举例： 开头的段落"""
        body = self.doc.element.body
        for a_key, b_key in self._spec["DEL_PAIRS"]:
            if a_key.endswith("示例"):
                a = self._first_example_after(getattr(self.A, a_key[:-2]))
            else:
                a = getattr(self.A, a_key)
            b = getattr(self.A, b_key)
            if a is None or a._p is b._p:
                continue
            self._delete_between(a, b)
            if a_key.endswith("示例"):
                # 示例锚点段落本身也要删除（_delete_between 不含起点）
                a._p.getparent().remove(a._p)
        tail = getattr(self.A, self._spec["DEL_TAIL_AFTER"])
        started, to_del = False, []
        for el in body.iterchildren():
            if el is tail._p: started = True; continue
            if started and el.tag == qn('w:p'): to_del.append(el)
        for el in to_del: body.remove(el)

    def _first_example_after(self, anchor):
        body = self.doc.element.body
        started = False
        for el in body.iterchildren():
            if el is anchor._p: started = True; continue
            if started and el.tag == qn('w:p'):
                if "".join(el.itertext()).strip().startswith(("示例：", "举例：", "示例")):
                    for p in self.doc.paragraphs:
                        if p._p is el: return p
        return None

    def _delete_between(self, a, b):
        body = self.doc.element.body
        started, to_del = False, []
        for el in body.iterchildren():
            if el is a._p: started = True; continue
            if el is b._p: break
            if started and el.tag == qn('w:p'): to_del.append(el)
        for el in to_del: body.remove(el)

    def save(self, verify=True):
        self.doc.save(self.out)
        if verify:
            d = Document(self.out)
            leftover = [p.text[:30] for p in d.paragraphs
                        if p.text.strip().startswith(("示例：", "举例："))]
            print(f"✓ 已生成: {self.out} [{self.ttype}]")
            print(f"  段落: {len(d.paragraphs)} | 表格: {len(d.tables)}")
            print(f"  残留示例: {leftover if leftover else '无 ✓'}")
            if leftover:
                print("  ⚠️ 有残留示例，请检查 delete_examples！")


class AppearanceBuilder(_Base):
    """外观类模板（gui/appearance）构建器：编号字段追加式填写"""

    def __init__(self, src_docx, out_docx, ttype="gui"):
        assert ttype in ("gui", "appearance"), f"外观类仅支持 gui/appearance: {ttype}"
        self.doc = Document(src_docx)
        self.out = out_docx
        self.ttype = ttype
        self._fields = GUI_FIELDS if ttype == "gui" else APPEARANCE_FIELDS
        self._name_para = None
        for p in self.doc.paragraphs:
            if p.text.strip().startswith("发明名称："):
                self._name_para = p; break
        self._prompt_cache = {}

    def _find_prompt(self, prefix):
        if prefix in self._prompt_cache:
            return self._prompt_cache[prefix]
        for p in self.doc.paragraphs:
            if p.text.strip().startswith(prefix):
                self._prompt_cache[prefix] = p
                return p
        raise RuntimeError(f"[{self.ttype}] 字段未找到: {prefix}")

    def fill_field(self, key, text):
        """编号字段提示后追加内容：fill_field("name", "XX摄像设备")"""
        prompt = self._find_prompt(self._fields[key])
        _set_run(prompt.add_run(), text, bold=True)

    def fill_name(self, name):
        """gui 模板的发明名称（appearance 无此字段自动跳过）"""
        if self._name_para is not None:
            _set_run(self._name_para.add_run(), name, bold=True)

    def P_after_field(self, key, text, bold=False):
        """编号字段段落之后插入正文段（如界面用途详述）"""
        prompt = self._find_prompt(self._fields[key])
        return self.after(prompt).P(text, bold=bold)

    def fill_search_table(self, rows_data):
        tbl = self.doc.tables[0]
        while len(tbl.rows) < 1 + len(rows_data):
            tbl._tbl.append(copy.deepcopy(tbl.rows[-1]._tr))
        for i, (k, r, d) in enumerate(rows_data):
            c = tbl.rows[i + 1].cells
            for cell, v, b in zip(c, (k, r, d), (True, False, False)):
                cell.text = ""
                p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(1)
                _add_md_runs(p, v, size=Pt(9.5), base_bold=b)
                _set_cell_borders(cell)

    def delete_examples(self):
        """删除模板尾部示例块（'示例：'起到文末）"""
        body = self.doc.element.body
        started, to_del = False, []
        for el in body.iterchildren():
            if el.tag == qn('w:p'):
                texts = "".join(el.itertext()).strip()
                if not started and texts.startswith(("示例：", "示例一", "示例二")):
                    started = True
                if started:
                    to_del.append(el)
        for el in to_del: body.remove(el)

    def save(self, verify=True):
        self.doc.save(self.out)
        if verify:
            d = Document(self.out)
            print(f"✓ 已生成: {self.out} [{self.ttype}]")
            print(f"  段落: {len(d.paragraphs)} | 表格: {len(d.tables)}")


class AfterInserter:
    """在锚点段落之后按序插入内容"""
    def __init__(self, builder, anchor_para):
        self.b = builder
        self.last_el = anchor_para._p

    def _new_par(self):
        p = self.b.doc.add_paragraph()
        self.last_el.addnext(p._p)
        self.last_el = p._p
        try: p.style = self.b.doc.styles["正文 A"]
        except KeyError: pass
        return p

    def P(self, text, bold=False, size=SIZE, space_after=4):
        p = self._new_par()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.25
        _add_md_runs(p, text, size=size, base_bold=bold)
        return p

    def CODE(self, lines, size=Pt(9)):
        for ln in lines.split("\n"):
            p = self._new_par()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.left_indent = Cm(0.5)
            _set_run(p.add_run(), ln if ln else " ", size=size, name=MONO,
                     color=RGBColor(0x30, 0x30, 0x30))
        self._new_par().paragraph_format.space_after = Pt(6)

    def IMG(self, path, caption, width=IMGW):
        p = self._new_par(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(path, width=width)
        c = self._new_par(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_after = Pt(8)
        _set_run(c.add_run(), caption, size=Pt(9), color=RGBColor(0x40, 0x40, 0x40))

    def table(self, header, rows, cell_size=Pt(9.5)):
        t = self.b.doc.add_table(rows=1 + len(rows), cols=len(header))
        self.last_el.addnext(t._tbl)
        self.last_el = t._tbl
        self.b._fill_row(t.rows[0], header, bold=True, size=cell_size)
        for i, row in enumerate(rows):
            self.b._fill_row(t.rows[i + 1], row, size=cell_size)
        return t
