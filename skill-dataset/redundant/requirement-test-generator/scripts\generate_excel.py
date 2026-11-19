#!/usr/bin/env python3
"""
Requirement Test Case Generator - Excel Output Script
Usage: python generate_excel.py <json_file> [output_file]
"""

import json
import sys
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from datetime import datetime
from pathlib import Path


def create_test_case_excel(test_cases: list, output_path: str = None, summary: dict = None, coverage: list = None):
    """
    Generate Excel file from test case data.

    Args:
        test_cases: List of test case dictionaries
        output_path: Output file path (optional)
        summary: Summary statistics dict (optional)
        coverage: Coverage data list (optional)

    Returns:
        Generated file path
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "测试用例"

    # Styles
    header_font_white = Font(bold=True, size=11, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    wrap_alignment = Alignment(wrap_text=True, vertical='top')

    # Headers for test cases sheet
    headers = ["用例ID", "功能模块", "用例标题", "优先级", "前置条件", "测试步骤", "输入条件", "预期输出", "测试类型", "关联需求", "备注"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Write test cases
    for row_idx, tc in enumerate(test_cases, 2):
        values = [
            tc.get("id", ""),
            tc.get("module", ""),
            tc.get("title", ""),
            tc.get("priority", ""),
            tc.get("precondition", ""),
            tc.get("steps", ""),
            tc.get("input", ""),
            tc.get("expected", ""),
            tc.get("type", ""),
            tc.get("requirement", ""),
            tc.get("note", "")
        ]
        for col_idx, value in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
            cell.alignment = wrap_alignment

    # Set column widths
    column_widths = [10, 12, 45, 8, 30, 45, 25, 45, 12, 15, 20]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    # Create summary sheet
    ws2 = wb.create_sheet("统计汇总")

    if summary:
        summary_data = [
            ["统计项", "数量"],
            ["总用例数", summary.get("total", len(test_cases))],
            ["", ""],
            ["按优先级统计", ""],
            ["P0 (阻塞)", summary.get("p0", 0)],
            ["P1 (严重)", summary.get("p1", 0)],
            ["P2 (一般)", summary.get("p2", 0)],
            ["P3 (建议)", summary.get("p3", 0)],
            ["", ""],
            ["按测试类型统计", ""],
            ["正向", summary.get("positive", 0)],
            ["逆向", summary.get("negative", 0)],
            ["边界", summary.get("boundary", 0)],
            ["异常", summary.get("exception", 0)],
            ["状态转换", summary.get("transition", 0)],
            ["组合", summary.get("combination", 0)],
        ]
    else:
        # Auto-calculate summary
        summary_data = [
            ["统计项", "数量"],
            ["总用例数", len(test_cases)],
            ["", ""],
            ["按优先级统计", ""],
            ["P0 (阻塞)", sum(1 for tc in test_cases if tc.get("priority") == "P0")],
            ["P1 (严重)", sum(1 for tc in test_cases if tc.get("priority") == "P1")],
            ["P2 (一般)", sum(1 for tc in test_cases if tc.get("priority") == "P2")],
            ["P3 (建议)", sum(1 for tc in test_cases if tc.get("priority") == "P3")],
            ["", ""],
            ["按测试类型统计", ""],
            ["正向", sum(1 for tc in test_cases if tc.get("type") == "正向")],
            ["逆向", sum(1 for tc in test_cases if tc.get("type") == "逆向")],
            ["边界", sum(1 for tc in test_cases if tc.get("type") == "边界")],
            ["异常", sum(1 for tc in test_cases if tc.get("type") == "异常")],
            ["状态转换", sum(1 for tc in test_cases if tc.get("type") == "状态转换")],
            ["组合", sum(1 for tc in test_cases if tc.get("type") == "组合")],
        ]

    for row_idx, row_data in enumerate(summary_data, 1):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws2.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
            if row_idx == 1 or row_data[1] == "":
                cell.font = Font(bold=True)

    ws2.column_dimensions['A'].width = 20
    ws2.column_dimensions['B'].width = 15

    # Create coverage sheet
    ws3 = wb.create_sheet("功能覆盖")

    if coverage:
        for row_idx, row_data in enumerate(coverage, 1):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws3.cell(row=row_idx, column=col_idx, value=value)
                cell.border = thin_border
                if row_idx == 1:
                    cell.font = header_font_white
                    cell.fill = header_fill

        ws3.column_dimensions['A'].width = 35
        ws3.column_dimensions['B'].width = 25
        ws3.column_dimensions['C'].width = 15

    # Generate output path if not provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"test_cases_{timestamp}.xlsx"

    wb.save(output_path)
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_excel.py <json_file> [output_file]")
        print("  json_file: Path to JSON file containing test cases")
        print("  output_file: Optional output Excel file path")
        print("\nJSON format:")
        print('{"test_cases": [...], "summary": {...}, "coverage": [...]}')
        sys.exit(1)

    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_cases = data.get("test_cases", [])
    summary = data.get("summary")
    coverage = data.get("coverage")

    output_path = create_test_case_excel(test_cases, output_file, summary, coverage)
    print(f"Excel file generated: {output_path}")
    print(f"Total test cases: {len(test_cases)}")


if __name__ == "__main__":
    main()
