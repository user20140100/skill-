# BizSolution 生成物存放约定

技能包内的 `examples/` 存放**黄金范例**（随技能版本维护）；**某次真实项目产出的** MD / HTML / PDF 不应默认写回技能目录，以免与仓库/个人技能分发混淆。

## 推荐：写在「用户当前工作项目」里

在**用户正在交付的业务或系统项目**根目录下建立统一归档（便于 Git、评审与版本管理）：

```text
<项目根目录>/
└── docs/
    └── solutions/
        └── <YYYY-MM-DD-主题英文或拼音>/   # 每次方案一个子目录
            ├── README.md                  # 可选：索引、评审结论、链接
            ├── 需求方案.md                 # 主文档（Markdown 源稿，推荐）
            ├── 需求方案.html               # 可选：由 MD 导出（Pandoc、VS Code、打印为 PDF 等）
            ├── 需求方案.pdf                # 可选：对外评审/归档用
            └── assets/                     # 可选：截图、从 drawio 导出的 png/svg
```

**命名建议**：同一主题迭代可在子目录加后缀，例如 `2026-05-03-delivery-transparency-v2`。

## 备选：仅本地草稿、不进入业务仓库

若暂无项目仓库，可在用户文档区自建目录，例如：

`~/Documents/Work/AI/solutions/<主题>/`

仍建议保持与上表相同的 `需求方案.md` / `.html` / `.pdf` / `assets/` 结构，便于日后迁入项目 `docs/solutions/`。

## 与六色制图的关系

- **drawio 源文件**：优先放在**项目**的 `docs/diagrams/`（与业务代码同级管理），技能内不强制复制一份。
- 需求方案 MD 中通过**相对路径**引用图片，例如：`../diagrams/delivery-six-color.png`。

## AI 执行时的默认行为（建议写入对话指令）

1. 先问或推断**项目根路径**，在 `docs/solutions/<slug>/` 下创建目录。
2. **主交付**写 `需求方案.md`；用户明确要求时再生成 HTML/PDF（并放入同目录 `assets/` 如有静态资源）。
3. 不要将大体积 PDF 提交到仅用于技能分发的 **Skills/BizSolution** 仓库（除非用户明确把该仓库当作文档库）。
