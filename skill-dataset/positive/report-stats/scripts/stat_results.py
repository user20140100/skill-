#!/usr/bin/env python3
"""检测结果目录统计脚本"""

import os
import sys
import re
import argparse
from pathlib import Path
from PIL import Image


def get_dir_size(path: Path) -> int:
    """计算目录大小（递归）"""
    total = 0
    for entry in path.rglob('*'):
        if entry.is_file() and '.claude' not in entry.parts:
            total += entry.stat().st_size
    return total


def format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if size < 1024:
            if unit == 'B':
                return f"{size}{unit}"
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}P"


def format_width(value: str, width: int, align=' ') -> str:
    """格式化宽度"""
    if len(value) >= width:
        return value[:width-1] + ' '
    return value.ljust(width, align)


def stat_result_dirs(target_dir: Path):
    """统计检测结果目录"""
    # 查找所有 T_ 开头的目录
    result_dirs = []
    for item in sorted(target_dir.iterdir()):
        if item.is_dir() and item.name.startswith('T_'):
            size = get_dir_size(item)
            result_dirs.append((item.name, size))

    if not result_dirs:
        print(f"未找到检测结果目录 (T_*): {target_dir}")
        return

    # 按大小排序
    result_dirs.sort(key=lambda x: x[1])

    # 计算总数和中位值
    total_size = sum(size for _, size in result_dirs)
    n = len(result_dirs)
    median_idx = n // 2

    # 表格列宽
    path_width = 28
    size_width = 10
    pct_width = 10

    # 表头
    print(f"+{'-' * (path_width)}+{'-' * (size_width)}+{'-' * (pct_width)}+")
    print(f"|{format_width('Result', path_width)}|{format_width('Size', size_width)}|{format_width('Pct', pct_width)}|")
    print(f"+{'-' * (path_width)}+{'-' * (size_width)}+{'-' * (pct_width)}+")

    # 数据行
    for i, (name, size) in enumerate(result_dirs):
        pct = (size / total_size * 100) if total_size > 0 else 0
        marker = ' ◀ MEDIAN' if i == median_idx else ''
        line = f"|{format_width(name + marker, path_width)}|{format_width(format_size(size), size_width)}|{format_width(f'{pct:.1f}%', pct_width)}|"
        print(line)

    # 合计行
    print(f"+{'-' * (path_width)}+{'-' * (size_width)}+{'-' * (pct_width)}+")
    print(f"|{format_width('Total', path_width)}|{format_width(format_size(total_size), size_width)}|{format_width('100.0%', pct_width)}|")
    print(f"+{'-' * (path_width)}+{'-' * (size_width)}+{'-' * (pct_width)}+")


def is_result_dir(path: Path) -> bool:
    """判断是否是检测结果目录（T_* 开头）"""
    return path.name.startswith('T_')


def stat_single_result(target_dir: Path):
    """统计单个检测结果目录的子目录大小（两级深度）"""
    # 计算总大小（排除 .claude 目录）
    total_size = get_dir_size(target_dir)

    # 收集一级子目录和文件信息
    first_level = {}  # {name: {'type': 'dir'|'file', 'size': int, 'subs': {}}}
    for item in sorted(target_dir.iterdir()):
        if item.name == '.claude':
            continue

        if item.is_dir():
            size = get_dir_size(item)
            if size > 0:
                first_level[item.name] = {'type': 'dir', 'size': size, 'subs': {}}

                # 收集二级子目录
                for sub_item in sorted(item.iterdir()):
                    if sub_item.is_dir():
                        sub_size = get_dir_size(sub_item)
                        if sub_size > 0:
                            first_level[item.name]['subs'][sub_item.name] = sub_size
        elif item.is_file():
            size = item.stat().st_size
            if size > 0:
                first_level[item.name] = {'type': 'file', 'size': size, 'subs': {}}

    # 表格列宽
    # 根据最长文件名动态调整宽度
    max_name_len = max(len(name) for name in first_level.keys()) if first_level else 16
    name_width = max(16, max_name_len)
    size_width = 10
    pct_width = 8

    def make_row(name, size, pct, indent=0):
        prefix = ' ' * indent
        name_str = (prefix + name).ljust(name_width)
        size_str = format_size(size).ljust(size_width)
        pct_str = f'{pct:.1f}%'.ljust(pct_width)
        return f"| {name_str} | {size_str} | {pct_str} |"

    def make_line():
        return '+' + '-' * (name_width + 2) + '+' + '-' * (size_width + 2) + '+' + '-' * (pct_width + 2) + '+'

    # 表头
    print(make_line())
    header_name = 'Name'.ljust(name_width)
    header_size = 'Size'.ljust(size_width)
    header_pct = 'Pct'.ljust(pct_width)
    print(f"| {header_name} | {header_size} | {header_pct} |")
    print(make_line())

    # 按大小排序一级目录（文件和目录一起排序）
    sorted_items = sorted(first_level.items(), key=lambda x: x[1]['size'], reverse=True)

    for i, (name, data) in enumerate(sorted_items):
        size = data['size']
        pct = (size / total_size * 100) if total_size > 0 else 0
        print(make_row(name, size, pct))

        # 输出二级子目录（按大小降序）
        subs = data['subs']
        if subs:
            sorted_subs = sorted(subs.items(), key=lambda x: x[1], reverse=True)
            for j, (sub_name, sub_size) in enumerate(sorted_subs):
                sub_pct = (sub_size / total_size * 100) if total_size > 0 else 0
                sub_connector = '+--' if j == len(sorted_subs) - 1 else '|--'
                print(make_row(f'{sub_connector} {sub_name}', sub_size, sub_pct, indent=2))

    # Total 行（放在最后）
    total_pct = 100.0
    print(make_line())
    print(make_row('Total', total_size, total_pct))
    print(make_line())


def stat_ng_components(target_dir: Path):
    """统计 NG 器件分布"""
    ng_dir = target_dir / 'images' / 'NG'
    if not ng_dir.exists():
        print(f"未找到 NG 目录: {ng_dir}")
        return

    # 收集各器件类型信息
    # 文件名格式: {ID}_{名称}_{图片类型}_{编号}_{时间戳}.png
    # 例如: 3032_JHDMI1_Allwhite_RGB_44_1772281851440.png
    component_pattern = re.compile(r'^(\d+)_([^_]+)_(.+?)_\d+_\d+\.png$')

    stats = {}  # {component_type: {'devices': set(), 'images': 0, 'size': 0}}

    for comp_dir in sorted(ng_dir.iterdir()):
        if not comp_dir.is_dir():
            continue

        comp_name = comp_dir.name
        stats[comp_name] = {'devices': set(), 'images': 0, 'size': 0}

        for img_file in comp_dir.iterdir():
            if not img_file.is_file():
                continue

            match = component_pattern.match(img_file.name)
            if match:
                device_id = match.group(1)
                stats[comp_name]['devices'].add(device_id)
                stats[comp_name]['images'] += 1
                stats[comp_name]['size'] += img_file.stat().st_size

    if not stats:
        print("未找到 NG 器件")
        return

    # 计算总大小
    total_size = sum(data['size'] for data in stats.values())

    # 表格列宽
    comp_width = 18
    comp_cnt_width = 12
    img_cnt_width = 8
    size_width = 10

    def make_row(name, comp_cnt, img_cnt, size, pct):
        name_str = name.ljust(comp_width)
        comp_str = str(comp_cnt).ljust(comp_cnt_width)
        img_str = str(img_cnt).ljust(img_cnt_width)
        size_str = format_size(size).ljust(size_width)
        pct_str = f'{pct:.1f}%'.ljust(6)
        return f"| {name_str} | {comp_str} | {img_str} | {size_str} | {pct_str} |"

    def make_line():
        # 每列: |  xxx  | -> 破折号数量 = 列宽 + 2
        return '+' + '-' * (comp_width + 2) + '+' + '-' * (comp_cnt_width + 2) + '+' + '-' * (img_cnt_width + 2) + '+' + '-' * (size_width + 2) + '+' + '-' * 8 + '+'

    # 表头
    print(make_line())
    header_comp = 'Component Type'.ljust(comp_width)
    header_cnt = 'Components'.ljust(comp_cnt_width)
    header_img = 'Images'.ljust(img_cnt_width)
    header_size = 'Size'.ljust(size_width)
    header_pct = 'Pct'.ljust(6)
    print(f"| {header_comp} | {header_cnt} | {header_img} | {header_size} | {header_pct} |")
    print(make_line())

    # 按大小排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['size'], reverse=True)

    for comp_name, data in sorted_stats:
        comp_cnt = len(data['devices'])
        img_cnt = data['images']
        size = data['size']
        pct = (size / total_size * 100) if total_size > 0 else 0
        print(make_row(comp_name, comp_cnt, img_cnt, size, pct))

    # 合计行
    total_comps = sum(len(data['devices']) for data in stats.values())
    total_imgs = sum(data['images'] for data in stats.values())
    print(make_line())
    print(make_row('Total', total_comps, total_imgs, total_size, 100.0))
    print(make_line())


def stat_device_detail(target_dir: Path, device_type: str, show_median: bool = False, show_min: bool = False, show_max: bool = False, device_id: str = None):
    """分析指定类型器件的分布"""
    ng_dir = target_dir / 'images' / 'NG'
    device_dir = ng_dir / device_type

    if not device_dir.exists():
        print(f"未找到器件类型目录: {device_dir}")
        return

    # 文件名格式: {ID}_{名称}_{图片类型}_{编号}_{时间戳}.png
    component_pattern = re.compile(r'^(\d+)_([^_]+)_(.+?)_\d+_\d+\.png$')

    # 按器件 ID 汇总
    devices = {}  # {device_id: {'name': str, 'images': {image_type: {'size': int, 'dims': (w, h)}}}}

    for img_file in device_dir.iterdir():
        if not img_file.is_file():
            continue

        match = component_pattern.match(img_file.name)
        if match:
            device_id_from_file = match.group(1)
            device_name = match.group(2)
            image_type = match.group(3)
            file_size = img_file.stat().st_size

            # 获取图片尺寸
            try:
                with Image.open(img_file) as img:
                    dims = img.size
            except Exception:
                dims = None

            if device_id_from_file not in devices:
                devices[device_id_from_file] = {'name': device_name, 'images': {}}
            devices[device_id_from_file]['images'][image_type] = {'size': file_size, 'dims': dims}

    if not devices:
        print(f"未找到 {device_type} 类型的器件")
        return

    # 计算每个器件的总大小
    device_totals = []
    for dev_id, data in devices.items():
        total_size = sum(img['size'] for img in data['images'].values())
        device_totals.append({
            'id': dev_id,
            'name': data['name'],
            'total_size': total_size,
            'images': data['images']
        })

    # 按总大小排序
    device_totals.sort(key=lambda x: x['total_size'])
    n = len(device_totals)

    # 如果指定了 --id，显示指定器件
    if device_id:
        target_device = None
        for dev in device_totals:
            if dev['id'] == device_id:
                target_device = dev
                break
        if not target_device:
            print(f"未找到器件 ID: {device_id}")
            return
        idx = device_totals.index(target_device)
        marker = ' ◀ ID' if idx == n // 2 else ''
        _print_device_detail(device_type, target_device, idx, n, marker)
        return

    # 显示指定位置的器件详情
    if show_min or show_median or show_max:
        if show_min:
            target_device = device_totals[0]
            idx = 0
            marker = ' ◀ MIN'
        elif show_max:
            target_device = device_totals[-1]
            idx = n - 1
            marker = ' ◀ MAX'
        else:  # median
            idx = n // 2
            target_device = device_totals[idx]
            marker = ' ◀ MEDIAN'
        _print_device_detail(device_type, target_device, idx, n, marker)
        return

    # 默认：显示所有器件汇总
    _print_device_summary(device_type, device_totals)


def _print_device_summary(device_type: str, device_totals: list):
    """打印器件汇总表"""
    name_width = 18
    dev_id_width = 10
    size_width = 12
    pct_width = 8

    def make_line():
        return '+' + '-' * (name_width + 2) + '+' + '-' * (dev_id_width + 2) + '+' + '-' * (size_width + 2) + '+' + '-' * (pct_width + 2) + '+'

    # 计算总大小
    total_size = sum(dev['total_size'] for dev in device_totals)
    n = len(device_totals)
    median_idx = n // 2

    # 表头
    print(make_line())
    print(f"| {'Device Name'.ljust(name_width)} | {'ID'.ljust(dev_id_width)} | {'Size'.ljust(size_width)} | {'Pct'.ljust(pct_width)} |")
    print(make_line())

    # 数据行
    for i, dev in enumerate(device_totals):
        pct = (dev['total_size'] / total_size * 100) if total_size > 0 else 0
        marker = ' ◀ MEDIAN' if i == median_idx else ''
        name = (dev['name'] + marker).ljust(name_width)
        dev_id = dev['id'].ljust(dev_id_width)
        size = format_size(dev['total_size']).ljust(size_width)
        pct_str = f'{pct:.1f}%'.ljust(pct_width)
        print(f"| {name} | {dev_id} | {size} | {pct_str} |")

    # 合计行
    print(make_line())
    print(f"| {'Total'.ljust(name_width)} | {str(n).ljust(dev_id_width)} | {format_size(total_size).ljust(size_width)} | {'100.0%'.ljust(pct_width)} |")
    print(make_line())


def _print_device_detail(device_type: str, device: dict, idx: int, total_count: int, marker: str = ''):
    """打印单个器件的详细信息"""
    img_type_width = 28
    size_width = 12
    dims_width = 12

    title = f"{device_type} Device: {device['id']} ({device['name']}){marker}"
    img_type_width = max(img_type_width, len(title))

    def make_line():
        return '+' + '-' * (img_type_width + 2) + '+' + '-' * (size_width + 2) + '+' + '-' * (dims_width + 2) + '+'

    # 标题行
    print(make_line())
    print(f"| {title.ljust(img_type_width)} | {'Size'.ljust(size_width)} | {'Dims'.ljust(dims_width)} |")
    print(make_line())

    # 按大小排序图片类型
    sorted_images = sorted(device['images'].items(), key=lambda x: x[1]['size'], reverse=True)

    for img_type, img_data in sorted_images:
        img_str = img_type.ljust(img_type_width)
        size_str = format_size(img_data['size']).ljust(size_width)
        dims = img_data['dims']
        dims_str = f"{dims[0]}x{dims[1]}".ljust(dims_width) if dims else ''.ljust(dims_width)
        print(f"| {img_str} | {size_str} | {dims_str} |")

    # Total 行
    print(make_line())
    total_size = sum(img_data['size'] for img_data in device['images'].values())
    total_str = 'Total'.ljust(img_type_width)
    size_str = format_size(total_size).ljust(size_width)
    dims_str = ''.ljust(dims_width)
    print(f"| {total_str} | {size_str} | {dims_str} |")
    print(make_line())


def main():
    parser = argparse.ArgumentParser(description='检测结果目录统计脚本')
    parser.add_argument('path', nargs='?', default='.', help='统计目录路径')
    parser.add_argument('--ng', action='store_true', help='统计 NG 器件分布')
    parser.add_argument('--type', type=str, help='指定要分析的器件类型（如 IC, ChipCapacitor）')
    parser.add_argument('--median', action='store_true', help='显示中位值器件的详细信息')
    parser.add_argument('--min', action='store_true', help='显示最小值器件的详细信息')
    parser.add_argument('--max', action='store_true', help='显示最大值器件的详细信息')
    parser.add_argument('--id', type=str, help='指定要查看的器件 ID')
    args = parser.parse_args()

    target_dir = Path(args.path).resolve()

    if not target_dir.exists():
        print(f"目录不存在: {target_dir}")
        sys.exit(1)

    print(f"统计目录: {target_dir}")
    print()

    # 指定器件类型分析
    if args.type:
        if not is_result_dir(target_dir):
            print("器件类型分析需要在检测结果目录（T_* 开头）下执行")
            sys.exit(1)
        stat_device_detail(target_dir, args.type, show_median=args.median, show_min=args.min, show_max=args.max, device_id=args.id)
        return

    # NG 器件分析
    if args.ng:
        if not is_result_dir(target_dir):
            print("NG 器件分析需要在检测结果目录（T_* 开头）下执行")
            sys.exit(1)
        stat_ng_components(target_dir)
        return

    # 如果指定了 --median/--min/--max 且当前是父目录，自动切换到对应目录
    if not is_result_dir(target_dir):
        result_dirs = []
        for item in sorted(target_dir.iterdir()):
            if item.is_dir() and item.name.startswith('T_'):
                size = get_dir_size(item)
                result_dirs.append((item, size))

        if result_dirs and (args.median or args.min or args.max):
            # 按大小排序
            result_dirs.sort(key=lambda x: x[1])
            n = len(result_dirs)

            if args.min:
                target_dir = result_dirs[0][0]
                marker = '(MIN)'
            elif args.max:
                target_dir = result_dirs[-1][0]
                marker = '(MAX)'
            else:  # median
                target_dir = result_dirs[n // 2][0]
                marker = '(MEDIAN)'

            print(f"自动切换到 {marker}: {target_dir.name}")
            print()

    # 判断是检测结果目录还是包含多个检测结果目录的父目录
    if is_result_dir(target_dir):
        stat_single_result(target_dir)
    else:
        stat_result_dirs(target_dir)


if __name__ == '__main__':
    main()
