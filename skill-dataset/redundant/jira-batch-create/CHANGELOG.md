# Changelog

## [1.0.1] - 2026-04-27

### Added
- Step 1 新增「导入隐藏行」可选配置项（默认为"否"，不导入隐藏行）
- Step 2 新增 openpyxl 隐藏行检测逻辑，通过 `ws.row_dimensions[row_idx].hidden` 过滤隐藏行

### Changed
- Excel 读取方式从 pandas 改为 openpyxl，以支持隐藏行属性检测

## [1.0.0] - 2026-04-20

### Added
- 批量创建功能：从 Excel 提取 NG 问题，批量创建 Jira Issue
- 批量修改功能：支持标题、经办人、标签、备注、自定义字段等批量修改
- 智能列名识别：自动匹配 Excel 列到字段映射
- 合并单元格处理：前向填充处理合并单元格
- AI 标识：使用 Jira wiki `{quote}` 格式（避免 emoji 导致数据库写入失败）
- 预览确认机制：所有操作必须用户确认后才执行
- 自定义字段动态查找：通过 `search_fields` 获取字段 ID，不硬编码
- 串行创建/修改：避免 API 限流
- 完整的错误处理和汇总报告
