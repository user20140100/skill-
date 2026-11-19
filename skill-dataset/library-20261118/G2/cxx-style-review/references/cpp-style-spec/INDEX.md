# C/C++ Coding Standard (Split Edition)

This directory contains a split edition of the coding standard for on-demand loading during reviews.

## Runtime Loading Policy

- Review workflows should load the split documents (for example, `style-naming.md`) as needed.
- The archived source-of-truth file `./source-of-truth/C&Cpp编程规范-初稿v0.3.md` is for maintenance and iteration only and must not be used as runtime input.

## Documents

- `overview.md`: Preamble + Chapter "概述" (scope/principles/classification).
- `style-naming.md`: Chapter "一. 风格规约" section "1-1 命名".
- `style-formatting.md`: Chapter "一. 风格规约" section "1-2 格式".
- `style-comments.md`: Chapter "一. 风格规约" section "1-3 注释".
- `practice-files.md`: Chapter "二. 实践规约" section "2-1 文件".
- `practice-macros.md`: Chapter "二. 实践规约" section "2-2 预处理与宏运用".
- `practice-control-flow.md`: Chapter "二. 实践规约" sections "2-3 条件控制语句" + "2-4 循环".
- `practice-functions-and-general.md`: Chapter "二. 实践规约" section "2-5 函数" + "2-5 综合".
- `practice-cpp-specific.md`: Chapter "二. 实践规约" section "2-6 其他C++规则".
- `safety-types-and-data.md`: Chapter "三. 安全规约" section "3-1 变量类型与数据安全".
- `safety-resources.md`: Chapter "三. 安全规约" section "3-2 资源使用".
- `safety-threading-and-build.md`: Chapter "三. 安全规约" sections "3-3 进程与线程" + "3-3 其他".

## Coverage

- See `coverage-map.md` for a heading-level mapping from the source document to each split file.
