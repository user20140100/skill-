---
name: project-prd-clear
description: 清除当前项目的 project-prd 工作区、project-prd-edit/project-prd-verify/project-prd-clear/project-prd-serve 四个项目级 skill、AGENTS.md 受管规则和受管 GitHub 门禁，使 project-prd 可以重新初始化。仅在用户明确要求清除、重置或重新生成项目 PRD 环境时使用；这是破坏性操作，执行前必须再次确认。
---

# Project PRD Clear

安全清理 project-prd 管理的精确路径，不触碰项目源码或非受管配置。

## 强制确认

1. 先说明将删除：`.project-prd/`、四个项目级 skill、AGENTS.md 中的 project-prd 受管块，以及受管 GitHub workflow。
2. 明确说明 `.project-prd` 中的全部 PRD 和审计历史会被永久删除；Git 已提交的内容仍可从 Git 历史恢复，未提交内容可能无法恢复。
3. 要求用户确认本次清理。没有当次明确确认时停止，不运行脚本。
4. 脚本在任何删除前必须验证 workspace owner、manifest/initializing 状态、所有受管路径、AGENTS.md 标记和 workflow 标记。任一预检失败时保持零修改。

## 执行

确认后运行：

```bash
python3 <本 skill 目录>/scripts/clear_project_prd.py \
  --project-root <项目根目录> \
  --confirm PROJECT-PRD-CLEAR
```

脚本只允许删除以下受管目标：

- `.project-prd/`
- `.agents/skills/project-prd-edit/`
- `.agents/skills/project-prd-verify/`
- `.agents/skills/project-prd-clear/`
- `.agents/skills/project-prd-serve/`
- `.github/workflows/project-prd-guard.yml`（仅当包含受管标记）
- `AGENTS.md` 中两个 project-prd 标记之间的内容

脚本结束后报告实际删除项和保留项。随后可再次调用全局 `project-prd` 重新初始化。

## 禁止事项

- 不接受通配符、环境变量展开或自定义删除路径。
- 不使用 `rm -rf` 或 Git reset/checkout。
- 不清理全局 `project-prd` skill。
- 发现 owner/状态文件无效、标记缺失或重复、受管路径为符号链接、路径过宽或工作区归属不明时停止，交由用户处理。
