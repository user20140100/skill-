---
name: svg2xml
description: 批量双向转换 SVG 与 Android VectorDrawable XML。支持 SVG→XML（fill-rule evenodd 镂空路径、圆形、矩形）和 XML→SVG（反向还原 path/group/颜色/透明度）。当用户提到 "SVG 转 XML"、"XML 转 SVG"、"转换 SVG"、"VectorDrawable"、"svg to xml"、"xml to svg" 时使用此 skill。
version: 0.1.0
author: yangyuebin
triggers:
  - SVG转XML
  - SVG 转 XML
  - XML转SVG
  - XML 转 SVG
  - 转换SVG
  - 转换 SVG
  - VectorDrawable
  - svg to xml
  - xml to svg
  - svg2xml
  - Android drawable
---

# SVG ↔ VectorDrawable XML Converter

批量双向转换：SVG → Android VectorDrawable XML，以及 VectorDrawable XML → SVG。

## 功能特性

### SVG → XML
- 自动扫描目录下所有 `.svg` 文件
- 正确处理 `fill-rule="evenodd"` 镂空路径（→ `android:fillType="evenOdd"`）
- 支持 `<path>`、`<circle>`、`<rect>`、`<g>` 元素
- 支持填充颜色、描边、透明度
- 可选转换后自动删除原 SVG 文件

### XML → SVG
- 自动扫描目录下所有 `.xml` 文件（自动跳过非 VectorDrawable 的 XML）
- 还原 `android:fillType="evenOdd"` → `fill-rule="evenodd"`
- 还原 `<group>` 的 translate/scale/rotate → SVG `transform`
- 还原 Android 颜色格式（#AARRGGBB）→ SVG hex + opacity
- 还原描边、透明度、clip-path 等属性
- 可选转换后自动删除原 XML 文件

## 使用方法

```
用户：把 res/drawable 目录下的 SVG 文件转换为 VectorDrawable XML
用户：将 src/main/res/drawable 中的 SVG 批量转成 Android 的 vector xml
用户：把 res/drawable 下的 XML 批量转回 SVG
用户：将 VectorDrawable XML 还原为 SVG 并删除原文件
```

## 参数说明

| 参数 | 说明 |
|------|------|
| 目录路径 | 包含文件的目录（支持相对/绝对路径） |
| --delete | 转换成功后删除原文件（可选） |

## 脚本对应关系

| 转换方向 | 脚本 | 输入 | 输出 |
|----------|------|------|------|
| SVG → XML | `svg_to_vector.py` | `*.svg` | `*.xml` |
| XML → SVG | `vector_to_svg.py` | `*.xml` | `*.svg` |

脚本位置：与本 SKILL.md 同目录。

## 执行流程

### SVG → XML
```bash
python3 svg_to_vector.py <目录> [--delete]
```

1. 验证目录存在
2. 扫描所有 `.svg` 文件
3. 逐个转换输出同目录同名 `.xml`
4. 如指定 `--delete`，删除转换成功的 SVG
5. 输出转换统计

### XML → SVG
```bash
python3 vector_to_svg.py <目录> [--delete]
```

1. 验证目录存在
2. 扫描所有 `.xml` 文件
3. 自动识别 VectorDrawable（非 VectorDrawable 自动跳过，不报错）
4. 逐个转换输出同目录同名 `.svg`
5. 如指定 `--delete`，删除转换成功的 XML
6. 输出转换统计（含跳过数量）

## 示例输出

### SVG → XML
```
Found 22 SVG files
✓ ic_tools_calculator.svg -> ic_tools_calculator.xml
✓ ic_tools_pip.svg -> ic_tools_pip.xml
...
Converted: 22/22
```

### XML → SVG
```
Found 15 XML files
✓ ic_home.xml -> ic_home.svg
⚠ layout_main.xml: skipped (Root element is <LinearLayout>, expected <vector>)
...
Converted: 14/15
Skipped (not VectorDrawable): 1
```

## 转换规则

### SVG → XML
1. `icon.svg` → `icon.xml`（同名替换扩展名，同目录输出）
2. 自动添加 `xmlns:android` 命名空间
3. 宽高自动添加 `dp` 单位
4. `fill-rule="evenodd"` → `android:fillType="evenOdd"`
5. `<circle>` / `<rect>` → `<path>` + 路径数据

### XML → SVG
1. `icon.xml` → `icon.svg`（同名替换扩展名，同目录输出）
2. `android:width/height`（dp/px 单位剥离）→ SVG `width/height`
3. `android:viewportWidth/Height` → SVG `viewBox`
4. `android:fillType="evenOdd"` → `fill-rule="evenodd"`
5. `#AARRGGBB` 颜色 → `#RRGGBB` + `fill-opacity`/`stroke-opacity`
6. `<group>` translateX/Y, scaleX/Y, rotation, pivotX/Y → SVG `transform`

## 注意事项

- 确保 Python 3 环境可用（标准库，无需额外安装）
- 复杂 SVG 特效（渐变、滤镜、遮罩）可能不完全支持
- 建议转换后检查生成文件是否正确渲染
