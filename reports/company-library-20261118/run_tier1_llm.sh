#!/bin/bash
# 对 Tier1 静态筛出的干净正例跑「带 LLM」的完整 Tier1（语义安全扫描开启）。
set -u
ROOT=/Users/yangyuhan/ai-agent-agent-skills
cd "$ROOT" || exit 1
STATUS="$ROOT/reports/company-library-20261118/tier1-llm-status.txt"
: > "$STATUS"

# 干净正例（--no-llm 下 overall=passed 且安全/PII 通过）
SKILLS="
G2/mr-suggestion
G4/grill-requirements
G4/requirement-analysis-pro
G4/requirement-spec
G4/requirements-analyst
G9/chrome-trace-analysis
G9/ios-crash-analysis
G9/third-party-sync-troubleshooting
"

run_one() {
  pair="$1"
  gid="${pair%%/*}"; name="${pair##*/}"
  out="$ROOT/reports/company-library-20261118/tier1-llm/$gid/$name"
  log="$ROOT/reports/company-library-20261118/tier1-llm-logs/$gid/$name.log"
  mkdir -p "$(dirname "$log")" "$out"
  docker compose run --rm skillevaluator tier1 "/skills/library-20261118/$gid/$name" \
    -r json,markdown -o "/app/reports/company-library-20261118/tier1-llm/$gid/$name" \
    > "$log" 2>&1
  rc=$?
  printf '%s\t%s\t%s\n' "$rc" "$gid" "$name" >> "$STATUS"
  return 0
}
export -f run_one
export ROOT STATUS

printf '%s\n' $SKILLS | sed '/^$/d' | xargs -n 1 -P 4 bash -c 'run_one "$0"'

echo "DONE $(date -u +%FT%TZ)"
