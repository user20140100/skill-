---
name: patent-assistant
description: >
  专利交底书一站式助手 — 融合 patent-disclosure（撰写）、patent-drafting-assistant（创新点评估）、
  patent-search（智慧芽检索）三个 skill 的完整能力，并新增公司标准文档格式自动输出： md 交底书可一键填入公司 6 类 doc
  模板（软件/硬件电路/结构/算法/外观GUI/外观一般）， 严格保留模板样式（字体/页面/表格/签名栏），mermaid 图自动渲染插图，孤儿媒体自动清理。


  用户只需提供一个点子/想法，自动完成：想法扩充与技术方案提炼 → 创新点评估筛选 → 智慧芽专利检索 → 撰写 md 交底书 → 转换为公司标准 doc
  模板格式交付。 每个关键节点向用户确认。


  当用户提到以下内容时触发：

  - "我有个点子/想法"、"帮我评估这个想法能不能申请专利"

  - "写交底书"、"专利交底书"、"生成交底书"、"帮我写一份专利"

  - "专利检索"、"查专利"、"智慧芽"、"有没有类似专利"

  - "把这个 md 按模板转成 doc"、"填入交底书模板"

  - "提炼发明点"、"创新点评估"
author: zhuchengwei
version: 1.1.3
---

# 专利交底书一站式助手

> **来源致谢**：本 skill 由 **zhuchengwei** 将以下三个 skill 融合而成：
>
> | 原 skill | 作者 | 融合内容 |
> |----------|------|---------|
> | [patent-disclosure](https://skills.gz.cvte.cn/skill/patent-disclosure) | 刘少杰 (liushaojie) | 撰写流程、md 模板结构、写作原则 |
> | [patent-drafting-assistant](https://skills.gz.cvte.cn/skill/patent-drafting-assistant) | 王志伟 (wangzhiwei7497) | 四阶段技术分析方法、五维创新点评估体系 |
> | [patent-search](https://skills.gz.cvte.cn/skill/patent-search) | 刘少杰 (liushaojie) | 智慧芽 Playwright 检索流程、差异分析方法 |
>
> **新增能力**：
> - md 交底书 → 公司 6 类 doc 模板一键转换（严格保留模板样式：字体/页面/表格边框/签名栏）
> - mermaid 流程图自动渲染为高清图片插入（外发前安全确认）
> - 模板示例内容自动清除、孤儿媒体自动瘦身、PDF 逐页验证交付

从一个点子到一份符合公司模板的 doc 交底书，五阶段流水线，**每个阶段产出都向用户确认后再继续**：

```
点子 → ① 想法扩充 → ② 创新点评估 → ③ 专利检索 → ④ md交底书 → ⑤ doc交付
        (确认方案)     (确认创新点)    (确认检索)     (确认草稿)     (验证交付)
```

用户可以只提供一个粗糙点子，也可以提供完整技术方案/PRD/代码——从哪个阶段开始取决于输入完整度。用户也可以指定只执行某一段（如"只检索"或"只转doc"）。

## 模板类型矩阵（阶段一确定，6 选 1）

| ttype | 模板文件（assets/） | 适用 | 结构特点 |
|-------|--------------------|------|---------|
| `software` | 交底书模板-软件类-已更新.doc | 方法/系统/软件方案 | 背景(一)(二)/方案(一)(二)/创新点/替换 五段式 |
| `hardware` | 交底书模板-硬件类--电路更新.doc | 电路/电源/硬件改进 | 问题并入背景(一)；方案需**电路图+工作原理** |
| `structure` | 交底书模板-结构类-已更新.doc | 机械结构/装配关系 | 背景无子标题；需**结构总图+爆炸图+部件标注**（附CAD） |
| `algorithm` | 交底书模板-算法-已更新.docx（原生docx） | 算法/模型/AI方法 | 背景技术；方案为**核心部分**；含公式/模型框图 |
| `gui` | 外观交底书模板（软件界面）-已更新.doc | GUI界面外观 | 编号字段1-9填写；无应用状态；需界面图 |
| `appearance` | 外观交底书模板（一般外观）-已更新.doc | 产品外观造型 | 编号字段1-7填写；无发明名称/状态；需六视图 |

**选择规则**：按点子的技术形态判断；含糊时（如"触摸结构+控制方法"）**问用户**要申请的类型。一个点子可拆多份不同类型交底书（如结构+方法各一份）。

---

## 阶段一：想法扩充与技术方案提炼

**输入**：用户的点子（可能只有一两句话）或技术材料（PRD/会议记录/代码）。

**粗糙点子的扩充方法**：
1. 从点子中识别：技术领域、面向的场景/产品形态
2. 结合领域知识补全：现有技术通常怎么做？这个点子改进了什么？技术上怎么实现？
3. 补全后的方案包含：问题 → 技术手段 → 技术效果
4. 若关键信息缺失（如运行平台、通信方式），**列出问题清单向用户询问**（一次问完，不要逐条追问）

**已有技术材料的提炼**：
阅读全部材料，提炼四要素：
1. **技术领域**
2. **要解决的问题**（现有技术的不足）
3. **核心技术方案**（怎么解决）
4. **关键创新点**（与现有技术的差异）

**产出确认**：向用户展示「领域/问题/方案/创新点」四要素卡片 + **模板类型建议**（按矩阵 6 选 1，含糊时问用户），确认无误后进入阶段二。

---

## 阶段二：创新点评估与筛选

**候选创新点清单**：列出 3-8 个候选点，每个含技术特征、解决的问题、技术效果、技术深度（⭐1-5）。

**五维评估**（加权）：

| 维度 | 评估标准 | 权重 |
|------|---------|------|
| 新颖性 | 是否有相同/相似方案公开 | 30% |
| 创造性 | 是否非显而易见的技术改进 | 30% |
| 实用性 | 能否实际应用并产生效果 | 20% |
| 技术深度 | 复杂度和实现难度 | 10% |
| 商业价值 | 应用前景和竞争壁垒 | 10% |

**产出确认**：展示评分表 + 建议写入交底书的创新点（建议选 3-5 个高分点），用户可增删调整。确认后进入阶段三。

---

## 阶段三：智慧芽专利检索

**检索关键词**：从确认的创新点提炼，每个创新点 1-2 组，每组 3-5 个词。

**前置条件**：Playwright MCP 工具 + 智慧芽账号（公司 OA 可 SSO）。

**若 Playwright/智慧芽不可用**，降级方案（询问用户选哪个）：
- A. 把检索关键词和智慧芽入口给用户，用户手动检索后粘贴结果
- B. 跳过检索，检索表留占位（标注"待检索"），后续补

**检索流程**（Playwright）：

1. **登录协助**：打开 `https://analytics.zhihuiya.com/search/input/simple`；若跳登录页，告知用户在浏览器完成登录后确认。成功标志：URL 含 `/search/input/simple`，标题含"简单搜索"。

2. **逐组执行检索**（URL 直跳比操作 UI 稳定）：
```
https://analytics.zhihuiya.com/search/result/tablelist/1?sort=desc&limit=20&q={URL编码关键词}&_type=query&search_mode=publication
```
   跳转后等 3 秒，`browser_snapshot` 提取：总结果数（`共 N 条`）、专利号（`CN[0-9]+[A-Z]`）、标题、申请人。

3. **结果数调整策略**：
   | 结果数 | 策略 |
   |--------|------|
   | 0 | 去掉最专业的词，换同义词重试 |
   | 1-20 | 理想，直接分析 |
   | 20-100 | 重点看前 20 条 |
   | >100 | 加限定词缩小 |

4. **筛选**：每组选 1-3 篇最相关专利（标题概念相近/同行业申请人/领域接近）。

5. **差异分析**（三个维度）：应用场景差异、技术路线差异、创新点覆盖。每条差异要具体写出"该专利做了什么 vs 本提案做了什么不同的事"。

6. **检索报告**：汇总表（关键词/结果数/最相关专利）+ 重点专利分析 + 总体结论（差异化创新点清单）。

**产出确认**：展示检索报告 + 即将填入交底书检索表的行，用户确认后进入阶段四。

> 注意事项：Playwright 报 "Browser is already in use" 时先 `pkill -f "chrome.*--remote-debugging"`；搜索框是 contenteditable div；快照很大时用 grep 提取。

---

## 阶段四：撰写 md 交底书

读取 `references/template.md`（软件类基础结构），**按模板类型调整结构**（写作原则：**具体到可实现**——让刚入行的人照着能做出来；**问题-方案-创新点一一对应**）：

### 通用结构（software 为基准）

| 章节 | 要求 |
|------|------|
| 声明确认 | 保留原文，签名留空 |
| 一、基本信息 | 发明名称（"一种[技术手段]的[目的]方法及系统"格式）+ 应用状态 ABCD（问用户）+ 阶段三检索结果填表 |
| 二（一）现有技术 | 分步骤描述 + Mermaid 流程图；调研行业主流方案列表格 |
| 二（二）问题 | 问题1-N，加粗标题+展开；与三的方案一一对应 |
| 三（一）方案 | 步骤概述（S1-SN）→ 整体流程图 → 逐步骤详述（技术问题/技术方案/细节图/重要技术点） |
| 三（二）实际例子 | 一个具体场景串联全方案（分阶段/步骤） |
| 四、创新点 | 创新点1-N，加粗标题+与现有技术对比 |
| 五、可替换方案 | 核心模块的替代实现 + 替换后方案仍成立的原因 |

### 各类型差异

| ttype | md 结构调整 | 图表要求 |
|-------|------------|---------|
| `hardware` | 问题并入背景(一)；方案需按**电路构成→各部分作用→工作原理（正常/保护等模式分态列举）**展开 | 电路框图（用户提供电路图，或用 mermaid 画功能框图） |
| `structure` | 背景不分(一)(二)；方案按**结构总图→爆炸图→逐部件（名称/序号/结构/功能）→细节放大**展开 | 结构图用户出（CAD/示意图）；mermaid 画装配关系；提醒用户备 CAD 附件 |
| `algorithm` | 背景=现有技术简介；方案=核心部分（**必须给出完整可实现方案**，含数学公式、模型结构、输入输出定义）；可多实施例 | 模型框图（graph TB）；公式用 LaTeX 行内 `$...$`；数据结构列表格 |
| `gui` | 不用通用结构！按编号字段：1名称（"用于XX的图形用户界面"）2用途 3设计要点（在于图形用户界面）4省略视图 5最要点图片 6基本设计 7界面用途 8-9各设计主视图界面 | 界面截图（用户提供，≥200DPI，前景背景色差明显）；**用文字写清各界面切换/交互逻辑**；标注重点保护界面 |
| `appearance` | 按编号字段：1名称 2用途 3设计要点 4视图（设计1线条图/设计2带虚线/设计3效果图）5最要点图片 6基本设计 7界面用途如有 | 六视图由用户出（JPG+DWG+立体图打包附件）；文字描述设计要点与形状特征 |

**Mermaid 图规范**：整体架构 `graph TB`、状态转换 `stateDiagram-v2`、时序交互 `sequenceDiagram`、数据流 `graph LR`；节点文字简洁，复杂说明放图外文字。

**产出确认**：保存为 `专利交底书_{名称简称}.md`，展示全文给用户审阅修改，确认后进入阶段五。

---

## 阶段五：转公司 doc 模板

把 md 填入公司模板 `assets/交底书模板-软件类-已更新.doc`（严格保留模板样式）。

### 5.1 环境准备

```bash
python3 -c "import docx" 2>/dev/null || pip install python-docx --break-system-packages -q
SOFFICE=$(which soffice || ls /tmp/lo/install/opt/libreoffice*/program/soffice 2>/dev/null | head -1)
if [ -z "$SOFFICE" ]; then
  VER=$(curl -s https://download.documentfoundation.org/libreoffice/stable/ | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
  cd /tmp && curl -sL -o lo.tar.gz "https://download.documentfoundation.org/libreoffice/stable/$VER/deb/x86_64/LibreOffice_${VER}_Linux_x86-64_deb.tar.gz" \
  && mkdir -p /tmp/lo && cd /tmp/lo && tar xzf /tmp/lo.tar.gz \
  && cd LibreOffice*_Linux_x86-64_deb/DEBS && mkdir -p /tmp/lo/install \
  && for d in *.deb; do dpkg-deb -x "$d" /tmp/lo/install 2>/dev/null; done
  SOFFICE=$(ls /tmp/lo/install/opt/libreoffice*/program/soffice | head -1)
fi
```

### 5.2 Mermaid 图渲染（⚠️ 安全确认）

**必须先问用户**：mermaid.ink 是外部服务，流程图源码含未公开技术细节，外发有泄密风险。选项：
- A. 同意外发 → mermaid.ink 渲染（最简单）
- B. 本地渲染 → `npm install @mermaid-js/mermaid-cli` + mmdc（需 chrome，配置 --no-sandbox）
- C. 用户自托管渲染服务地址 → `render_mermaid.py` 不支持时改 curl 自托管 API

用户选 A 后：
```bash
python3 <skill目录>/scripts/render_mermaid.py <md文件> -o /tmp/mmd
# 幂等可重试；失败图会列出，重跑只补缺失
```

### 5.3 模板转换与内容映射

**按 ttype 选模板文件**（algorithm 已是 docx 无需转换；其余 doc 先转 docx）：

| ttype | 模板文件 |
|-------|---------|
| software | 交底书模板-软件类-已更新.doc |
| hardware | 交底书模板-硬件类--电路更新.doc |
| structure | 交底书模板-结构类-已更新.doc |
| algorithm | 交底书模板-算法-已更新.docx（直接用） |
| gui | 外观交底书模板（软件界面）-已更新.doc |
| appearance | 外观交底书模板（一般外观）-已更新.doc |

```bash
export HOME=$HOME && $SOFFICE --headless --convert-to docx --outdir /tmp/work <skill目录>/assets/<模板文件>
```

**发明类 4 种**（software/hardware/structure/algorithm）用 DocBuilder：

```python
import sys; sys.path.insert(0, "<skill目录>/scripts")
from docx_helpers import DocBuilder
from docx.shared import Pt

b = DocBuilder("/tmp/work/<模板>.docx", "/tmp/work/输出.docx", ttype="software")  # 按类型传 ttype
A = b.A
b.fill_name("一种xxx方法及系统")      # 发明名称
b.fill_status("B")                    # 应用状态字母（问用户）
b.fill_search_table([(关键词, 结果, 不同点), ...])  # 阶段三的检索行
b.delete_examples()                   # ★ 一键删全部模板示例（按 ttype 内置删除区）

# 锚点按类型自动适配：背景内容→A.BG2 前；方案+例子→A.INNOV 前；创新点→A.ALT 前
b.P(A.BG2, "正文...支持**加粗**"); b.CODE(A.BG2, "代码...")
b.IMG(A.BG2, "/tmp/mmd/render_fig1.png", "（图1：xxx）")
b.table(A.BG2, ["列1","列2"], [["a","b"]])
b.P(A.INNOV, "S1 xxx：...", size=Pt(11.5))   # 方案（hardware 需分"正常/保护"工作模式；structure 需逐部件标注）
b.P(A.ALT, "创新点1：...", bold=True)
ins = b.after(A.ALT)                  # 替换方案 → after() 插标题后
ins.P("替换方式：", bold=True); ins.P("①...")
b.save()                              # 自动验证：残留示例检查
```

**外观类 2 种**（gui/appearance）用 AppearanceBuilder（编号字段追加式）：

```python
from docx_helpers import AppearanceBuilder

b = AppearanceBuilder("/tmp/work/<外观模板>.docx", "/tmp/work/输出.docx", ttype="gui")
b.fill_name("用于XX的图形用户界面")    # 仅 gui 有发明名称；appearance 自动跳过
b.fill_field("name", "XX设备的图形用户界面")   # 1.产品名称
b.fill_field("purpose", "xx用途说明")          # 2.用途
b.fill_field("points", "...")                  # 3.设计要点（gui 固定"在于图形用户界面"可不动）
b.fill_field("omit_views", "省略左/右/俯/仰视图") if ttype=="gui" else None  # 4.省略视图
b.fill_field("basic_design", "包括N项设计，设计1为基本设计")  # 6.基本设计（改N）
b.fill_field("ui_purpose", "...")              # 7.界面用途
b.P_after_field("ui_purpose", "各界面交互逻辑详述：...", bold=False)  # 字段后插正文
b.fill_search_table([(关键词, 结果, 不同点), ...])
b.delete_examples()                    # 删尾部示例块
b.save()
```

> 外观类图片（六视图/界面图）按模板要求**不放 word 内**，提醒用户单独打包 JPG/DWG/立体图作为附件上传。

### 5.4 清理与转 doc

```bash
python3 <skill目录>/scripts/clean_media.py /tmp/work/输出.docx   # 剥孤儿媒体（否则10MB+）
$SOFFICE --headless --convert-to doc --outdir /tmp/work /tmp/work/输出.docx
```

### 5.5 验证交付（必做）

```bash
$SOFFICE --headless --convert-to pdf --outdir /tmp/work <输出.doc>
pdftoppm -png -r 55 -f 1 -l 3 <输出.pdf> page    # Read 工具看图验证
```

**交付清单**：
- [ ] 第1页：发明名称已填、状态字母已标、声明确认完整
- [ ] 智慧芽表：行数=检索条数，边框完整
- [ ] 全部图表渲染、有编号图注、中文无乱码
- [ ] 章节顺序：四→创新点→**五、标题→替换方案**
- [ ] 文件 <2MB；无"示例：应用程序"残留
- [ ] 同时交付 .doc（公司格式）+ .docx（备用）

---

## 模板结构速查（阶段五锚点，按 ttype 自动适配）

```
发明类（software/hardware/structure/algorithm）：
[发明名称：] ← A.NAME 追加          [应用状态：] ← A.STATUS 追加字母（外观类无）
[智慧芽表格] ← fill_search_table
[背景内容] → 插 A.BG2 前（hardware/structure 无独立问题节，问题并入背景）
[方案+例子内容] → 插 A.INNOV 前
[创新点内容] → 插 A.ALT 前          [替换方案] → b.after(A.ALT)

外观类（gui/appearance）：
[发明名称：] ← fill_name（仅gui）   [编号字段1-9] ← fill_field(key, text)
[字段后正文] ← P_after_field(key, text)   [智慧芽表格] ← fill_search_table
```

**易错点**：
| 坑 | 解法 |
|---|------|
| 漏删模板示例（BG1/SOL1 段最易漏） | 只用 `delete_examples()`，勿手写删除 |
| 五、标题跑到内容后面 | 用 `b.after(A.ALT)`，勿用 `b.P(A.ALT,...)` |
| 孤儿媒体撑大文件 | `clean_media.py` 必跑 |
| md 的申请类型字段 | 模板无此字段，不写入 |
| md 末尾生成说明/待确认项 | 内部元信息，不写入 doc |
| soffice 报错 | 前置 `export HOME=$HOME` |

## 字体规范（与模板一致）

正文微软雅黑 10.5pt 行距1.25 ｜ 小节标题 11.5pt 加粗 ｜ 图注 9pt 灰居中 ｜ 代码块 Consolas 9pt 缩进0.5cm ｜ 表格 9.5pt 首行加粗全边框 ｜ 图宽 14.2cm
