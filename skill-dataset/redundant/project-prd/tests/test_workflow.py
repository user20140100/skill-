from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_prd_lib  # noqa: E402


SKILL_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap.py"
EDIT = SKILL_ROOT / "assets" / "project-skills" / "project-prd-edit" / "scripts" / "apply_prd_change.py"
CLEAR = SKILL_ROOT / "assets" / "project-skills" / "project-prd-clear" / "scripts" / "clear_project_prd.py"


def simple_prd_text(extra_value: str = "") -> str:
    return f"""---
prd_schema: feature-points-v3
prd_id: PRD-ORDER-QUERY
product: Demo
baseline_version: current-code
date: 2026-08-06
author: Project PRD Agent
category: 订单系统
category_domain: 订单数据
category_goal: 帮助用户准确查询和管理订单信息
category_contract:
  - actor=订单调用方
  - outcome=准确查询和管理订单信息
  - object=订单数据
category_fit:
  - actor=订单调用方 @ src/orders.py:find_order
  - object=订单数据 @ src/orders.py:find_order
feature: 订单查询
status: active
complexity: simple
complexity_reasons:
  - 单一查询入口且直接返回查询结果
decomposition_candidates:
  - DC-01|trigger|按订单编号查询|src/orders.py:find_order|FP-01
decomposition_basis:
  - FP-01: 按订单编号完成一次独立查询闭环
source_entries:
  - src/orders.py:find_order
---

# Demo 订单查询 产品需求文档

> 版本：current-code | 日期：2026-08-06 | 作者：Project PRD Agent

## 一、文档说明

### 1.1 文档目的

本文档记录订单查询的现有代码基线、查询边界和返回结果。

### 1.2 产品定位

订单查询是调用方读取指定订单的基础能力。

### 1.3 现有功能概览

| 模块 | 功能点 | 已有能力 |
|---|---|---|
| 订单查询 | FP-01 按编号查询 | 按订单编号查询已有订单 |

### 1.4 术语表

- **订单编号**：唯一定位订单的输入标识。

## 二、功能模块与功能点

### 模块 A：订单查询

#### FP-01 按编号查询

**1. 功能描述**

- **是什么**：用户在订单查询场景中，通过输入订单编号，获得对应订单。
- **为什么**：
  - **用户痛点**：用户需要定位指定订单。
  - **业务价值**：支持订单信息的定向读取。

**2. 交互逻辑**

1. 调用方提交订单编号 → 系统返回对应订单。

**3. 跳转逻辑**

无页面跳转，操作在查询接口内完成。

**4. 跳转过程逻辑**

不涉及页面跳转；系统在调用边界内查找订单。

**5. 正向限制**

| 项目 | 限制 |
|---|---|
| 订单编号 | 使用已存在的订单编号 |

**6. 反向限制**

| 项目 | 说明 |
|---|---|
| 查询副作用 | 查询不得修改订单 {extra_value} |

**7. 异常/空态/错误提示**

| 场景 | 提示内容 | 展示方式 | 源码证据 |
|---|---|---|---|
| 空态：订单不存在 | 返回空结果 | 接口返回 | `src/orders.py:find_order` |
| 操作失败：查询异常 | 向调用方返回失败 | 接口返回 | `src/orders.py:find_order` |
| 网络异常：不适用 | 不适用：该能力无网络依赖 | 无展示 | `src/orders.py:find_order` |
| 权限不足：不适用 | 不适用：当前入口无权限分支 | 无展示 | `src/orders.py:find_order` |
| 边界超限：编号无效 | 返回空结果 | 接口返回 | `src/orders.py:find_order` |

## 三、功能关联与闭环关系

### 3.1 业务流程图

简单单步查询，无需流程图。

**关键闭环链路：**

1. 订单查询：FP-01 接收订单编号 → 查找订单 → 返回结果。

- 相关 PRD：无。

### 3.2 规则矩阵覆盖审计

| Matrix ID | 功能点 | 规则类型 | 源码证据 | 代码项 | PRD 覆盖项 |
|---|---|---|---|---|---|
| MX-NONE | FP-01 | none | `src/orders.py:find_order` | 无可枚举矩阵 | 无可枚举矩阵 |

## 四、行为覆盖与代码追溯

| Behavior ID | 功能点 | 源码证据 | 用户可感知行为 | PRD 章节 |
|---|---|---|---|---|
| B001 | FP-01 | `src/orders.py:find_order` | 按编号返回订单 | 交互逻辑 |

## 五、验证依据

- B001 → `tests/test_orders.py`

## 六、已知缺口与待确认项

无已知未实现项。
"""


def complex_prd_text() -> str:
    point_blocks: list[str] = []
    exception_rows = {
        1: "| 空态：不适用 | 不适用：入口始终可执行 | 无展示 | `src/flow.py:step1` |\n| 操作失败：不适用 | 不适用：入口没有失败分支 | 无展示 | `src/flow.py:step2` |",
        2: "| 网络异常：不适用 | 不适用：当前阶段无网络依赖 | 无展示 | `src/flow.py:step3` |",
        3: "| 权限不足：不适用 | 不适用：当前阶段无权限判断 | 无展示 | `src/flow.py:step5` |",
        4: "| 边界超限：不适用 | 不适用：终态函数没有重复分支 | 无展示 | `src/flow.py:step7` |",
    }
    for index in range(1, 5):
        point_blocks.append(f"""#### FP-{index:02d} 流程阶段{index}

**1. 功能描述**

- **是什么**：用户执行阶段{index}动作，系统完成阶段{index}处理并进入明确状态。
- **为什么**：
  - **用户痛点**：用户需要了解阶段{index}的处理结果和可执行边界。
  - **业务价值**：保证多阶段流程的阶段{index}结果可预期且可恢复。

**2. 交互逻辑**

1. 用户提交阶段{index}请求 → 系统执行步骤{index * 2 - 1}并反馈处理中状态。
2. 用户继续或取消阶段{index} → 系统执行步骤{index * 2}并返回完成或清理结果。

**3. 跳转逻辑**

| 触发操作 | 目标页面/流程 | 说明 |
|---|---|---|
| 完成阶段{index} | 阶段{index + 1 if index < 4 else '结果'} | 展示阶段结果并进入后续流程 |

**4. 跳转过程逻辑**

阶段{index}入口 → 校验当前状态 → 执行阶段{index} → 返回阶段结果。

**5. 正向限制**

| 项目 | 限制 |
|---|---|
| 阶段{index}前置状态 | 仅上一阶段完成后允许进入 |

**6. 反向限制**

| 项目 | 说明 |
|---|---|
| 阶段{index}重复执行 | 执行中拒绝重复发起并保持当前状态 |

**7. 异常/空态/错误提示**

| 场景 | 提示内容 | 展示方式 | 源码证据 |
|---|---|---|---|
{exception_rows[index]}
""")
    coverage = "\n".join(
        f"| B{index:03d} | FP-{((index - 1) // 2) + 1:02d} | `src/flow.py:step{index}` | 用户可感知流程结果{index} | {'交互逻辑' if index % 2 else '反向限制'} |"
        for index in range(1, 9)
    )
    return f"""---
prd_schema: feature-points-v3
prd_id: PRD-FLOW-DEMO
product: Demo
baseline_version: current-code
date: 2026-08-06
author: Project PRD Agent
category: 流程管理
category_domain: 多阶段业务流程
category_goal: 帮助用户完成可控且可恢复的多阶段操作
category_contract:
  - actor=流程操作用户
  - outcome=完成可控且可恢复的多阶段操作
  - object=多阶段业务流程
  - lifecycle=发起到清理的状态转换
category_fit:
  - actor=流程操作用户 @ src/flow.py:step1
  - object=多阶段业务流程 @ src/flow.py:step1
  - lifecycle=发起到清理的状态转换 @ src/flow.py:step2
feature: 复杂流程
status: active
complexity: complex
complexity_reasons:
  - 包含五阶段状态转换
  - 包含异步取消和失败清理
decomposition_candidates:
  - DC-01|trigger|独立流程发起|src/flow.py:step1<br>src/flow.py:step2|FP-01
  - DC-02|stage|中间状态转换|src/flow.py:step3|FP-02
  - DC-03|external_wait|外部协作等待|src/flow.py:step5<br>src/flow.py:step6|FP-03
  - DC-04|terminal|完成与清理终态|src/flow.py:step7|FP-04
decomposition_basis:
  - FP-01: 独立的流程发起与入口校验
  - FP-02: 独立的中间阶段状态转换
  - FP-03: 独立的外部协作与权限检查
  - FP-04: 独立的完成、取消与清理闭环
source_entries:
  - src/flow.py:step1
  - src/flow.py:step2
  - src/flow.py:step3
  - src/flow.py:step4
  - src/flow.py:step5
  - src/flow.py:step6
  - src/flow.py:step7
  - src/flow.py:step8
---

# Demo 复杂流程 产品需求文档

> 版本：current-code | 日期：2026-08-06 | 作者：Project PRD Agent

## 一、文档说明

### 1.1 文档目的

本文档完整描述复杂流程的四个独立功能点、八个执行步骤和失败恢复边界。

### 1.2 产品定位

该流程为用户提供多阶段、可取消且可恢复的业务处理能力。

### 1.3 现有功能概览

| 模块 | 功能点 | 已有能力 |
|---|---|---|
| 流程 | FP-01 流程阶段1 | 发起与入口校验 |
| 流程 | FP-02 流程阶段2 | 中间状态转换 |
| 流程 | FP-03 流程阶段3 | 外部协作与权限检查 |
| 流程 | FP-04 流程阶段4 | 完成、取消与清理 |

### 1.4 术语表

- **流程阶段**：具有独立入口、结果和边界的处理单元。
- **状态转换**：流程从一个可观察状态进入下一个状态。
- **清理闭环**：取消或完成后释放资源并复位状态的过程。

## 二、功能模块与功能点

### 模块 A：复杂流程

{chr(10).join(point_blocks)}

## 三、功能关联与闭环关系

### 3.1 业务流程图

```mermaid
flowchart TD
  A["FP-01 流程发起"] --> B["FP-02 状态转换"]
  B --> C["FP-03 外部协作"]
  C --> D["FP-04 完成与清理"]
  C -->|取消| B
```

**关键闭环链路：**

1. 处理闭环：FP-01 发起 → FP-02 状态转换 → FP-03 外部协作 → FP-04 完成与清理。

- 相关 PRD：无。

### 3.2 规则矩阵覆盖审计

| Matrix ID | 功能点 | 规则类型 | 源码证据 | 代码项 | PRD 覆盖项 |
|---|---|---|---|---|---|
| MX-01 | FP-02 | state | `src/flow.py:step3` | 待处理<br>处理中<br>完成 | 待处理<br>处理中<br>完成 |

## 四、行为覆盖与代码追溯

| Behavior ID | 功能点 | 源码证据 | 用户可感知行为 | PRD 章节 |
|---|---|---|---|---|
{coverage}

## 五、验证依据

- B001 → `tests/test_flow.py`
- B002 → `tests/test_flow.py`
- B003 → `tests/test_flow.py`
- B004 → `tests/test_flow.py`
- B005 → `tests/test_flow.py`
- B006 → `tests/test_flow.py`
- B007 → `tests/test_flow.py`
- B008 → `tests/test_flow.py`

## 六、已知缺口与待确认项

无已知未实现项。
"""


def two_point_complex_prd_text() -> str:
    content = complex_prd_text()
    content = re.sub(
        r"(?ms)^#### FP-03 .*?(?=^#### FP-04 )",
        "",
        content,
    )
    content = re.sub(
        r"(?ms)^#### FP-04 .*?(?=^## 三、功能关联与闭环关系)",
        "",
        content,
    )
    for line in (
        "  - DC-03|external_wait|外部协作等待|src/flow.py:step5<br>src/flow.py:step6|FP-03\n",
        "  - DC-04|terminal|完成与清理终态|src/flow.py:step7|FP-04\n",
        "  - FP-03: 独立的外部协作与权限检查\n",
        "  - FP-04: 独立的完成、取消与清理闭环\n",
        "  - src/flow.py:step5\n",
        "  - src/flow.py:step6\n",
        "  - src/flow.py:step7\n",
        "  - src/flow.py:step8\n",
        "| 流程 | FP-03 流程阶段3 | 外部协作与权限检查 |\n",
        "| 流程 | FP-04 流程阶段4 | 完成、取消与清理 |\n",
    ):
        content = content.replace(line, "")
    content = re.sub(r"(?m)^\| B00[5-8] .*\n", "", content)
    content = re.sub(r"(?m)^- B00[5-8] .*\n", "", content)
    content = content.replace(
        "2. 用户继续或取消阶段1 → 系统执行步骤2并返回完成或清理结果。",
        "2. 用户继续或取消阶段1 → 系统执行步骤2并返回完成或清理结果。\n"
        "3. 系统收到阶段1恢复事件 → 系统恢复入口状态并允许重新发起。",
    )
    content = content.replace(
        "| 阶段1前置状态 | 仅上一阶段完成后允许进入 |",
        "| 阶段1前置状态 | 仅上一阶段完成后允许进入 |\n"
        "| 阶段1恢复入口 | 仅清理完成后允许重新发起 |",
    )
    content = content.replace(
        "| 阶段2重复执行 | 执行中拒绝重复发起并保持当前状态 |",
        "| 阶段2重复执行 | 执行中拒绝重复发起并保持当前状态 |\n"
        "| 阶段2越级进入 | 拒绝执行并保持上一阶段状态 |",
    )
    content = content.replace(
        "| 网络异常：不适用 | 不适用：当前阶段无网络依赖 | 无展示 | `src/flow.py:step3` |",
        "| 网络异常：不适用 | 不适用：当前阶段无网络依赖 | 无展示 | `src/flow.py:step3` |\n"
        "| 权限不足：不适用 | 不适用：当前阶段无权限判断 | 无展示 | `src/flow.py:step3` |\n"
        "| 边界超限：重复发起 | 流程正在执行 | 内联提示 | `src/flow.py:step4` |",
    )
    content = content.replace(
        "| B004 | FP-02 | `src/flow.py:step4` | 用户可感知流程结果4 | 反向限制 |",
        "| B004 | FP-02 | `src/flow.py:step4` | 用户可感知流程结果4 | 反向限制 |\n"
        "| B005 | FP-01 | `src/flow.py:step1` | 阶段一恢复后允许重新发起 | 交互逻辑 |\n"
        "| B006 | FP-02 | `src/flow.py:step4` | 越级进入时保持上一阶段状态 | 反向限制 |",
    )
    content = content.replace(
        "- B004 → `tests/test_flow.py`",
        "- B004 → `tests/test_flow.py`\n"
        "- B005 → `tests/test_flow.py`\n"
        "- B006 → `tests/test_flow.py`",
    )
    content = content.replace(
        "1. 处理闭环：FP-01 发起 → FP-02 状态转换 → FP-03 外部协作 → FP-04 完成与清理。",
        "1. 处理闭环：FP-01 发起与恢复 → FP-02 状态转换与最终清理。",
    )
    content = content.replace(
        '  A["FP-01 流程发起"] --> B["FP-02 状态转换"]\n'
        '  B --> C["FP-03 外部协作"]\n'
        '  C --> D["FP-04 完成与清理"]\n'
        "  C -->|取消| B",
        '  A["FP-01 流程发起与恢复"] --> B["FP-02 状态转换与清理"]\n'
        "  B -->|取消| A",
    )
    return content


def shutdown_prd_text() -> str:
    points = (
        ("电源键长按入口", "src/shutdown.py:power_key", "src/shutdown.py:power_process"),
        ("UDI 请求与来源策略", "src/shutdown.py:udi_request", "src/shutdown.py:udi_request"),
        ("拦截器优先级判断", "src/shutdown.py:interceptor_chain", "src/shutdown.py:interceptor_chain"),
        ("确认弹窗与倒计时", "src/shutdown.py:confirm_dialog", "src/shutdown.py:confirm_dialog"),
        ("PC 协同关机等待", "src/shutdown.py:pc_request", "src/shutdown.py:pc_callback"),
        ("最终关机策略", "src/shutdown.py:final_strategy", "src/shutdown.py:final_strategy"),
        ("PC 状态反向触发", "src/shutdown.py:pc_listener", "src/shutdown.py:reverse_trigger"),
    )
    exception_rows = (
        "空态：无可用关机入口 | 保持当前运行状态 | 无展示",
        "操作失败：UDI 请求被拒绝 | 返回拒绝结果 | 系统事件",
        "网络异常：不适用 | 不适用：拦截链无网络依赖 | 无展示",
        "权限不足：不适用 | 不适用：确认交互无权限判断 | 无展示",
        "边界超限：重复确认 | 保持首次确认结果 | 内联状态",
        "操作失败：策略执行失败 | 保持关机流程终态 | 系统事件",
        "边界超限：重复 PC 状态 | 忽略重复状态 | 无展示",
    )
    point_blocks: list[str] = []
    overview_rows: list[str] = []
    behavior_rows: list[str] = []
    verification_rows: list[str] = []
    for index, (title, main_source, boundary_source) in enumerate(points, start=1):
        feature_point_id = f"FP-{index:02d}"
        overview_rows.append(
            f"| 关机流程 | {feature_point_id} {title} | 已实现{title}的主路径和边界处理 |"
        )
        scenario, prompt, display = [item.strip() for item in exception_rows[index - 1].split("|")]
        point_blocks.append(f"""#### {feature_point_id} {title}

**1. 功能描述**

- **是什么**：用户或系统在关机流程中通过{title}进入下一项明确处理阶段。
- **为什么**：
  - **用户痛点**：关机过程需要让{title}的结果和边界可预期。
  - **业务价值**：保证整机关机在多入口和外部协作下形成可验证闭环。

**2. 交互逻辑**

1. 角色触发{title} → 系统执行该阶段主路径并返回阶段结果。
2. 角色重复、取消或失败触发{title} → 系统保持既定状态并执行边界处理。

**3. 跳转逻辑**

无页面跳转；流程进入下一关机阶段或保持当前状态。

**4. 跳转过程逻辑**

不涉及页面跳转；关机入口 → {title} → 下一阶段或稳定终态。

**5. 正向限制**

| 项目 | 限制 |
|---|---|
| {title}准入 | 仅在前置阶段满足时执行当前阶段 |

**6. 反向限制**

| 项目 | 说明 |
|---|---|
| {title}重复或越级执行 | 拒绝重复推进并保持当前稳定状态 |

**7. 异常/空态/错误提示**

| 场景 | 提示内容 | 展示方式 | 源码证据 |
|---|---|---|---|
| {scenario} | {prompt} | {display} | `{boundary_source}` |
""")
        main_id = f"B{index * 2 - 1:03d}"
        boundary_id = f"B{index * 2:03d}"
        behavior_rows.extend((
            f"| {main_id} | {feature_point_id} | `{main_source}` | 完成{title}主路径 | 交互逻辑 |",
            f"| {boundary_id} | {feature_point_id} | `{boundary_source}` | 处理{title}边界结果 | 反向限制 |",
        ))
        verification_rows.extend((
            f"- {main_id} → `tests/test_shutdown.py`",
            f"- {boundary_id} → `tests/test_shutdown.py`",
        ))

    source_entries = (
        "src/shutdown.py:power_key",
        "src/shutdown.py:power_process",
        "src/shutdown.py:udi_request",
        "src/shutdown.py:interceptor_chain",
        "src/shutdown.py:confirm_dialog",
        "src/shutdown.py:pc_request",
        "src/shutdown.py:pc_callback",
        "src/shutdown.py:final_strategy",
        "src/shutdown.py:pc_listener",
        "src/shutdown.py:reverse_trigger",
    )
    return f"""---
prd_schema: feature-points-v3
prd_id: PRD-POWER-SHUTDOWN
product: Demo
baseline_version: current-code
date: 2026-08-06
author: Project PRD Agent
category: 电源与关机
category_domain: 整机关机状态
category_goal: 帮助设备使用者安全完成整机关机
category_contract:
  - actor=设备使用者与系统事件
  - outcome=安全完成整机关机
  - object=整机关机状态
  - lifecycle=关机发起到设备终止
category_fit:
  - actor=设备使用者与系统事件 @ src/shutdown.py:power_key
  - object=整机关机状态 @ src/shutdown.py:final_strategy
  - lifecycle=关机发起到设备终止 @ src/shutdown.py:pc_listener
feature: 关机流程
status: active
complexity: complex
complexity_reasons:
  - 包含七阶段状态转换和两类独立触发入口
  - 包含来源映射、拦截器优先级、确认交互、PC 异步协作和最终策略
decomposition_candidates:
  - DC-01|trigger|电源键长按入口|src/shutdown.py:power_key<br>src/shutdown.py:power_process|FP-01
  - DC-02|stage|UDI 请求与来源策略|src/shutdown.py:udi_request|FP-02
  - DC-03|decision|拦截器优先级判断|src/shutdown.py:interceptor_chain|FP-03
  - DC-04|interaction|确认弹窗与倒计时|src/shutdown.py:confirm_dialog|FP-04
  - DC-05|external_wait|PC 协同关机等待|src/shutdown.py:pc_request<br>src/shutdown.py:pc_callback|FP-05
  - DC-06|terminal|最终关机策略|src/shutdown.py:final_strategy|FP-06
  - DC-07|trigger|PC 状态反向触发|src/shutdown.py:pc_listener<br>src/shutdown.py:reverse_trigger|FP-07
decomposition_basis:
{chr(10).join(f'  - FP-{index:02d}: {title}具有独立触发、输入输出或可验证产品规则' for index, (title, _, _) in enumerate(points, start=1))}
source_entries:
{chr(10).join(f'  - {item}' for item in source_entries)}
---

# Demo 关机流程 产品需求文档

> 版本：current-code | 日期：2026-08-06 | 作者：Project PRD Agent

## 一、文档说明

### 1.1 文档目的

本文档描述从电源键或 PC 状态进入整机关机的七阶段产品闭环。

### 1.2 产品定位

关机流程协调本机策略、用户确认和 PC 外部协作，最终选择实际关机方式。

### 1.3 现有功能概览

| 模块 | 功能点 | 已有能力 |
|---|---|---|
{chr(10).join(overview_rows)}

### 1.4 术语表

- **UDI**：关机请求及来源策略的统一接口。
- **关机拦截器**：按优先级决定流程是否继续的规则链。
- **PC 协同**：设备等待关联 PC 完成关机确认的外部协作阶段。

## 二、功能模块与功能点

### 模块 A：整机关机

{chr(10).join(point_blocks)}

## 三、功能关联与闭环关系

### 3.1 业务流程图

```mermaid
flowchart TD
  A["FP-01 电源键入口"] --> B["FP-02 UDI 来源策略"]
  B --> C["FP-03 拦截器判断"]
  C -->|允许| D["FP-04 确认交互"]
  C -->|拒绝| STOP["保持运行"]
  D --> E["FP-05 PC 协同等待"]
  E --> F["FP-06 最终关机策略"]
  G["FP-07 PC 状态反向触发"] --> B
```

**关键闭环链路：**

1. 本机关机：FP-01 电源键入口 → FP-02 UDI 来源策略 → FP-03 拦截器 → FP-04 确认 → FP-05 PC 协同 → FP-06 最终关机。
2. PC 反向触发：FP-07 PC 状态事件 → FP-02 UDI 来源策略 → FP-06 最终关机。

- 相关 PRD：无。

### 3.2 规则矩阵覆盖审计

| Matrix ID | 功能点 | 规则类型 | 源码证据 | 代码项 | PRD 覆盖项 |
|---|---|---|---|---|---|
| MX-01 | FP-02 | mapping | `src/shutdown.py:udi_request` | 本地电源键<br>PC 反向事件 | 本地电源键<br>PC 反向事件 |
| MX-02 | FP-03 | priority | `src/shutdown.py:interceptor_chain` | 允许继续<br>拒绝并停止 | 允许继续<br>拒绝并停止 |
| MX-03 | FP-04 | copy | `src/shutdown.py:confirm_dialog` | 取消关机<br>确认关机 | 取消关机<br>确认关机 |
| MX-04 | FP-05 | state | `src/shutdown.py:pc_request` | 请求协同<br>等待确认<br>协同完成 | 请求协同<br>等待确认<br>协同完成 |
| MX-05 | FP-06 | policy | `src/shutdown.py:final_strategy` | 标准关机<br>厂商关机 | 标准关机<br>厂商关机 |

## 四、行为覆盖与代码追溯

| Behavior ID | 功能点 | 源码证据 | 用户可感知行为 | PRD 章节 |
|---|---|---|---|---|
{chr(10).join(behavior_rows)}

## 五、验证依据

{chr(10).join(verification_rows)}

## 六、已知缺口与待确认项

无已知未实现项。
"""


class ProjectPrdWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "demo-project"
        self.root.mkdir()
        (self.root / ".git").mkdir()
        (self.root / ".git" / "config").write_text(
            '[remote "origin"]\n  url = https://github.com/example/demo.git\n', encoding="utf-8"
        )
        (self.root / "src").mkdir()
        (self.root / "src" / "orders.py").write_text(
            "def find_order(order_id):\n"
            "    if not order_id:\n        return None\n"
            "    try:\n        return order_id\n"
            "    except Exception:\n        return {'error': 'query_failed'}\n\n"
            "def find_detail(order_id):\n"
            "    if not order_id:\n        return None\n"
            "    try:\n        return order_id\n"
            "    except Exception:\n        return {'error': 'query_failed'}\n\n"
            "def authorize_order(order_id):\n    return True\n",
            encoding="utf-8",
        )
        (self.root / "src" / "flow.py").write_text(
            "\n".join(
                "def step3():\n    states = ('待处理', '处理中', '完成')\n    return states"
                if index == 3 else (
                    "def step4(value=None):\n    if value == 'duplicate': return 'inline_state'\n    return 4"
                    if index == 4 else f"def step{index}(): return {index}"
                )
                for index in range(1, 9)
            ) + "\n",
            encoding="utf-8",
        )
        (self.root / "src" / "shutdown.py").write_text(
            "def power_key(): return 'power_key'\n"
            "def power_process():\n    if not power_key(): return 'empty'\n    return 'ready'\n"
            "def udi_request():\n"
            "    origins = ('本地电源键', 'PC 反向事件')\n"
            "    try:\n        status = 'accepted'\n        return origins, status\n"
            "    except Exception:\n        return 'failed_event'\n"
            "def interceptor_chain():\n"
            "    policies = ('允许继续', '拒绝并停止')\n    return policies\n"
            "def confirm_dialog():\n"
            "    options = ('取消关机', '确认关机')\n    return options\n"
            "def pc_request():\n"
            "    states = ('请求协同', '等待确认', '协同完成')\n    return states\n"
            "def pc_callback():\n    if pc_request() == 'duplicate': return 'inline_state'\n    return 'confirmed'\n"
            "def final_strategy():\n"
            "    strategies = ('标准关机', '厂商关机')\n"
            "    try:\n        return strategies\n    except Exception:\n        return 'failed_event'\n"
            "def pc_listener(): return 'pc_listener'\n"
            "def reverse_trigger():\n    if pc_listener() == 'duplicate': return 'ignored'\n    return 'triggered'\n",
            encoding="utf-8",
        )
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_orders.py").write_text(
            "def test_find_order():\n    assert True\n", encoding="utf-8"
        )
        (self.root / "tests" / "test_flow.py").write_text(
            "def test_flow():\n    assert True\n", encoding="utf-8"
        )
        (self.root / "tests" / "test_shutdown.py").write_text(
            "def test_shutdown():\n    assert True\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_command(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, *args], cwd=self.root, text=True, capture_output=True, check=False
        )
        self.assertEqual(expected, result.returncode, msg=result.stdout + result.stderr)
        return result

    def prepare(self) -> None:
        self.run_command(str(BOOTSTRAP), "prepare", "--project-root", str(self.root))

    def complete_prd_tasks(self, agent_ids: list[str] | None = None) -> None:
        workspace = self.root / ".project-prd"
        task_root = workspace / ".analysis" / "tasks"
        task_root.mkdir(parents=True, exist_ok=True)
        targets = [path.relative_to(workspace).as_posix() for path in project_prd_lib.list_prd_files(workspace)]
        agents = agent_ids or [f"agent-{index}" for index in range(1, len(targets) + 1)]
        self.assertEqual(len(targets), len(agents))
        tasks: list[dict[str, object]] = []
        for index, (target, agent_id) in enumerate(zip(targets, agents, strict=True), start=1):
            task_id = f"prd-{index:03d}"
            target_path = workspace / target
            metadata = project_prd_lib.validate_prd(
                target_path.read_text(encoding="utf-8"), Path(target), self.root
            )
            source_scope = sorted({str(item).split(":", 1)[0] for item in metadata["source_entries"]})
            packet_lines = [
                "---",
                f"task_id: {task_id}",
                f"target_path: {target}",
                f"prd_id: {metadata['prd_id']}",
                f"product: {metadata['product']}",
                f"baseline_version: {metadata['baseline_version']}",
                f"date: {metadata['date']}",
                f"author: {metadata['author']}",
                f"category: {metadata['category']}",
                f"feature: {metadata['feature']}",
                f"category_domain: {metadata['category_domain']}",
                f"category_goal: {metadata['category_goal']}",
                "category_contract:",
                *[f"  - {key}={value}" for key, value in metadata["_category_contract"].items()],
                "category_fit:",
                *[f"  - {item}" for item in metadata["category_fit"]],
                "source_scope:",
                *[f"  - {item}" for item in source_scope],
                "behavior_inventory:",
                "  - 完整行为清单见目标 PRD 追溯输入",
                f"complexity: {metadata['complexity']}",
                "complexity_reasons:",
                *[f"  - {item}" for item in metadata["complexity_reasons"]],
                "decomposition_candidates:",
                *[f"  - {item}" for item in metadata["decomposition_candidates"]],
                "decomposition_basis:",
                *[f"  - {item}" for item in metadata["decomposition_basis"]],
                "feature_points:",
                *[f"  - FP-{fp_index:02d}" for fp_index in range(1, metadata["function_point_count"] + 1)],
                "verification_evidence:",
                "  - 验证证据见目标 PRD",
                "writer_path: .project-prd/tools/project-prd-writer/SKILL.md",
                "template_path: .project-prd/tools/project-prd-writer/references/prd-template.md",
                "acceptance_criteria:",
                "  - 单文件校验和全局 finalize 通过",
                "---",
                "",
                "# Project PRD Task",
            ]
            (task_root / f"{task_id}.md").write_text(
                "\n".join(packet_lines) + "\n",
                encoding="utf-8",
            )
            tasks.append({
                "task_id": task_id,
                "target_path": target,
                "agent_id": agent_id,
                "status": "completed",
                "attempt": 1,
                "error": None,
                "attempts": [{
                    "attempt": 1,
                    "agent_id": agent_id,
                    "status": "completed",
                    "error": None,
                }],
            })
        (workspace / ".analysis" / "progress.json").write_text(
            json.dumps({"schema_version": 1, "tasks": tasks}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def initialize(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root))

    def test_full_lifecycle_and_one_time_gate(self) -> None:
        self.initialize()
        workspace = self.root / ".project-prd"
        owner = json.loads((workspace / ".project-prd-owner.json").read_text(encoding="utf-8"))
        manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
        initialization = json.loads(
            (workspace / ".history" / "initialization.json").read_text(encoding="utf-8")
        )
        self.assertEqual(3, owner["format_version"])
        self.assertEqual(3, manifest["format_version"])
        self.assertEqual(3, initialization["format_version"])
        self.assertIn("editable_files", initialization)
        self.assertEqual(initialization["prd_files"], initialization.get("editable_files"))
        self.assertEqual({
            "covered": 1,
            "total": 1,
            "uncovered": [],
            "rate_percent": 100.0,
        }, initialization["feature_coverage"])
        guard = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        self.run_command(str(guard), "integrity", "--project-root", str(self.root))
        duplicate = self.run_command(
            str(BOOTSTRAP), "prepare", "--project-root", str(self.root), expected=2
        )
        self.assertIn("project-prd-clear", duplicate.stderr)
        clear_script = self.root / ".agents" / "skills" / "project-prd-clear" / "scripts" / "clear_project_prd.py"
        self.run_command(
            str(clear_script), "--project-root", str(self.root), "--confirm", "PROJECT-PRD-CLEAR"
        )
        self.assertFalse((self.root / ".project-prd").exists())
        self.assertFalse((self.root / ".agents" / "skills" / "project-prd-edit").exists())

    def test_controlled_edit_updates_manifest_and_history(self) -> None:
        self.initialize()
        draft = self.root / "work" / "order-query.md"
        draft.parent.mkdir()
        draft.write_text(simple_prd_text("且结果必须稳定"), encoding="utf-8")
        result = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "update",
            "--target", "订单系统/订单查询.md", "--source", str(draft),
            "--reason", "明确查询的无副作用限制",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(1, payload["generation"])
        self.assertTrue((self.root / payload["audit_record"]).is_file())

    def test_controlled_edit_tracks_arbitrary_binary_resource(self) -> None:
        self.initialize()
        source = self.root / "docs" / "comparison.png"
        source.parent.mkdir()
        before = b"\x89PNG\r\n\x1a\n\x00\xffbefore"
        source.write_bytes(before)

        result = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "create",
            "--target", "assets/comparisons/ink-builder.png", "--source", str(source),
            "--reason", "新增 PRD 二进制对比图资源",
        )

        payload = json.loads(result.stdout)
        target = self.root / ".project-prd" / "assets" / "comparisons" / "ink-builder.png"
        manifest = json.loads(
            (self.root / ".project-prd" / "manifest.json").read_text(encoding="utf-8")
        )
        receipt = json.loads((self.root / payload["audit_record"]).read_text(encoding="utf-8"))
        self.assertEqual(before, target.read_bytes())
        self.assertEqual(hashlib.sha256(before).hexdigest(), manifest["files"]["assets/comparisons/ink-builder.png"])
        self.assertEqual("assets/comparisons/ink-builder.png", receipt["changes"][0]["target"])

        after = b"\x89PNG\r\n\x1a\n\x00\xfeafter"
        source.write_bytes(after)
        updated = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "update",
            "--target", "assets/comparisons/ink-builder.png", "--source", str(source),
            "--reason", "优化 PRD 对比图资源",
        )
        updated_payload = json.loads(updated.stdout)
        self.assertEqual(2, updated_payload["generation"])
        self.assertEqual(after, target.read_bytes())
        guard = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        self.run_command(str(guard), "integrity", "--project-root", str(self.root))

        target.write_bytes(b"tampered")
        rejected = self.run_command(
            str(guard), "integrity", "--project-root", str(self.root), expected=2
        )
        self.assertIn("未经受控入口修改", rejected.stderr)

    def test_controlled_edit_accepts_resources_in_arbitrary_locations_and_formats(self) -> None:
        self.initialize()
        work = self.root / "work"
        work.mkdir()
        payloads = {
            "overview.json": b'{"kind":"resource"}\n',
            ".assets/raw/data.bin": b"\x00\xff\x10",
            "docs/samples/readme.md": b"# Resource markdown\n",
            "订单系统/comparison.svg": b'<svg><script>opaque resource bytes</script></svg>\n',
        }
        changes = []
        for index, (target, content) in enumerate(payloads.items()):
            source = work / f"source-{index}.bin"
            source.write_bytes(content)
            changes.append({"operation": "create", "target": target, "source": str(source)})
        changes_path = work / "changes.json"
        changes_path.write_text(json.dumps(changes, ensure_ascii=False), encoding="utf-8")

        self.run_command(
            str(EDIT), "--project-root", str(self.root), "--changes", str(changes_path),
            "--reason", "新增跨目录、多格式 PRD 资源",
        )
        manifest = json.loads((self.root / ".project-prd" / "manifest.json").read_text(encoding="utf-8"))
        for target, content in payloads.items():
            self.assertEqual(content, (self.root / ".project-prd" / target).read_bytes())
            self.assertEqual(hashlib.sha256(content).hexdigest(), manifest["files"][target])

    def test_finalize_tracks_arbitrary_binary_resources(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        resource = self.root / ".project-prd" / "assets" / "raw" / "comparison.bin"
        resource.parent.mkdir(parents=True)
        resource.write_bytes(b"\xff\xfe\x00\x00")

        self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root))
        manifest = json.loads((self.root / ".project-prd" / "manifest.json").read_text(encoding="utf-8"))
        initialization = json.loads((self.root / ".project-prd" / ".history" / "initialization.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(resource.read_bytes()).hexdigest(), manifest["files"]["assets/raw/comparison.bin"])
        self.assertIn("assets/raw/comparison.bin", initialization["editable_files"])

    def test_controlled_edit_rejects_project_prd_functional_targets(self) -> None:
        self.initialize()
        source = self.root / "work" / "resource.bin"
        source.parent.mkdir()
        source.write_bytes(b"resource")
        invalid_targets = (
            "manifest.json", "INDEX.md", ".project-prd-owner.json", ".initializing.json",
            ".gitignore", "tools/forbidden.bin", ".history/forbidden.bin",
            ".analysis/forbidden.bin", "output/forbidden.bin", "cache/__pycache__/x.bin",
            "cache/generated.pyc",
        )

        for target in invalid_targets:
            with self.subTest(target=target):
                result = self.run_command(
                    str(EDIT), "--project-root", str(self.root), "--operation", "create",
                    "--target", target, "--source", str(source),
                    "--reason", "验证受控目标边界", expected=2,
                )
                self.assertIn("不允许作为资源编辑", result.stderr)

    def test_controlled_update_adopts_existing_untracked_binary_resource_without_bootstrap(self) -> None:
        self.initialize()
        target = self.root / ".project-prd" / "legacy" / "comparison.dat"
        target.parent.mkdir()
        target.write_bytes(b"\xfflegacy")
        source = self.root / "docs" / "comparison.dat"
        source.parent.mkdir()
        source.write_bytes(b"\x00optimized")

        result = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "update",
            "--target", "legacy/comparison.dat", "--source", str(source),
            "--reason", "受控接管既有未登记资源",
        )
        payload = json.loads(result.stdout)
        receipt = json.loads((self.root / payload["audit_record"]).read_text(encoding="utf-8"))
        manifest = json.loads((self.root / ".project-prd" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(b"\x00optimized", target.read_bytes())
        self.assertEqual("create", receipt["changes"][0]["operation"])
        self.assertIsNone(receipt["changes"][0]["before_sha256"])
        self.assertIn("legacy/comparison.dat", manifest["files"])
        guard = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        self.run_command(str(guard), "integrity", "--project-root", str(self.root))

    def test_controlled_delete_audits_existing_untracked_resource(self) -> None:
        self.initialize()
        target = self.root / ".project-prd" / "legacy" / "obsolete.bin"
        target.parent.mkdir()
        target.write_bytes(b"obsolete")

        result = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "delete",
            "--target", "legacy/obsolete.bin", "--reason", "删除既有未登记资源",
            "--confirm-delete", "DELETE-PRD",
        )

        payload = json.loads(result.stdout)
        receipt = json.loads((self.root / payload["audit_record"]).read_text(encoding="utf-8"))
        self.assertFalse(target.exists())
        self.assertEqual("delete", receipt["changes"][0]["operation"])
        self.assertIsNone(receipt["changes"][0]["before_sha256"])
        guard = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        self.run_command(str(guard), "integrity", "--project-root", str(self.root))

    def test_skill_update_syncs_runtime_without_changing_prd_edit_chain(self) -> None:
        self.initialize()
        draft = self.root / "work" / "order-query.md"
        draft.parent.mkdir()
        draft.write_text(simple_prd_text("且结果必须稳定"), encoding="utf-8")
        self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "update",
            "--target", "订单系统/订单查询.md", "--source", str(draft),
            "--reason", "建立 update 前的受控编辑链",
        )

        workspace = self.root / ".project-prd"
        prd_path = workspace / "订单系统" / "订单查询.md"
        index_path = workspace / "INDEX.md"
        before_prd = prd_path.read_text(encoding="utf-8")
        before_index = index_path.read_text(encoding="utf-8")
        before_manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
        installed_skill = self.root / ".agents" / "skills" / "project-prd-serve" / "SKILL.md"
        installed_runtime = workspace / "tools" / "project_prd_lib.py"
        installed_skill.write_text("stale skill\n", encoding="utf-8")
        installed_runtime.write_text("stale runtime\n", encoding="utf-8")

        result = self.run_command(
            str(BOOTSTRAP), "update", "--project-root", str(self.root)
        )
        payload = json.loads(result.stdout)
        after_manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual("updated", payload["status"])
        self.assertEqual(
            (SKILL_ROOT / "assets" / "project-skills" / "project-prd-serve" / "SKILL.md").read_text(encoding="utf-8"),
            installed_skill.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            (SKILL_ROOT / "scripts" / "project_prd_lib.py").read_text(encoding="utf-8"),
            installed_runtime.read_text(encoding="utf-8"),
        )
        self.assertEqual(before_prd, prd_path.read_text(encoding="utf-8"))
        self.assertEqual(before_index, index_path.read_text(encoding="utf-8"))
        for key in ("edit_generation", "last_authorized_edit", "updated_at"):
            self.assertEqual(before_manifest[key], after_manifest[key])
        self.assertEqual(1, after_manifest["skill_update_generation"])
        self.assertEqual(payload["audit_record"], after_manifest["last_authorized_skill_update"])
        audit = json.loads((self.root / payload["audit_record"]).read_text(encoding="utf-8"))
        self.assertEqual("skill-update", audit["type"])
        guard = workspace / "tools" / "project_prd_guard.py"
        self.run_command(str(guard), "integrity", "--project-root", str(self.root))

    def test_skill_update_does_not_discover_or_register_resources(self) -> None:
        self.initialize()
        workspace = self.root / ".project-prd"
        source = self.root / "work" / "tracked.bin"
        source.parent.mkdir()
        source.write_bytes(b"tracked")
        self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "create",
            "--target", "assets/tracked.bin", "--source", str(source),
            "--reason", "建立受控资源基线",
        )
        manifest_before = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
        tracked_hash = manifest_before["files"]["assets/tracked.bin"]
        (workspace / "assets" / "tracked.bin").write_bytes(b"tampered-after-registration")
        untracked = workspace / "other" / "untracked.dat"
        untracked.parent.mkdir()
        untracked.write_bytes(b"untracked")

        update_result = self.run_command(
            str(BOOTSTRAP), "update", "--project-root", str(self.root)
        )
        update_payload = json.loads(update_result.stdout)
        manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
        self.assertNotIn("legacy_resources", update_payload)
        self.assertNotIn("pending_legacy_resources", manifest)
        self.assertEqual(tracked_hash, manifest["files"]["assets/tracked.bin"])
        self.assertNotIn("other/untracked.dat", manifest["files"])
        update_audit = json.loads(
            (self.root / update_payload["audit_record"]).read_text(encoding="utf-8")
        )
        self.assertNotIn("legacy_resources", update_audit)
        guard = workspace / "tools" / "project_prd_guard.py"
        integrity = self.run_command(str(guard), "integrity", "--project-root", str(self.root), expected=2)
        self.assertIn("未经受控入口修改：assets/tracked.bin", integrity.stderr)
        self.assertIn("发现未登记 PRD/资源文件：other/untracked.dat", integrity.stderr)

    def test_skill_update_rejects_invalid_update_generation(self) -> None:
        self.initialize()
        manifest_path = self.root / ".project-prd" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["skill_update_generation"] = True
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        result = self.run_command(
            str(BOOTSTRAP), "update", "--project-root", str(self.root), expected=2
        )
        self.assertIn("skill_update_generation 必须是非负整数", result.stderr)

    def test_update_cannot_change_prd_identity(self) -> None:
        self.initialize()
        draft = self.root / "work" / "changed-id.md"
        draft.parent.mkdir()
        draft.write_text(
            simple_prd_text().replace("PRD-ORDER-QUERY", "PRD-ORDER-REPLACED"), encoding="utf-8"
        )
        result = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "update",
            "--target", "订单系统/订单查询.md", "--source", str(draft),
            "--reason", "尝试替换 PRD 身份", expected=2,
        )
        self.assertIn("update 必须保持 prd_id 稳定", result.stderr)

    def test_controlled_create_and_delete(self) -> None:
        self.initialize()
        draft = self.root / "work" / "order-detail.md"
        draft.parent.mkdir()
        second = (
            simple_prd_text()
            .replace("PRD-ORDER-QUERY", "PRD-ORDER-DETAIL")
            .replace("feature: 订单查询", "feature: 订单详情")
            .replace("Demo 订单查询 产品需求文档", "Demo 订单详情 产品需求文档")
            .replace("src/orders.py:find_order", "src/orders.py:find_detail")
        )
        draft.write_text(second, encoding="utf-8")
        self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "create",
            "--target", "订单系统/订单详情.md", "--source", str(draft),
            "--reason", "新增订单详情 PRD",
        )
        self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "delete",
            "--target", "订单系统/订单详情.md", "--reason", "用户明确删除该 PRD",
            "--confirm-delete", "DELETE-PRD",
        )
        manifest = json.loads((self.root / ".project-prd" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(2, manifest["edit_generation"])

    def test_batch_edit_atomically_updates_shared_category_contract(self) -> None:
        self.prepare()
        first = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        first.parent.mkdir()
        first.write_text(simple_prd_text(), encoding="utf-8")
        second_content = (
            simple_prd_text()
            .replace("PRD-ORDER-QUERY", "PRD-ORDER-DETAIL")
            .replace("feature: 订单查询", "feature: 订单详情")
            .replace("Demo 订单查询 产品需求文档", "Demo 订单详情 产品需求文档")
            .replace("src/orders.py:find_order", "src/orders.py:find_detail")
        )
        second = self.root / ".project-prd" / "订单系统" / "订单详情.md"
        second.write_text(second_content, encoding="utf-8")
        self.complete_prd_tasks()
        self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root))

        work = self.root / "work"
        work.mkdir()
        first_draft = work / "query.md"
        second_draft = work / "detail.md"
        resource_draft = work / "comparison.bin"
        resource_draft.write_bytes(b"\x00mixed-resource\xff")
        replacements = (
            ("category_domain: 订单数据", "category_domain: 订单生命周期数据"),
            (
                "category_goal: 帮助用户准确查询和管理订单信息",
                "category_goal: 帮助用户在订单生命周期内一致地查询和管理信息",
            ),
            (
                "  - outcome=准确查询和管理订单信息",
                "  - outcome=在订单生命周期内一致地查询和管理信息",
            ),
        )
        first_changed = simple_prd_text("并保持生命周期一致")
        second_changed = second_content.replace(
            "查询不得修改订单  ", "查询不得修改订单 并保持生命周期一致 "
        )
        for old, new in replacements:
            first_changed = first_changed.replace(old, new)
            second_changed = second_changed.replace(old, new)
        first_draft.write_text(first_changed, encoding="utf-8")
        second_draft.write_text(second_changed, encoding="utf-8")

        single = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "update",
            "--target", "订单系统/订单查询.md", "--source", str(first_draft),
            "--reason", "统一升级订单分类契约", expected=2,
        )
        self.assertIn("category_domain/category_goal/category_contract 不一致", single.stderr)
        self.assertEqual(simple_prd_text(), first.read_text(encoding="utf-8"))

        changes = work / "changes.json"
        changes.write_text(json.dumps([
            {
                "operation": "update",
                "target": "订单系统/订单查询.md",
                "source": str(first_draft),
            },
            {
                "operation": "update",
                "target": "订单系统/订单详情.md",
                "source": str(second_draft),
            },
            {
                "operation": "create",
                "target": "assets/order/comparison.bin",
                "source": str(resource_draft),
            },
        ], ensure_ascii=False), encoding="utf-8")
        result = self.run_command(
            str(EDIT), "--project-root", str(self.root), "--changes", str(changes),
            "--reason", "统一升级订单分类契约",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(3, payload["change_count"])
        self.assertEqual(1, payload["generation"])
        receipt = json.loads((self.root / payload["audit_record"]).read_text(encoding="utf-8"))
        self.assertEqual(3, receipt["format_version"])
        self.assertEqual(3, len(receipt["changes"]))
        self.assertEqual(
            b"\x00mixed-resource\xff",
            (self.root / ".project-prd" / "assets" / "order" / "comparison.bin").read_bytes(),
        )

    def test_direct_prd_edit_is_rejected(self) -> None:
        self.initialize()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.write_text(simple_prd_text("未受控修改"), encoding="utf-8")
        guard = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        result = self.run_command(str(guard), "integrity", "--project-root", str(self.root), expected=2)
        self.assertIn("未经受控入口修改", result.stderr)

    def test_manifest_summary_and_receipt_are_verified(self) -> None:
        self.initialize()
        manifest_path = self.root / ".project-prd" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["prd_count"] = 999
        manifest["last_authorized_edit"] = ".history/missing.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        guard = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        result = self.run_command(str(guard), "integrity", "--project-root", str(self.root), expected=2)
        self.assertIn("manifest.prd_count", result.stderr)
        self.assertIn("missing.json", result.stderr)

    def test_ci_rejects_runtime_mutation_with_rehashed_manifest(self) -> None:
        subprocess.run(["git", "init"], cwd=self.root, check=True, capture_output=True)
        self.initialize()
        commit_message = (
            "[other] create test baseline\n"
            "[why] verify project-prd CI protection\n"
            "[how] commit an isolated temporary fixture\n"
            "[influence] temporary test repository only\n"
            "[jira] none"
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=Project PRD Test", "-c", "user.email=test@example.com",
             "commit", "-m", commit_message],
            cwd=self.root, check=True, capture_output=True, text=True,
        )
        base_ref = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

        runtime = self.root / ".project-prd" / "tools" / "project_prd_guard.py"
        runtime.write_text(runtime.read_text(encoding="utf-8") + "\n# unauthorized runtime change\n", encoding="utf-8")
        manifest_path = self.root / ".project-prd" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = project_prd_lib.compute_hashes(self.root / ".project-prd")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=Project PRD Test", "-c", "user.email=test@example.com",
             "commit", "-m", commit_message.replace("baseline", "runtime mutation")],
            cwd=self.root, check=True, capture_output=True, text=True,
        )

        trusted_guard = SKILL_ROOT / "assets" / "runtime" / "project_prd_guard.py"
        env = dict(os.environ)
        env["PYTHONPATH"] = str(SKILL_ROOT / "scripts")
        result = subprocess.run(
            [sys.executable, str(trusted_guard), "ci", "--project-root", str(self.root), "--base-ref", base_ref],
            cwd=self.root, text=True, capture_output=True, check=False, env=env,
        )
        self.assertEqual(2, result.returncode, msg=result.stdout + result.stderr)
        self.assertIn("不得在普通 PR 修改 project-prd 运行时", result.stderr)

    def test_ci_accepts_authorized_binary_resource_in_arbitrary_directory(self) -> None:
        subprocess.run(["git", "init"], cwd=self.root, check=True, capture_output=True)
        self.initialize()
        commit_message = (
            "[other] create test baseline\n"
            "[why] verify project-prd resource CI protection\n"
            "[how] commit an isolated temporary fixture\n"
            "[influence] temporary test repository only\n"
            "[jira] none"
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=Project PRD Test", "-c", "user.email=test@example.com",
             "commit", "-m", commit_message],
            cwd=self.root, check=True, capture_output=True, text=True,
        )
        base_ref = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

        source = self.root / "work" / "diagram.bin"
        source.parent.mkdir()
        source.write_bytes(b"\x00authorized-resource\xff")
        self.run_command(
            str(EDIT), "--project-root", str(self.root), "--operation", "create",
            "--target", ".assets/nested/diagram.bin", "--source", str(source),
            "--reason", "新增 CI 验证二进制资源",
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=Project PRD Test", "-c", "user.email=test@example.com",
             "commit", "-m", commit_message.replace("baseline", "resource change")],
            cwd=self.root, check=True, capture_output=True, text=True,
        )

        trusted_guard = SKILL_ROOT / "assets" / "runtime" / "project_prd_guard.py"
        env = dict(os.environ)
        env["PYTHONPATH"] = str(SKILL_ROOT / "scripts")
        result = subprocess.run(
            [sys.executable, str(trusted_guard), "ci", "--project-root", str(self.root), "--base-ref", base_ref],
            cwd=self.root, text=True, capture_output=True, check=False, env=env,
        )
        self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)
        self.assertIn("project-prd CI guard PASS", result.stdout)

    def test_clear_requires_exact_confirmation(self) -> None:
        self.initialize()
        result = self.run_command(
            str(CLEAR), "--project-root", str(self.root), "--confirm", "wrong", expected=2
        )
        self.assertIn("确认令牌无效", result.stderr)
        self.assertTrue((self.root / ".project-prd").is_dir())

    def test_clear_refuses_unowned_same_name_directory(self) -> None:
        workspace = self.root / ".project-prd"
        workspace.mkdir()
        sentinel = workspace / "user-content.txt"
        sentinel.write_text("keep", encoding="utf-8")
        result = self.run_command(
            str(CLEAR), "--project-root", str(self.root), "--confirm", "PROJECT-PRD-CLEAR", expected=2
        )
        self.assertIn("归属", result.stderr)
        self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))

    def test_clear_marker_preflight_fails_without_deleting(self) -> None:
        self.initialize()
        agents_path = self.root / "AGENTS.md"
        agents_path.write_text(
            agents_path.read_text(encoding="utf-8").replace("<!-- PROJECT_PRD_RULES_END -->", ""),
            encoding="utf-8",
        )
        result = self.run_command(
            str(CLEAR), "--project-root", str(self.root), "--confirm", "PROJECT-PRD-CLEAR", expected=2
        )
        self.assertIn("受管标记缺失或重复", result.stderr)
        self.assertTrue((self.root / ".project-prd").is_dir())
        self.assertTrue((self.root / ".agents" / "skills" / "project-prd-edit").is_dir())

    def test_clear_preserves_existing_agents_content(self) -> None:
        original = "# Team Rules\n\nKeep this rule.\n"
        (self.root / "AGENTS.md").write_text(original, encoding="utf-8")
        self.initialize()
        clear_script = self.root / ".agents" / "skills" / "project-prd-clear" / "scripts" / "clear_project_prd.py"
        self.run_command(
            str(clear_script), "--project-root", str(self.root), "--confirm", "PROJECT-PRD-CLEAR"
        )
        self.assertEqual(original, (self.root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_project_spec_workspace_remains_independent(self) -> None:
        original_agents = (
            "<!-- PROJECT_SPEC_RULES_START -->\n"
            "## Existing Project Spec Rules\n"
            "<!-- PROJECT_SPEC_RULES_END -->\n"
        )
        (self.root / "AGENTS.md").write_text(original_agents, encoding="utf-8")
        sentinel = self.root / ".project-spec" / "sentinel.txt"
        sentinel.parent.mkdir()
        sentinel.write_text("keep", encoding="utf-8")
        self.initialize()
        clear_script = self.root / ".agents" / "skills" / "project-prd-clear" / "scripts" / "clear_project_prd.py"
        self.run_command(
            str(clear_script), "--project-root", str(self.root), "--confirm", "PROJECT-PRD-CLEAR"
        )
        self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))
        self.assertEqual(original_agents, (self.root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_failed_finalize_remains_partial_and_can_be_cleared(self) -> None:
        self.prepare()
        invalid = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        invalid.parent.mkdir()
        invalid.write_text("# invalid\n", encoding="utf-8")
        self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2)
        status = self.run_command(str(BOOTSTRAP), "status", "--project-root", str(self.root))
        payload = json.loads(status.stdout)
        self.assertEqual("partial", payload["status"])
        self.assertTrue(payload["resumable"])
        self.assertEqual("resume", payload["recovery_action"])

    def test_unowned_partial_workspace_is_not_resumable(self) -> None:
        workspace = self.root / ".project-prd"
        workspace.mkdir()
        (workspace / "user-content.txt").write_text("keep", encoding="utf-8")
        status = self.run_command(str(BOOTSTRAP), "status", "--project-root", str(self.root))
        payload = json.loads(status.stdout)
        self.assertEqual("partial", payload["status"])
        self.assertFalse(payload["resumable"])
        self.assertEqual("clear", payload["recovery_action"])

    def test_full_prd_requires_why_dimensions(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text().replace("**用户痛点**", "**原因**"), encoding="utf-8")
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2)
        self.assertIn("用户痛点", result.stderr)

    def test_template_placeholder_is_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("订单查询场景", "[场景]"), encoding="utf-8"
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("未替换的模板占位符", result.stderr)

    def test_tbd_content_and_fake_source_are_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("用户需要定位指定订单", "TBD"), encoding="utf-8"
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("已知缺口必须集中到第六章", result.stderr)

        target.write_text(
            simple_prd_text().replace("src/orders.py:find_order", "src/missing.py:missing_symbol"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("source_entries 指向的文件不存在", result.stderr)

    def test_missing_source_symbol_is_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("find_order", "definitely_missing_symbol"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("Symbol 定义不存在", result.stderr)

    def test_qualified_symbol_token_bypass_is_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("find_order", "find_order.return"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("Symbol 必须是单一名称", result.stderr)

    def test_fake_test_path_is_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("tests/test_orders.py", "tests/missing_orders.py"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("验证依据 指向的文件不存在", result.stderr)

    def test_production_source_cannot_masquerade_as_test_evidence(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("tests/test_orders.py", "src/orders.py"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("必须指向测试目录或测试命名文件", result.stderr)

    def test_filename_merely_ending_in_test_letters_is_not_test_evidence(self) -> None:
        (self.root / "src" / "contest.py").write_text("value = True\n", encoding="utf-8")
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace("tests/test_orders.py", "src/contest.py"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("必须指向测试目录或测试命名文件", result.stderr)

    def test_fake_behavior_source_evidence_is_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        invalid = simple_prd_text().replace(
            "| B001 | FP-01 | `src/orders.py:find_order`",
            "| B001 | FP-01 | `src/orders.py:missing_behavior_symbol`",
        )
        target.write_text(invalid, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("Behavior B001 源码证据 的 Symbol 定义不存在", result.stderr)

    def test_workflow_is_fail_closed_and_clear_requires_all_artifacts_absent(self) -> None:
        workflow = (SKILL_ROOT / "assets" / "github" / "project-prd-guard.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("python .project-prd/tools/project_prd_guard.py", workflow)
        self.assertIn("trusted project-prd guard is absent from the base revision", workflow)
        self.assertIn("$PROJECT_PRD_BASE_SHA:.project-prd/tools/project_prd_guard.py", workflow)
        self.assertIn("$PROJECT_PRD_BASE_SHA:.project-prd/tools/project_prd_lib.py", workflow)
        self.assertIn("[ -e .github/workflows/project-prd-guard.yml ]", workflow)
        self.assertIn("PROJECT_PRD_RULES_(START|END)", workflow)

    def test_internal_prd_writer_is_bundled_and_mandatory(self) -> None:
        internal_skill = (
            SKILL_ROOT / "assets" / "internal-skills" / "project-prd-writer" / "SKILL.md"
        )
        contract = internal_skill.parent / "references" / "full-template-contract.md"
        self.assertTrue(internal_skill.is_file())
        self.assertTrue(contract.is_file())
        self.assertIn("name: project-prd-writer", internal_skill.read_text(encoding="utf-8"))
        main_skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("assets/internal-skills/project-prd-writer/SKILL.md", main_skill)
        contract_text = contract.read_text(encoding="utf-8")
        for section in (
            "功能描述", "交互逻辑", "跳转逻辑", "跳转过程逻辑",
            "正向限制", "反向限制", "异常/空态/错误提示",
        ):
            self.assertIn(section, contract_text)
        self.prepare()
        installed_writer = self.root / ".project-prd" / "tools" / "project-prd-writer"
        self.assertTrue((installed_writer / "SKILL.md").is_file())
        self.assertTrue((installed_writer / "references" / "prd-template.md").is_file())
        self.assertFalse((self.root / ".agents" / "skills" / "project-prd-writer").exists())

    def test_main_contract_requires_one_fresh_subagent_per_prd(self) -> None:
        main_skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "每份细分功能 PRD 必须委派给一个全新的独立子代理",
            "主代理不得亲自撰写 PRD 正文",
            "主代理只负责全局分析、任务包、调度和最终门禁",
            "同一子代理不得处理第二份 PRD",
            ".project-prd/.analysis/tasks/<task-id>.md",
            ".project-prd/.analysis/progress.json",
        ):
            self.assertIn(required, main_skill)

    def test_completion_report_requires_feature_coverage_with_auditable_counts(self) -> None:
        main_skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (SKILL_ROOT / "references" / "initialization-workflow.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "功能覆盖率",
            "已覆盖细分功能数",
            "已识别细分功能总数",
            "未覆盖功能清单",
            "covered / total",
        ):
            self.assertIn(required, main_skill + workflow)

    def test_prd_task_packet_declares_all_required_fields(self) -> None:
        workflow = (SKILL_ROOT / "references" / "initialization-workflow.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "`task_id`", "`target_path`", "`category`", "`feature`",
            "`category_domain`", "`category_goal`", "`category_contract`", "`category_fit`",
            "`source_scope`", "`behavior_inventory`", "`complexity`",
            "`complexity_reasons`", "`decomposition_candidates`", "`decomposition_basis`",
            "`feature_points`", "`verification_evidence`", "`writer_path`",
            "`template_path`", "`acceptance_criteria`",
        ):
            self.assertIn(required, workflow)

    def test_writer_is_isolated_to_one_task_and_one_target(self) -> None:
        writer = (
            SKILL_ROOT / "assets" / "internal-skills" / "project-prd-writer" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for required in (
            "只读取当前任务包",
            "只写入任务包指定的唯一目标文件",
            "不得读取其他 PRD 正文",
            "不得读取其他任务包",
            "不得运行 `finalize` 或 `integrity`",
            "不得扩展读取范围",
        ):
            self.assertIn(required, writer)

    def test_progress_contract_bounds_parallelism_and_resumes_incomplete_tasks(self) -> None:
        workflow = (SKILL_ROOT / "references" / "initialization-workflow.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "`pending/running/completed/failed`",
            "`task_id/target_path/agent_id/status/attempt/error`",
            "`attempts[]`",
            "`min(4, 可用子代理槽位, 未完成任务数)`",
            "续跑只重派 `pending/failed`",
            "不得重写 `completed`",
            "任何 `failed/running/pending` 项都必须阻止完成锁定",
        ):
            self.assertIn(required, workflow)

    def test_only_main_agent_runs_cross_prd_validation_and_finalize(self) -> None:
        workflow = (SKILL_ROOT / "references" / "initialization-workflow.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "子代理只执行单文件自审",
            "只有主代理可以生成 INDEX",
            "执行跨 PRD 分类契约、引用关系和完整覆盖校验",
            "不得以单个子代理成功代替全局校验",
        ):
            self.assertIn(required, workflow)

        self.prepare()
        workspace_ignore = (self.root / ".project-prd" / ".gitignore").read_text(
            encoding="utf-8"
        )
        self.assertIn(".analysis/", workspace_ignore)

    def test_finalize_rejects_prd_without_completed_subagent_task(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("没有逐 PRD 子代理任务", result.stderr)

    def test_finalize_rejects_pending_subagent_task(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        progress_path = self.root / ".project-prd" / ".analysis" / "progress.json"
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        progress["tasks"][0].update({
            "agent_id": None,
            "status": "pending",
            "attempt": 0,
            "error": None,
            "attempts": [],
        })
        progress_path.write_text(json.dumps(progress, ensure_ascii=False), encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("存在未完成的逐 PRD 子代理任务", result.stderr)

    def test_finalize_rejects_reused_agent_across_prds(self) -> None:
        self.prepare()
        first = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        first.parent.mkdir()
        first.write_text(simple_prd_text(), encoding="utf-8")
        second = self.root / ".project-prd" / "订单系统" / "订单详情.md"
        second.write_text(
            simple_prd_text()
            .replace("PRD-ORDER-QUERY", "PRD-ORDER-DETAIL")
            .replace("feature: 订单查询", "feature: 订单详情")
            .replace("Demo 订单查询 产品需求文档", "Demo 订单详情 产品需求文档")
            .replace("src/orders.py:find_order", "src/orders.py:find_detail"),
            encoding="utf-8",
        )
        self.complete_prd_tasks(agent_ids=["shared-agent", "shared-agent"])
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("同一子代理不得处理多份 PRD", result.stderr)

    def test_tampered_managed_asset_makes_partial_non_resumable(self) -> None:
        self.prepare()
        writer = self.root / ".project-prd" / "tools" / "project-prd-writer" / "SKILL.md"
        writer.write_text("tampered\n", encoding="utf-8")
        status = self.run_command(str(BOOTSTRAP), "status", "--project-root", str(self.root))
        payload = json.loads(status.stdout)
        self.assertEqual("partial", payload["status"])
        self.assertFalse(payload["resumable"])
        self.assertEqual("clear", payload["recovery_action"])

    def test_progress_path_escape_makes_partial_non_resumable(self) -> None:
        self.prepare()
        progress = {
            "schema_version": 1,
            "tasks": [{
                "task_id": "prd-001",
                "target_path": "../escape.md",
                "agent_id": None,
                "status": "pending",
                "attempt": 0,
                "error": None,
                "attempts": [],
            }],
        }
        (self.root / ".project-prd" / ".analysis" / "progress.json").write_text(
            json.dumps(progress), encoding="utf-8"
        )
        status = self.run_command(str(BOOTSTRAP), "status", "--project-root", str(self.root))
        payload = json.loads(status.stdout)
        self.assertFalse(payload["resumable"])
        self.assertEqual("clear", payload["recovery_action"])

    def test_finalize_rejects_missing_task_packet(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        (self.root / ".project-prd" / ".analysis" / "tasks" / "prd-001.md").unlink()
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("子代理任务包不存在或不安全", result.stderr)

    def test_finalize_rejects_incomplete_task_packet(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        packet = self.root / ".project-prd" / ".analysis" / "tasks" / "prd-001.md"
        packet.write_text(
            packet.read_text(encoding="utf-8").replace(
                "behavior_inventory:\n  - 完整行为清单见目标 PRD 追溯输入\n", ""
            ),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("缺少字段：behavior_inventory", result.stderr)

    def test_finalize_rejects_task_source_scope_escape(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        packet = self.root / ".project-prd" / ".analysis" / "tasks" / "prd-001.md"
        packet.write_text(
            packet.read_text(encoding="utf-8").replace("  - src/orders.py\n", "  - ../escape.py\n"),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("source_scope 路径无效", result.stderr)

    def test_finalize_rejects_symlinked_prd_file(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(simple_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        outside = Path(self.temp_dir.name) / "outside-prd.md"
        target.replace(outside)
        target.symlink_to(outside)
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("符号链接", result.stderr)

    def test_symlinked_task_directory_makes_partial_non_resumable(self) -> None:
        self.prepare()
        task_root = self.root / ".project-prd" / ".analysis" / "tasks"
        task_root.rmdir()
        outside = Path(self.temp_dir.name) / "outside-tasks"
        outside.mkdir()
        task_root.symlink_to(outside, target_is_directory=True)
        status = self.run_command(str(BOOTSTRAP), "status", "--project-root", str(self.root))
        payload = json.loads(status.stdout)
        self.assertFalse(payload["resumable"])
        self.assertEqual("clear", payload["recovery_action"])

    def test_unclosed_running_attempt_makes_partial_non_resumable(self) -> None:
        self.prepare()
        progress = {
            "schema_version": 1,
            "tasks": [{
                "task_id": "prd-001",
                "target_path": "订单系统/订单查询.md",
                "agent_id": "agent-2",
                "status": "completed",
                "attempt": 2,
                "error": None,
                "attempts": [
                    {"attempt": 1, "agent_id": "agent-1", "status": "running", "error": None},
                    {"attempt": 2, "agent_id": "agent-2", "status": "completed", "error": None},
                ],
            }],
        }
        (self.root / ".project-prd" / ".analysis" / "progress.json").write_text(
            json.dumps(progress), encoding="utf-8"
        )
        status = self.run_command(str(BOOTSTRAP), "status", "--project-root", str(self.root))
        payload = json.loads(status.stdout)
        self.assertFalse(payload["resumable"])
        self.assertEqual("clear", payload["recovery_action"])

    def test_prepare_rejects_symlink_escape(self) -> None:
        outside = Path(self.temp_dir.name) / "outside-agents"
        outside.mkdir()
        (self.root / ".agents").symlink_to(outside, target_is_directory=True)
        result = self.run_command(
            str(BOOTSTRAP), "prepare", "--project-root", str(self.root), expected=2
        )
        self.assertIn("符号链接越出项目", result.stderr)
        self.assertEqual([], list(outside.iterdir()))
        self.assertFalse((self.root / ".project-prd").exists())

    def test_jump_logic_requires_explicit_no_jump_or_table(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        target.write_text(
            simple_prd_text().replace(
                "无页面跳转，操作在查询接口内完成。",
                "该功能没有额外说明。",
            ),
            encoding="utf-8",
        )
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("跳转逻辑必须提供包含表头和数据行", result.stderr)

    def test_exception_table_requires_all_five_categories(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        incomplete = simple_prd_text().replace("网络异常：不适用", "依赖异常：不适用")
        target.write_text(incomplete, encoding="utf-8")
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2)
        self.assertIn("异常提示表缺少类别：网络异常", result.stderr)

    def test_generic_catchall_category_is_rejected(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "工具" / "订单查询.md"
        target.parent.mkdir()
        mixed = simple_prd_text().replace("category: 订单系统", "category: 工具")
        target.write_text(mixed, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("无业务语义的兜底名称", result.stderr)
        self.assertIn("单成员分类也允许", result.stderr)

    def test_generic_count_category_is_rejected_after_nfkc_normalization(self) -> None:
        for category in ("模块　１", "分类01", "功能组二", "若干功能"):
            content = simple_prd_text().replace("category: 订单系统", f"category: {category}")
            with self.subTest(category=category), self.assertRaisesRegex(
                project_prd_lib.ProjectPrdError, "无业务语义的兜底名称"
            ):
                project_prd_lib.validate_prd(
                    content, Path(category) / "订单查询.md", self.root
                )

    def test_business_qualified_tool_category_is_not_rejected_by_name(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "工具与资源" / "订单查询.md"
        target.parent.mkdir()
        qualified = simple_prd_text().replace("category: 订单系统", "category: 工具与资源")
        target.write_text(qualified, encoding="utf-8")
        self.complete_prd_tasks()
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root))
        self.assertEqual(1, json.loads(result.stdout)["category_count"])

    def test_overview_feature_point_column_must_map_exactly(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        invalid = simple_prd_text().replace(
            "| 订单查询 | FP-01 按编号查询 |",
            "| 订单查询 | 按编号查询 FP-01 |",
        )
        target.write_text(invalid, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("‘功能点’列必须按顺序与 FP 一一对应", result.stderr)

    def test_category_members_must_share_domain_and_user_goal(self) -> None:
        self.prepare()
        first = self.root / ".project-prd" / "信源与工具" / "订单查询.md"
        first.parent.mkdir()
        first.write_text(
            simple_prd_text().replace("category: 订单系统", "category: 信源与工具"),
            encoding="utf-8",
        )
        second = self.root / ".project-prd" / "信源与工具" / "订单详情.md"
        mismatched = (
            simple_prd_text()
            .replace("category: 订单系统", "category: 信源与工具")
            .replace("PRD-ORDER-QUERY", "PRD-ORDER-DETAIL")
            .replace("feature: 订单查询", "feature: 订单详情")
            .replace("Demo 订单查询 产品需求文档", "Demo 订单详情 产品需求文档")
            .replace("src/orders.py:find_order", "src/orders.py:find_detail")
            .replace(
                "category_goal: 帮助用户准确查询和管理订单信息",
                "category_goal: 帮助运维人员安装设备应用包",
            )
        )
        second.write_text(mismatched, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("category_domain/category_goal/category_contract 不一致", result.stderr)

    def test_generic_shared_category_contract_is_rejected(self) -> None:
        invalid = simple_prd_text().replace(
            "  - object=订单数据",
            "  - object=通用技术能力",
        ).replace(
            "  - object=订单数据 @ src/orders.py:find_order",
            "  - object=通用技术能力 @ src/orders.py:find_order",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "过于泛化"):
            project_prd_lib.validate_prd(
                invalid, Path("信源与工具") / "订单查询.md", self.root
            )

    def test_category_members_need_two_common_evidenced_dimensions(self) -> None:
        self.prepare()
        first = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        first.parent.mkdir()
        first_content = simple_prd_text().replace(
            "  - object=订单数据\ncategory_fit:",
            "  - object=订单数据\n  - journey=订单读取旅程\ncategory_fit:",
        )
        first.write_text(first_content, encoding="utf-8")
        second = self.root / ".project-prd" / "订单系统" / "订单详情.md"
        second_content = (
            first_content
            .replace("PRD-ORDER-QUERY", "PRD-ORDER-DETAIL")
            .replace("feature: 订单查询", "feature: 订单详情")
            .replace("Demo 订单查询 产品需求文档", "Demo 订单详情 产品需求文档")
            .replace("src/orders.py:find_order", "src/orders.py:find_detail")
            .replace(
                "category_fit:\n  - actor=订单调用方 @ src/orders.py:find_detail\n"
                "  - object=订单数据 @ src/orders.py:find_detail",
                "category_fit:\n  - outcome=准确查询和管理订单信息 @ src/orders.py:find_detail\n"
                "  - journey=订单读取旅程 @ src/orders.py:find_detail",
            )
        )
        second.write_text(second_content, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("共同有源码证据的聚合维度少于两个", result.stderr)

    def test_complex_single_fp_is_rejected_even_with_many_aggregate_entries(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        compressed = complex_prd_text()
        for feature_point_id in ("FP-02", "FP-03", "FP-04"):
            compressed = compressed.replace(f"#### {feature_point_id}", f"##### 被压缩的 {feature_point_id}")
        target.write_text(compressed, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("complex PRD 至少需要 2 个Feature Point项", result.stderr)

    def test_every_feature_point_requires_all_seven_prd_writer_sections(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        incomplete = complex_prd_text().replace("**6. 反向限制**", "**6. 被压缩的限制**", 1)
        target.write_text(incomplete, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("FP-01 必须按固定顺序且恰好一次包含 prd-writer 完整 7 章节", result.stderr)

    def test_complex_feature_point_requires_behavior_coverage(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        compressed = complex_prd_text().replace(
            "| B007 | FP-04 | `src/flow.py:step7` | 用户可感知流程结果7 | 交互逻辑 |\n",
            "",
        ).replace(
            "| B008 | FP-04 | `src/flow.py:step8` | 用户可感知流程结果8 | 反向限制 |\n",
            "",
        )
        target.write_text(compressed, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("FP-04 至少需要 1 个独立 Behavior", result.stderr)

    def test_complex_feature_point_requires_main_and_boundary_behaviors(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        incomplete = (
            complex_prd_text()
            .replace("  - src/flow.py:step8\n", "")
            .replace(
                "| B008 | FP-04 | `src/flow.py:step8` | 用户可感知流程结果8 | 反向限制 |\n",
                "",
            )
            .replace("- B008 → `tests/test_flow.py`\n", "")
        )
        target.write_text(incomplete, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("FP-04 必须同时映射主路径 Behavior 和限制/异常 Behavior", result.stderr)

    def test_empty_decomposition_reason_is_rejected(self) -> None:
        invalid = simple_prd_text().replace(
            "  - FP-01: 按订单编号完成一次独立查询闭环",
            "  - FP-01:",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "元数据缺失|实质拆解理由"):
            project_prd_lib.validate_prd(invalid, Path("订单系统") / "订单查询.md", self.root)

    def test_complex_prd_cannot_use_sparse_interactions(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        compressed = simple_prd_text().replace(
            "complexity: simple\ncomplexity_reasons:\n  - 单一查询入口且直接返回查询结果",
            "complexity: complex\ncomplexity_reasons:\n  - 包含多阶段状态\n  - 包含异步失败清理",
        ).replace(
            "decomposition_basis:\n  - FP-01: 按订单编号完成一次独立查询闭环",
            "decomposition_basis:\n  - FP-01: 独立触发入口\n  - FP-02: 独立阶段转换\n  - FP-03: 独立策略分支\n  - FP-04: 独立失败清理",
        )
        target.write_text(compressed, encoding="utf-8")
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2)
        self.assertIn("至少需要 2 个Feature Point项", result.stderr)

    def test_every_source_entry_requires_behavior_mapping(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "订单系统" / "订单查询.md"
        target.parent.mkdir()
        incomplete = simple_prd_text().replace(
            "  - src/orders.py:find_order\n---",
            "  - src/orders.py:find_order\n  - src/orders.py:authorize_order\n---",
        )
        target.write_text(incomplete, encoding="utf-8")
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2)
        self.assertIn("未映射=src/orders.py:authorize_order", result.stderr)

    def test_verification_must_cover_every_behavior(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        incomplete = complex_prd_text().replace("- B004 → `tests/test_flow.py`\n", "")
        target.write_text(incomplete, encoding="utf-8")
        result = self.run_command(
            str(BOOTSTRAP), "finalize", "--project-root", str(self.root), expected=2
        )
        self.assertIn("验证依据未映射 Behavior ID：B004", result.stderr)

    def test_complete_complex_prd_passes_quality_gate(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        target.write_text(complex_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root))
        payload = json.loads(result.stdout)
        self.assertEqual(1, payload["prd_count"])
        self.assertEqual(4, payload["function_point_count"])
        self.assertEqual(8, payload["interaction_count"])
        self.assertEqual(4, payload["positive_constraint_count"])
        self.assertEqual(4, payload["negative_constraint_count"])
        self.assertEqual(5, payload["exception_count"])
        self.assertEqual(8, payload["behavior_count"])
        self.assertEqual({"simple": 0, "standard": 0, "complex": 1}, payload["complexity_counts"])
        self.assertEqual({
            "covered": 1,
            "total": 1,
            "uncovered": [],
            "rate_percent": 100.0,
        }, payload["feature_coverage"])

    def test_two_point_complex_prd_passes_without_four_point_floor(self) -> None:
        self.prepare()
        target = self.root / ".project-prd" / "流程管理" / "复杂流程.md"
        target.parent.mkdir()
        target.write_text(two_point_complex_prd_text(), encoding="utf-8")
        self.complete_prd_tasks()
        result = self.run_command(str(BOOTSTRAP), "finalize", "--project-root", str(self.root))
        payload = json.loads(result.stdout)
        self.assertEqual(2, payload["function_point_count"])
        self.assertGreaterEqual(payload["interaction_count"], 5)
        self.assertEqual(6, payload["behavior_count"])

    def test_multiple_anchor_candidates_cannot_be_compressed_into_one_fp(self) -> None:
        invalid = simple_prd_text().replace(
            "  - DC-01|trigger|按订单编号查询|src/orders.py:find_order|FP-01",
            "  - DC-01|trigger|按订单编号查询|src/orders.py:find_order|FP-01\n"
            "  - DC-02|stage|订单结果转换|src/orders.py:find_order|FP-01",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "恰好映射一个独立锚点候选"):
            project_prd_lib.validate_prd(
                invalid, Path("订单系统") / "订单查询.md", self.root
            )

    def test_candidate_evidence_must_be_covered_by_same_fp_behavior(self) -> None:
        invalid = complex_prd_text().replace(
            "DC-02|stage|中间状态转换|src/flow.py:step3|FP-02",
            "DC-02|stage|中间状态转换|src/flow.py:step1|FP-02",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "同一 FP 的 Behavior 覆盖"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_rule_matrix_must_cover_exact_code_items(self) -> None:
        invalid = simple_prd_text().replace(
            "| MX-NONE | FP-01 | none | `src/orders.py:find_order` | 无可枚举矩阵 | 无可枚举矩阵 |",
            "| MX-01 | FP-01 | mapping | `src/orders.py:find_order` | order_id<br>query_failed | order_id<br>missing_order |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "必须与代码项精确一致"):
            project_prd_lib.validate_prd(
                invalid, Path("订单系统") / "订单查询.md", self.root
            )

    def test_priority_matrix_order_must_match_code_order(self) -> None:
        invalid = complex_prd_text().replace(
            "| MX-01 | FP-02 | state | `src/flow.py:step3` | 待处理<br>处理中<br>完成 | 待处理<br>处理中<br>完成 |",
            "| MX-01 | FP-02 | state | `src/flow.py:step3` | 待处理<br>处理中<br>完成 | 完成<br>处理中<br>待处理 |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "顺序不一致"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_complex_matrix_signals_cannot_use_mx_none(self) -> None:
        invalid = complex_prd_text().replace(
            "| MX-01 | FP-02 | state | `src/flow.py:step3` | 待处理<br>处理中<br>完成 | 待处理<br>处理中<br>完成 |",
            "| MX-NONE | FP-02 | none | `src/flow.py:step3` | 无可枚举矩阵 | 无可枚举矩阵 |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "不得使用 MX-NONE"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_explicit_absence_of_state_matrix_allows_mx_none(self) -> None:
        valid = simple_prd_text().replace(
            "单一查询入口且直接返回查询结果",
            "单一查询入口且无状态转换",
        )
        metadata = project_prd_lib.validate_prd(
            valid, Path("订单系统") / "订单查询.md", self.root
        )
        self.assertEqual(0, metadata["matrix_count"])

    def test_mx_none_is_rejected_when_source_contains_rule_collection(self) -> None:
        orders = self.root / "src" / "orders.py"
        orders.write_text(
            orders.read_text(encoding="utf-8")
            + "\norder_states = ('PENDING', 'PAID', 'CANCELLED')\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "不得使用 MX-NONE"):
            project_prd_lib.validate_prd(
                simple_prd_text(), Path("订单系统") / "订单查询.md", self.root
            )

    def test_matrix_cannot_omit_rule_item_extracted_from_source(self) -> None:
        invalid = complex_prd_text().replace(
            "| MX-01 | FP-02 | state | `src/flow.py:step3` | 待处理<br>处理中<br>完成 | 待处理<br>处理中<br>完成 |",
            "| MX-01 | FP-02 | state | `src/flow.py:step3` | 待处理<br>处理中 | 待处理<br>处理中 |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "漏写源码证据中的规则项"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_every_source_rule_collection_requires_matrix_coverage(self) -> None:
        flow = self.root / "src" / "flow.py"
        flow.write_text(
            flow.read_text(encoding="utf-8").replace(
                "def step8(): return 8",
                "def step8():\n    modes = ('隐藏模式', '公开模式')\n    return modes",
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "未被任何 Matrix 覆盖"):
            project_prd_lib.validate_prd(
                complex_prd_text(), Path("流程管理") / "复杂流程.md", self.root
            )

    def test_unsupported_timeout_and_permission_claims_are_rejected(self) -> None:
        timeout_claim = simple_prd_text().replace(
            "| 网络异常：不适用 | 不适用：该能力无网络依赖 | 无展示 | `src/orders.py:find_order` |",
            "| 网络异常：等待超时 | 等待超时后返回失败 | 接口返回 | `src/orders.py:find_order` |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "超时声明缺少"):
            project_prd_lib.validate_prd(
                timeout_claim, Path("订单系统") / "订单查询.md", self.root
            )

        permission_claim = simple_prd_text().replace(
            "| 权限不足：不适用 | 不适用：当前入口无权限分支 | 无展示 | `src/orders.py:find_order` |",
            "| 权限不足：无查询权限 | 返回权限不足 | 接口返回 | `src/orders.py:find_order` |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "权限不足声明缺少"):
            project_prd_lib.validate_prd(
                permission_claim, Path("订单系统") / "订单查询.md", self.root
            )

    def test_unrelated_function_cannot_back_toast_claim_for_target_symbol(self) -> None:
        orders = self.root / "src" / "orders.py"
        orders.write_text(
            orders.read_text(encoding="utf-8")
            + "\ndef unrelated_ui():\n    return toast('unrelated')\n",
            encoding="utf-8",
        )
        invalid = simple_prd_text().replace(
            "| 操作失败：查询异常 | 向调用方返回失败 | 接口返回 | `src/orders.py:find_order` |",
            "| 操作失败：查询异常 | 向调用方返回失败 | Toast | `src/orders.py:find_order` |",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "源码证据没有 Toast 行为"):
            project_prd_lib.validate_prd(
                invalid, Path("订单系统") / "订单查询.md", self.root
            )

    def test_complex_flow_diagram_must_cover_every_feature_point(self) -> None:
        invalid = complex_prd_text().replace('  C --> D["FP-04 完成与清理"]\n', "")
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "流程图必须覆盖全部 Feature Point"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_mermaid_cannot_pack_multiple_feature_points_into_one_node(self) -> None:
        invalid = re.sub(
            r"(?ms)```mermaid\nflowchart TD\n.*?```",
            '```mermaid\nflowchart TD\n  X["FP-01 FP-02 FP-03 FP-04"] --> Y["完成"]\n```',
            complex_prd_text(),
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "每个节点只能表示一个"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_mermaid_feature_point_nodes_must_form_one_connected_flow(self) -> None:
        invalid = complex_prd_text().replace(
            '  C --> D["FP-04 完成与清理"]\n',
            '  X["独立入口"] --> D["FP-04 完成与清理"]\n',
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "同一连通业务闭环"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_decision_node_requires_two_labeled_outgoing_branches(self) -> None:
        invalid = shutdown_prd_text().replace(
            '  C -->|允许| D["FP-04 确认交互"]\n  C -->|拒绝| STOP["保持运行"]',
            '  C --> D["FP-04 确认交互"]\n  C --> STOP["保持运行"]',
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "两条不同条件标签的出边"):
            project_prd_lib.validate_prd(
                invalid, Path("电源与关机") / "关机流程.md", self.root
            )

    def test_decision_node_cannot_repeat_same_labeled_branch(self) -> None:
        invalid = shutdown_prd_text().replace(
            '  C -->|拒绝| STOP["保持运行"]',
            '  C -->|允许| D["FP-04 确认交互"]',
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "重复的边|不同条件标签"):
            project_prd_lib.validate_prd(
                invalid, Path("电源与关机") / "关机流程.md", self.root
            )

    def test_same_anchor_cannot_be_duplicated_across_feature_points(self) -> None:
        invalid = complex_prd_text().replace(
            "DC-02|stage|中间状态转换|src/flow.py:step3|FP-02",
            "DC-02|trigger|中间状态转换|src/flow.py:step1<br>src/flow.py:step2|FP-02",
        )
        with self.assertRaisesRegex(project_prd_lib.ProjectPrdError, "不得重复膨胀"):
            project_prd_lib.validate_prd(
                invalid, Path("流程管理") / "复杂流程.md", self.root
            )

    def test_shutdown_golden_regression_keeps_seven_feature_points_and_flow(self) -> None:
        metadata = project_prd_lib.validate_prd(
            shutdown_prd_text(), Path("电源与关机") / "关机流程.md", self.root
        )
        self.assertEqual(7, metadata["function_point_count"])
        self.assertEqual(7, metadata["candidate_count"])
        self.assertEqual(5, metadata["matrix_count"])
        self.assertEqual(1, metadata["diagram_count"])
        self.assertEqual(14, metadata["behavior_count"])
        self.assertNotIn("无信号", shutdown_prd_text())


if __name__ == "__main__":
    unittest.main()
