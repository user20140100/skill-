---
name: requirement-test-generator
description: |
  Generate comprehensive test cases from requirement documents for any domain.
  Supports built-in assets (AC controller, etc.) and custom domain definitions.
  Use this skill when the user wants to create test cases from requirement documents,
  including mode switching, state transitions, protection logic, timing functions,
  and boundary conditions. Triggers on phrases like "需求测试用例", "生成测试用例",
  "requirement test cases", "从需求生成测试", or when provided with requirement
  documents for any controller or system.
compatibility:
  - Python 3.x
  - openpyxl
metadata:
  audience: qa-engineer
  workflow: requirement-to-testcase
  output-format: xlsx
  domain: test-design
user-invocable: true
version: 1.0.0
author: yangjunjie
---

# 需求驱动测试用例生成器

从需求文档生成结构化、高覆盖率的测试用例，输出 Excel 格式。支持多领域域知识加载。

## 域知识加载

在开始分析前，先确定目标领域：

1. **检查 `assets/` 目录**: 是否存在匹配的域知识文件
2. **自动识别**: 根据需求文档中的关键词匹配已有域（如检测到"空调"、"制冷"、"压缩机"等关键词 → 加载 `assets/ac-controller.md`）
3. **无匹配域**: 使用纯通用方法论，仅依赖 `references/test-methodology.md`
4. **用户指定域**: 用户可通过"使用XX领域知识"明确指定

域知识文件提供：
- 功能模块清单与子功能
- 状态转换规则与时间约束
- 领域特有的保护/约束逻辑
- 领域特有的测试数据模板
- 领域特有的常见测试场景

> 域知识文件位于 `assets/` 目录，格式参见 `assets/_template.md`

## Workflow

### Step 1: 分析需求

从需求文档中提取：

1. **功能范围**: 包含哪些功能模块和子功能？
2. **输入源**: 用户操作入口有哪些？（按钮、界面、API、传感器等）
3. **输出/反馈**: 系统如何呈现结果？（显示、响应、状态变更等）
4. **约束与阈值**: 数值限制、时间限制、权限约束、业务规则
5. **状态机**: 状态转换规则、优先级规则
6. **异常处理**: 故障模式、降级策略、恢复机制

> 如已加载域知识，参照域文件中的「Step 1 补充提取项」和「功能模块」章节补充领域特有的提取项
> 通用测试方法论见 `references/test-methodology.md`

### Step 2: 生成测试场景

对每个功能模块，按 6 个维度生成测试用例：

| Type | Description |
|------|-------------|
| **正向功能** | Normal operation, valid inputs |
| **逆向功能** | Invalid inputs, boundary violations |
| **边界条件** | Min/max values, threshold crossing |
| **异常处理** | Sensor/hardware failure, communication error |
| **状态转换** | State switching, priority conflicts |
| **组合场景** | Multiple functions active simultaneously |

**Priority levels**: P0 (阻塞) → P1 (严重) → P2 (一般) → P3 (建议)

> 详细方法论和用例模板见 `references/test-methodology.md`
> 如已加载域知识，参照域文件中的「常见测试场景」和「测试数据模板」章节

### Step 3: 命名规范

```
[模块]_[功能]_[场景]_[预期结果]
```

**示例:**
- `用户登录_密码校验_输入空密码_提示必填`
- `订单提交_库存检查_库存为0_阻止下单`
- `数据导入_格式校验_CSV格式错误_报错并跳过`

> 如已加载域知识，参照域文件中的「命名示例」章节获取领域专用示例

### Step 4: 输出 Excel

生成 Excel 文件，包含以下列：

| Column | Description |
|--------|-------------|
| 用例ID | TC-XXX format |
| 功能模块 | 所属功能模块 |
| 用例标题 | Test case title |
| 优先级 | P0/P1/P2/P3 |
| 前置条件 | Prerequisites |
| 测试步骤 | Step-by-step instructions |
| 输入条件 | Input signals, parameters |
| 预期输出 | Expected behavior, state changes |
| 测试类型 | 正向/逆向/边界/异常/状态转换/组合 |
| 关联需求 | Link to requirement document |
| 备注 | Additional notes |

**输出格式:**
```
test_cases_<timestamp>.xlsx
├── Sheet: 测试用例
├── Sheet: 功能覆盖
└── Sheet: 统计汇总
```

## Bundled Scripts

### generate_excel.py

生成格式化的 Excel 文件。

**Usage:**
```bash
python scripts/generate_excel.py <json_file> [output_file]
```

**JSON Schema:**
```json
{
  "test_cases": [
    {
      "id": "TC-001",
      "module": "用户认证",
      "title": "用户登录_密码校验_正确密码_登录成功",
      "priority": "P0",
      "precondition": "用户已注册",
      "steps": "1.打开登录页面\n2.输入正确的用户名和密码\n3.点击登录",
      "input": "用户名：testuser，密码：correct_password",
      "expected": "登录成功，跳转到主页",
      "type": "正向",
      "requirement": "REQ-用户登录",
      "note": ""
    }
  ],
  "coverage": [
    ["需求点", "用例编号", "覆盖情况"],
    ["正确密码登录", "TC-001", "已覆盖"]
  ]
}
```

**Dependencies:**
```bash
pip install openpyxl
```

## Reference Files

| File | Content |
|------|---------|
| `references/test-methodology.md` | 通用测试覆盖维度、优先级定义、命名规范、用例模板、测试数据设计方法 |
| `assets/*.md` | 领域特定功能模块、状态转换规则、测试数据模板、常见场景 |
| `assets/_template.md` | 新增域知识的模板文件 |

## Best Practices

1. **覆盖状态转换**: 状态切换必须包含进入条件、退出条件、时序约束
2. **测试优先级冲突**: 多条规则同时触发时的优先级处理
3. **验证输出一致性**: 显示/反馈必须与内部状态一致
4. **测试故障模式**: 所有输入源都应有故障场景用例
5. **考虑用户行为**: 快速重复操作、同时多入口操作
6. **持久化验证**: 掉电/重启场景下状态的保持与恢复
