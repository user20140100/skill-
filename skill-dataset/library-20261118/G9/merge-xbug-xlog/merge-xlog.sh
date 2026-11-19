#!/bin/bash
#
# merge-xlog.sh - 解压并合并 xlog 压缩日志文件
# Usage: bash merge-xlog.sh "/path/to/xlog/directory"
#

set -e

TARGET_DIR="$1"

# 如果没有提供目录参数，拒绝执行
if [ -z "$TARGET_DIR" ]; then
  echo "❌ 错误: 缺少目录参数"
  echo ""
  echo "用法: bash merge-xlog.sh \"/path/to/xlog/directory\""
  echo ""
  echo "示例:"
  echo "  bash merge-xlog.sh \"/Users/robinyeung/Downloads/2008/FS/data/misc/xlog/5_2026-04-09_200649\""
  echo ""
  exit 1
fi

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ 错误: 目录不存在: $TARGET_DIR"
  exit 1
fi

cd "$TARGET_DIR"

# 获取目录名作为输出文件名
DIR_NAME=$(basename "$TARGET_DIR")
OUTPUT_FILE="${DIR_NAME}.log"

# 检查是否存在 .gz 文件
if ! ls log_*.gz >/dev/null 2>&1; then
  echo "⚠️  警告: 目录中没有 log_*.gz 文件"
  exit 1
fi

echo "📦 目录: $TARGET_DIR"
echo "📝 输出文件: $OUTPUT_FILE"

# 第一步：解压所有 .gz 文件（保留原文件）
echo "🔍 正在解压..."
gz_count=0
for f in log_*.gz; do
  if [ -f "$f" ]; then
    gunzip -k "$f" 2>/dev/null || true
    ((gz_count++))
  fi
done
echo "✓ 解压完成 ($gz_count files)"

# 第二步：按数字顺序合并
echo "🔗 正在合并..."
(for i in {0..9}; do
  if [ -f "log_$i" ]; then
    cat "log_$i"
  fi
done) > "$OUTPUT_FILE"

# 第三步：验证结果
log_count=$(ls -1 log_[0-9] 2>/dev/null | wc -l)
line_count=$(wc -l < "$OUTPUT_FILE")
file_size=$(du -h "$OUTPUT_FILE" | awk '{print $1}')

echo "✓ 合并完成"

# 第四步：清理中间产物
echo "🧹 正在清理中间产物..."
rm -f log_[0-9]
echo "✓ 清理完成"

echo ""
echo "📊 统计信息:"
echo "  原始文件数:   $log_count"
echo "  合并后行数:   $line_count"
echo "  合并文件大小: $file_size"
echo "  输出文件:     $OUTPUT_FILE"
echo ""
echo "✅ 完成!"
