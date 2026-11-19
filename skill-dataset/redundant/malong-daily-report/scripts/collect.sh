#!/usr/bin/env bash
# collect.sh — 码龙日报数据采集主编排
#
# 采集飞书日历/聊天/文档 + 当日 git 提交 + Claude Code 开发活动，
# 输出分段 markdown 素材到 stdout（供 Claude 过滤闲聊后总结为日报）。
#
# 设计原则：
#   - 每个数据源独立容错，单源失败不影响其他源
#   - 只读采集，不缓存任何 token/密钥
#   - 兼容 macOS 自带 bash 3.2（避免 mapfile / 关联数组）
#
# 用法:
#   bash collect.sh                              # 默认今天
#   bash collect.sh --date 2026-06-16
#   bash collect.sh --date yesterday --no-code   # 仅飞书源
#   bash collect.sh --no-lark                    # 离线：仅代码/开发源

set -u

DATE_ARG="today"
ME=""
NO_LARK=0
NO_CODE=0
TZ_OFFSET="+08:00"   # 飞书消息 ISO 时间用的时区偏移；跨时区可改

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE_ARG="$2"; shift 2 ;;
    --date=*) DATE_ARG="${1#*=}"; shift ;;
    --me) ME="$2"; shift 2 ;;
    --me=*) ME="${1#*=}"; shift ;;
    --no-lark) NO_LARK=1; shift ;;
    --no-code) NO_CODE=1; shift ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "未知参数: $1（忽略）" >&2; shift ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 会议 JSON 临时文件（供精力看板去重），退出时清理
MEETINGS_JSON="$(mktemp 2>/dev/null || echo "/tmp/malong_meetings_$$.json")"
trap 'rm -f "$MEETINGS_JSON"' EXIT

# ---- 日期解析（用 python3，跨平台；输出 D / D2=次日）----
PYDATE=$(python3 - "$DATE_ARG" <<'PY'
import sys
from datetime import datetime, timedelta
s = sys.argv[1]
today = datetime.now().date()
if s == "today":
    d = today
elif s == "yesterday":
    d = today - timedelta(days=1)
else:
    d = datetime.strptime(s, "%Y-%m-%d").date()
print(d.strftime("%Y-%m-%d"), (d + timedelta(days=1)).strftime("%Y-%m-%d"))
PY
)
read -r D D2 <<< "$PYDATE"
ISO_START="${D}T00:00:00${TZ_OFFSET}"
ISO_END="${D}T23:59:59${TZ_OFFSET}"

echo "# 码龙日报素材 · ${D}"
echo
echo "> 采集于 $(date '+%Y-%m-%d %H:%M:%S')"
echo

# ---- 获取我的 open_id（用于聊天筛选）----
if [[ -z "$ME" ]]; then
  ME=$(lark-cli auth status --verify 2>/dev/null \
       | python3 -c "import sys,json;print(json.load(sys.stdin)['identities']['user']['openId'])" 2>/dev/null || true)
fi

emit() { echo "## $1"; echo; }

# ======================= 飞书源 =======================
if [[ "$NO_LARK" -ne 1 ]]; then

  emit "今日会议（飞书日历）"
  # 采 JSON 供精力看板与会议去重；同时 pretty 展示会议标题
  lark-cli calendar +agenda --as user --start "${D}" --end "${D}" --format json > "$MEETINGS_JSON" 2>/dev/null || true
  ( lark-cli calendar +agenda --as user --start "${D}" --end "${D}" --format pretty 2>&1 \
      | grep -vE 'applink|message_position' | head -80 ) || echo "（日历采集失败或无日程）"
  echo

  emit "我发出的消息（飞书聊天）"
  if [[ -n "$ME" ]]; then
    ( lark-cli im +messages-search --query '' --sender "${ME}" \
        --start "${ISO_START}" --end "${ISO_END}" --page-size 50 --page-all --format pretty 2>&1 \
        | grep -vE 'applink|message_position' | head -160 ) || echo "（聊天采集失败）"
  else
    echo "（未获取到 open_id，跳过本段；可用 --me 指定）"
  fi
  echo

  emit "@我的消息（飞书聊天）"
  ( lark-cli im +messages-search --query '' --is-at-me \
      --start "${ISO_START}" --end "${ISO_END}" --page-size 50 --format pretty 2>&1 \
      | grep -vE 'applink|message_position' | head -100 ) || echo "（@我消息采集失败）"
  echo

  emit "今日编辑的文档（飞书云空间）"
  ( lark-cli drive +search --mine --edited-since "${D}" --edited-until "${D2}" --format pretty 2>&1 \
      | head -60 ) || echo "（文档-编辑采集失败）"
  echo

  emit "今日创建的文档（飞书云空间）"
  ( lark-cli drive +search --created-by-me --created-since "${D}" --created-until "${D2}" --format pretty 2>&1 \
      | head -60 ) || echo "（文档-创建采集失败）"
  echo

fi

# ======================= 代码与开发源 =======================
if [[ "$NO_CODE" -ne 1 ]]; then

  emit "代码与开发（Claude Code 会话 + Git 提交）"

  # 1) Claude Code 会话活动 + 会议去重精力看板
  MFLAG=""
  [[ -s "$MEETINGS_JSON" ]] && MFLAG="--meetings-json $MEETINGS_JSON"
  CS_OUT=$(python3 "${SCRIPT_DIR}/claude_sessions.py" --date "${D}" $MFLAG 2>&1 || true)
  echo "$CS_OUT" | grep -v '^@@ACTIVE_DIRS@@'
  echo

  # 2) 对活跃项目目录跑 git log
  ACTIVE_DIRS=$(echo "$CS_OUT" | awk -F'\t' '/^@@ACTIVE_DIRS@@/{for(i=2;i<=NF;i++) print $i}')
  if [[ -n "$ACTIVE_DIRS" ]]; then
    echo "### 当日 Git 提交"
    echo
    while IFS= read -r d; do
      [[ -z "$d" ]] && continue
      if git -C "$d" rev-parse --git-dir >/dev/null 2>&1; then
        LOG=$(git -C "$d" log --all --since="${D} 00:00" --until="${D} 23:59" \
              --pretty=format:"- %h %an: %s" 2>/dev/null | head -30)
        if [[ -n "$LOG" ]]; then
          echo "- **${d}**"
          echo "$LOG"
          echo
        fi
      fi
    done <<< "$ACTIVE_DIRS"
  fi
  echo

fi

echo "---"
echo "素材采集完成。下一步：过滤闲聊/私人内容，按主题（项目推进/会议/答疑/文档/开发/线下支持）归类，"
echo "生成简洁工作日报，写入 ~/.dailylog/${D}-工作日报.md 并上传飞书个人空间。"
