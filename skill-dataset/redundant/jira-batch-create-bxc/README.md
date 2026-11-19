# jira-batch-create

从 Excel 批量创建/修改 Jira Issue，用于自动化测试 NG 问题登记和已有 Issue 批量修复。

## 功能

1. **批量创建** - 从 Excel 测试结果提取 NG 问题，批量创建 Jira Issue
2. **批量修改** - 对已创建的 Jira Issue 批量修改字段（标题、经办人、备注、标签等）

## 触发词

- "批量创建 Jira Issue"
- "Excel 导入 Jira"
- "NG 问题批量登记"
- "批量修改 Jira Issue"

## 前置条件

- mcp-atlassian MCP server 已配置（需要 `JIRA_PERSONAL_TOKEN`）
- 包含测试结果的 `.xlsx` 文件

## 安装依赖

```bash
pip3 install mcp-atlassian --break-system-packages
pip3 install openpyxl pandas
```

## 工作流程概要

### 批量创建

1. 收集基础信息（项目 key、平台、客户、经办人等）
2. 读取 Excel 并智能识别列映射
3. 筛选 NG 问题、预览创建计划
4. 获取 Jira 必填字段
5. 用户确认后串行创建 Issue
6. 输出汇总报告

### 批量修改

1. 确定修改范围（JQL / Issue Key 列表 / 标签筛选）
2. 收集修改内容（标题、经办人、标签、备注等）
3. 预览修改内容
4. 用户确认后串行修改
5. 输出修改报告

## 注意事项

- 所有创建/修改操作必须用户确认后才执行
- Jira Server 不支持 emoji（4 字节 UTF-8），AI 标识使用纯文本
- 自定义字段 ID 通过 `search_fields` 动态查找，不硬编码
- 串行处理避免 API 限流
