---
name: requirement_completion_skill
description: 将空调室内机功能需求输入转成可补全、可改写、可评审、可提取的结构化需求结果
user-invocable: true
version: 1.0.0
author: yangjunjie
---

# requirement_completion_skill

## 作用
用于把空调室内机功能需求相关的自然语言输入，转成可评审、可补全、可改写、可提取的结构化需求结果。

## 何时使用
- 用户要补全功能需求
- 用户要把一句话改写成标准需求
- 用户要评审已有需求文本
- 用户要从需求中提取结构化字段
- 用户要解释某个功能模块在需求补全时应关注什么

## 不适用场景
- 纯技术实现方案设计
- 电控算法推导
- 硬件选型
- 成本评估
- 详细测试用例生成

## 输入
读取 `schemas/input_schema.json`。

最小输入：
- `task_type`
- `user_input`

运行时可选读取：
- `core/common_requirement_framework.json`
- `core/task_templates.json`
- `modules/module_registry.json`
- `rules/matching_rules.json`
- `rules/multi_module_resolution_rules.json`
- `runtime/runtime_workflow.json`
- `modules/plugins/*.json`
- `examples/few_shot_examples.json`

## 输出
读取 `schemas/output_schema.json`。

所有任务输出都必须至少包含：
- `task_type`
- `matched_modules`

其余字段严格按 `core/task_templates.json` 和 `schemas/output_schema.json` 输出：
- `completion`：`intent_type`、`core_intent`、`explicit_requirements`、`inferred_requirements`、`missing_dimensions`、`default_inference`、`must_confirm`、`risks`、`follow_up_questions`、`rewritten_requirement`、`assumptions`
- `rewrite`：`intent_type`、`core_intent`、`must_confirm`、`rewritten_requirement`、`assumptions`
- `review`：`intent_type`、`core_intent`、`review_issues`、`missing_dimensions`、`risks`、`follow_up_questions`、`rewritten_requirement`
- `extraction`：`intent_type`、`structured_extraction`、`assumptions`
- `explanation`：`core_intent`、`default_inference`、`must_confirm`

## 执行顺序
1. 按 `task_type` 和输入语义确认任务类型。
2. 读取 `modules/module_registry.json` 和 `rules/matching_rules.json` 识别主模块与关联模块。
3. 读取命中模块对应的 `modules/plugins/*.json`。
4. 使用 `core/common_requirement_framework.json` 检查通用维度缺失项。
5. 叠加插件中的 `default_rules`、`must_confirm_rules`、`common_missing_items`、`inference_rules`。
6. 多模块时按 `rules/multi_module_resolution_rules.json` 合并冲突、优先级和恢复逻辑。
7. 按 `core/task_templates.json` 和 `schemas/output_schema.json` 组织输出。
8. 输出前自检：
   - 不把默认经验当成用户显式需求
   - 明确区分 `default_inference` 和 `must_confirm`
   - 多模块时显式写出联动关系和冲突点

## 关键约束
- 不要只解释原理，必须回到需求逻辑。
- 不要省略优先级、恢复逻辑、异常处理。
- 信息不足时，不给唯一确定结论，明确写出假设与待确认项。
- 多模块命中时，必须区分主模块和关联模块。

## 文件约定
- 通用规则：`core/common_requirement_framework.json`
- 任务输出裁剪：`core/task_templates.json`
- 系统提示词：`prompts/system_prompt.txt`
- 输入输出约束：`schemas/input_schema.json`、`schemas/output_schema.json`
- 模块注册：`modules/module_registry.json`
- 模块插件：`modules/plugins/<module_code>.json`
- 模块匹配：`rules/matching_rules.json`
- 多模块编排：`rules/multi_module_resolution_rules.json`
- 命名约束：`rules/naming_conventions.json`
- 运行流程：`runtime/runtime_workflow.json`
- 标准样例：`examples/few_shot_examples.json`
- 验证集：`examples/validation_set.json`
