# -*- coding: utf-8 -*-
"""每份交底书唯一需要写的脚本：内容映射（真实完整示例：开机logo交底书）

前置：
  1. 模板已转为 docx:  soffice --headless --convert-to docx --outdir /tmp/work <skill>/assets/交底书模板-软件类-已更新.doc
  2. mermaid 已渲染:   python3 <skill>/scripts/render_mermaid.py <md> -o /tmp/mmd
  3. 本脚本改 CONTENT 部分为新交底书内容后运行
后置：
  4. python3 <skill>/scripts/clean_media.py <输出docx>
  5. soffice --headless --convert-to doc --outdir /tmp/work <输出docx>
"""
import sys
sys.path.insert(0, __import__("os").environ.get("SKILL_DIR", "") + "/scripts")
from docx_helpers import DocBuilder

SRC = "/tmp/work/交底书模板-软件类-已更新.docx"
OUT = "/tmp/work/专利交底书_输出.docx"

b = DocBuilder(SRC, OUT)
A = b.A

# ===== 基本信息 =====
b.fill_name("一种开机logo与开机动画的多品牌预置及工厂切换方法、装置及存储介质")
b.fill_status("C")
b.fill_search_table([
    ("开机logo 工厂 切换", "CN121387390B《...》（深圳大趋智能，有效）", "其为差异化烧录...；本发明..."),
    # ... md 检索表的每一行
])

# ===== 删除模板示例（必须先删后插） =====
b.delete_examples()

# ===== 二（一）现有技术（插在 A.BG2 前） =====
b.P(A.BG2, "ODM厂商用同一主板方案为多个品牌客户生产...")
b.P(A.BG2, "路线1（传统编译式）：...")
b.IMG(A.BG2, "/tmp/mmd/render_fig1.png", "（图1：现有技术四路线）")

# ===== 二（二）问题（插在 A.SOL 前） =====
b.P(A.SOL, "问题1：xxx。", bold=True)
b.P(A.SOL, "问题1的详细描述...")

# ===== 三（一）方案（插在 A.SOL2 前） =====
b.P(A.SOL2, "【步骤概述】", bold=True, size=__import__("docx.shared", fromlist=["Pt"]).Pt(11.5))
b.P(A.SOL2, "S1 固件预置：...")
b.IMG(A.SOL2, "/tmp/mmd/render_fig2.png", "（图2：整体方案流程）")
b.P(A.SOL2, "S1 固件预置详述", bold=True)
b.CODE(A.SOL2, "vendor/\n├── bootlogo/\n│   └── brand_a/logo.bmp")
b.table(A.SOL2, ["优先级", "存放位", "作用"], [["高", "ODM", "预置通道"]])

# ===== 三（二）例子（插在 A.INNOV 前） =====
b.P(A.INNOV, "场景1：xxx", bold=True)
b.P(A.INNOV, "1．第一步...")

# ===== 四、创新点（插在 A.ALT 前） =====
b.P(A.ALT, "创新点1：xxx", bold=True)
b.P(A.ALT, "创新点1详细...")

# ===== 五、替换方案（用 after() 插在五、标题之后，顺序天然正确） =====
ins = b.after(A.ALT)
ins.P("logo生效方式的替换：", bold=True)
ins.P("① ...；② ...")

b.save()  # 自动 fix_alt_heading + 验证
