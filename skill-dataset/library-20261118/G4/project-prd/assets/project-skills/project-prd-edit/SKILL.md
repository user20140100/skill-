---
name: project-prd-edit
description: 项目 .project-prd 逐功能 PRD 与普通资源文件的唯一修改入口。用户明确要求新增、修改、废弃或删除功能需求，或同步 PRD 相关图片、数据、附件等资源时使用；不得为迁就错误实现而修改 PRD。通过受控脚本校验 PRD、原子写入任意二进制资源、重建索引、更新哈希清单并留下审计记录。
---

# Project PRD Edit

仅在用户明确要求改变功能定义或其受管资源时编辑。代码实现与 PRD 不一致不自动构成修改 PRD 的理由。

## 工作流

1. 定位包含 `.project-prd/manifest.json` 的项目根目录。
2. 运行完整性门禁：

   ```bash
   python3 .project-prd/tools/project_prd_guard.py integrity --project-root <项目根目录>
   ```

   失败时停止；不得把未知直接修改纳入新基线。若本次目标本身是已存在但尚未登记的普通资源，仍通过编辑脚本显式 `update`；脚本只为该目标开放受控接管，并以 `create` 语义加入审计链。
3. 确定目标类型和 `create`、`update` 或 `delete`；删除必须再次确认：
   - PRD：`<功能分类>/<细分功能>.md`。
   - 资源：`.project-prd` 内除两级 PRD Markdown 和 project-prd 控制面之外的任意普通文件；支持任意相对目录、扩展名和二进制内容。
4. 修改 PRD 时，阅读 `INDEX.md`、目标及关联 PRD、对应代码和测试，并完整阅读 `<项目根目录>/.project-prd/tools/project-prd-writer/SKILL.md` 及其模板契约。重建受影响的行为清单和 Feature Point 拆解，同步分类契约、复杂度、流程图、矩阵和追溯证据。
5. 修改资源时，阅读引用该资源的 PRD，并在 `.project-prd` 外准备源文件；不得直接覆盖目标。资源内容由其实际消费者负责格式与安全校验，project-prd 只保证原始字节、事务、哈希和审计完整性。
6. 在 `.project-prd` 外准备完整草稿，调用：

   ```bash
   python3 <本 skill 目录>/scripts/apply_prd_change.py \
     --project-root <项目根目录> \
     --operation update \
     --target '<功能分类>/<细分功能>.md' \
     --source <外部草稿.md> \
     --reason '<用户明确要求的变更原因>'
   ```

   新增使用 `create`；删除使用 `delete --confirm-delete DELETE-PRD` 且不传 `--source`。
   资源使用同一命令，将 `--target` 改为所需的 `.project-prd` 相对路径，将 `--source` 指向外部源文件。
   同一分类的契约变更、跨分类移动或其他多文件联动必须使用一次原子批量事务：

   ```bash
   python3 <本 skill 目录>/scripts/apply_prd_change.py \
     --project-root <项目根目录> \
     --changes <.project-prd 外的变更清单.json> \
     --reason '<用户明确要求的同一组变更原因>'
   ```

   变更清单是 JSON 数组，每项包含 `operation`、`target`，create/update 另含 `source`，delete 另含 `confirm_delete: "DELETE-PRD"`。脚本只校验最终工作区，失败会整体回滚。
7. PRD 与资源需同步变化时，把 Markdown 和全部相关资源放进同一 `--changes` 原子事务。
8. 重新运行完整性门禁，阅读审计记录，报告目标路径、受影响 PRD ID、行为影响和需同步的代码/测试。

## 规则

- 恰好两级的 `<功能分类>/<细分功能>.md` 保留为 PRD 命名空间；其他普通文件统一视为资源，更新必须提交完整文件。
- 资源可位于 `.project-prd` 内任意相对目录并使用任意文件类型；资源必须进入 manifest、审计哈希链和回滚事务，不得申请例外直接修改。
- `manifest.json`、`INDEX.md`、`.project-prd-owner.json`、`.initializing.json`、`.gitignore`、`tools/`、`.history/`、`.analysis/`、`output/` 以及 Python 缓存属于 project-prd 控制面或运行时，不是可编辑资源。
- 保持已有 `prd_id` 稳定；只有功能语义完全移除时才删除。
- 功能描述必须分开“是什么”、“用户痛点”和“业务价值”；无证据的产品意图标为待确认。
- 每个 FP 必须按固定顺序恰好一次包含 `prd-writer` 完整七章节，并覆盖自己的独立分支、失败、取消、恢复和清理。
- complex PRD 必须维护逐 FP 独立节点、连通且展开 decision 分支的 Mermaid 流程图；矩阵代码项必须来自证据范围并与 PRD 项精确一致。
- 异常表必须包含空态、操作失败、网络异常、权限不足、边界超限并逐行引用源码；不得虚构超时、权限、Toast 或弹窗。
- Behavior 必须精确归属 FP；`source_entries` 必须等于 Behavior 源码证据去重后的集合。
- 禁止直接写 `.project-prd` 中的 PRD、资源、manifest、INDEX 或审计记录。
- 不得通过放宽限制、删除异常或把缺陷改写成需求来迁就当前实现。
