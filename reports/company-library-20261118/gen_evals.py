#!/usr/bin/env python3
"""为 G4 需求组 4 个重叠 skill 生成「共用」的 Tier3 评测用例（agentskills.io 格式）。

公平性设计（有无 skill 必须同输入、同单轮）：
1. 四个 skill 共用完全相同的 prompt / expected_output / assertions，仅 skill_name /
   expected_skill 随 skill 变化；prompt 不提及任何 skill 用法。
2. 每条用例「任务方向明确」：直接下达"请根据以下信息输出需求文档"，并把完成任务所需的
   全部信息一次性写进 prompt，使单轮执行即可产出交付物。
3. 不采用"预填答案式模拟对话"、也不在 opencode 反问时注入额外输入——输入固定，两个
   arm（with-skill / baseline）拿到的 prompt 逐字节相同。
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("/Users/yangyuhan/ai-agent-agent-skills")
BASE = ROOT / "skill-dataset/library-20261118"

# (目录名, skill 名)
SKILLS = [
    ("G4/requirement-spec", "requirement-spec"),
    ("G4/requirements-analyst", "requirements-analyst"),
    ("G4/grill-requirements", "grill-requirements"),
    ("G4/requirement-analysis-pro", "requirement-analysis-pro"),
]

# 3 条共用用例：2 正例（新功能 / 改造）+ 1 负向控制（无关请求）。
# 正例：完整信息预置在 prompt 中，明确"请直接输出需求文档"，单轮可完成。
CASES = [
    {
        "id": "req-001",
        "expected_skill": None,  # 运行时按 skill 填入
        "expected_script": None,
        "prompt": (
            "请根据以下信息，直接输出一份规范、完整的需求文档（Markdown 格式）。\n\n"
            "【需求背景】公司内部系统要新增「加班申请」功能，替换现在线下填纸表、微信找领导签字的方式，"
            "便于留痕和 HR 统计。\n"
            "【使用角色】员工（提交申请）、部门主管（审批）、HR（月度汇总）。\n"
            "【填写内容】加班日期、开始时间、结束时间、加班事由（选填，不超过 200 字）；"
            "加班时长由系统按起止时间自动计算。\n"
            "【审批流程】员工提交 → 部门主管审批（同意/驳回，驳回需填写原因）；"
            "加班时长超过 4 小时时，需部门总监额外审批；法定节假日加班自动标记。\n"
            "【权限】员工仅可查看/修改自己的申请；部门主管仅可查看/审批本部门申请；"
            "HR 可查看全公司但不可修改。\n"
            "【列表与查询】员工端列表显示日期、时长、状态（待审批/已通过/已驳回），"
            "支持按状态、按月份筛选；HR 端支持按月导出汇总。\n\n"
            "请直接输出完整的需求文档。"
        ),
        "expected_output": (
            "The agent produced a complete, structured Markdown requirement document for the "
            "overtime-request feature. It covered: background/pain point, users and roles "
            "(employee, manager, HR), data fields (with auto-calculated duration), the approval "
            "flow (including the >4-hour escalation to the director and the holiday flag), "
            "permissions (employee/manager/HR at three levels), list & query (filters plus "
            "monthly export), and acceptance criteria."
        ),
        "assertions": [
            "The agent produced a structured Markdown requirement document with section headings, not a chat-style reply or a list of questions",
            "The document covers the data fields (date, start/end time, duration, reason) and the auto-calculated duration rule",
            "The document covers the approval flow including the >4-hour escalation to the director",
            "The document states permissions for employee/manager/HR at three levels",
            "The document covers list & query (filters, monthly export)",
            "The document includes acceptance criteria or a checklist",
        ],
    },
    {
        "id": "req-002",
        "expected_skill": None,
        "expected_script": None,
        "prompt": (
            "请根据以下信息，直接输出一份规范、完整的需求文档（Markdown 格式）。\n\n"
            "【改造对象】公司已有的「报销申请」功能。\n"
            "【现状问题】一张报销单只能填一种费用类型；领导审批时看不到发票照片。\n"
            "【改造目标】(1) 一张单可填多种费用（如打车费、餐费、住宿费分列）；"
            "(2) 审批时能看到发票照片；(3) 财务支持导出。\n"
            "【历史数据】已有历史报销单需能继续查看，不影响本次改造。\n"
            "【使用角色】员工（提交）、部门主管（审批）、财务（导出）。\n\n"
            "请直接输出完整的改造需求文档。"
        ),
        "expected_output": (
            "The agent produced a complete, structured Markdown requirement document for modifying "
            "the expense-reimbursement feature. It covered: the current limitation (single expense "
            "type per form, no invoice photo in approval), the requested changes (multiple expense "
            "types, invoice photos during approval, finance export), how legacy data should be "
            "handled, the users/roles, and acceptance criteria."
        ),
        "assertions": [
            "The agent produced a structured Markdown requirement document with section headings",
            "The document covers the change from single to multiple expense types per form",
            "The document covers showing invoice photos during approval",
            "The document covers finance export as a new capability",
            "The document addresses how legacy/historical data is handled",
            "The document includes acceptance criteria or a checklist",
        ],
    },
    {
        "id": "req-003",
        "expected_skill": None,
        "expected_script": None,
        "prompt": "写一个 Python 脚本，读取 CSV 文件并统计每一列的非空值数量。",
        "expected_output": (
            "The agent answered the programming question directly by writing a Python script that "
            "reads a CSV and counts non-null values per column, without activating or referencing "
            "any requirement-analysis skill."
        ),
        "assertions": [
            "The agent wrote a Python script using csv/pandas to count non-null values per column",
            "The agent did NOT activate or reference any requirement-document skill",
            "The agent did not produce a requirement document",
        ],
    },
]

CONFIG = {
    "schema_version": 1,
    "harbor": {"base_image_mode": "reuse", "n_attempts": 1},
}


def main() -> None:
    for rel, skill_name in SKILLS:
        evals_dir = BASE / rel / "evals"
        evals_dir.mkdir(parents=True, exist_ok=True)

        cases = []
        for c in CASES:
            c = dict(c)
            # 负向控制用例保持 expected_skill=null；正例指向本 skill
            c["expected_skill"] = skill_name if c["id"] != "req-003" else None
            cases.append(c)

        payload = {"skill_name": skill_name, "evals": cases}
        (evals_dir / "evals.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (evals_dir / "config.yml").write_text(
            "schema_version: 1\nharbor:\n  base_image_mode: reuse\n  n_attempts: 1\n",
            encoding="utf-8",
        )
        print(f"wrote {rel}/evals/evals.json + config.yml")


if __name__ == "__main__":
    main()
