#!/bin/bash
# 对 G4 需求组 4 个重叠 skill 跑完整 Tier3（3 用例 × 双 arm），2 路并行。
set -u
ROOT=/Users/yangyuhan/ai-agent-agent-skills
cd "$ROOT" || exit 1
STATUS="$ROOT/reports/company-library-20261118/tier3-v2-status.txt"
: > "$STATUS"

SKILLS="
G4/requirement-spec
G4/requirements-analyst
G4/grill-requirements
G4/requirement-analysis-pro
"

run_one() {
  pair="$1"
  gid="${pair%%/*}"; name="${pair##*/}"
  log="$ROOT/reports/company-library-20261118/tier3-v2-logs/$name.log"
  mkdir -p "$(dirname "$log")"
  docker compose run --rm skillevaluator tier3 "/skills/library-20261118/$gid/$name" \
    --agents opencode --model openai/qwen3.8-flash --timeout-multiplier 3 \
    --results-dir "/app/reports/company-library-20261118/tier3-v2/$name" \
    > "$log" 2>&1
  rc=$?
  printf '%s\t%s\t%s\n' "$rc" "$gid" "$name" >> "$STATUS"
  return 0
}
export -f run_one
export ROOT STATUS

printf '%s\n' $SKILLS | sed '/^$/d' | xargs -n 1 -P 2 bash -c 'run_one "$0"'

echo "DONE $(date -u +%FT%TZ)"
