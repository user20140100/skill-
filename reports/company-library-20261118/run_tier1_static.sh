#!/bin/bash
# Run static Tier 1 (--no-llm) for the selected company-library skill groups.
set -u
ROOT=/Users/yangyuhan/ai-agent-agent-skills
cd "$ROOT" || exit 1
STATUS="$ROOT/reports/company-library-20261118/tier1-status.txt"
: > "$STATUS"

run_one() {
  gid="$1"; name="$2"
  out="$ROOT/reports/company-library-20261118/tier1/$gid/$name"
  log="$ROOT/reports/company-library-20261118/tier1-logs/$gid/$name.log"
  mkdir -p "$(dirname "$log")" "$out"
  docker compose run --rm skillevaluator tier1 "/skills/library-20261118/$gid/$name" \
    --no-llm -r json,markdown -o "/app/reports/company-library-20261118/tier1/$gid/$name" \
    > "$log" 2>&1
  rc=$?
  printf '%s\t%s\t%s\n' "$rc" "$gid" "$name" >> "$STATUS"
  return 0
}
export -f run_one
export ROOT STATUS

for gid in G2 G4 G9; do
  for d in "$ROOT/skill-dataset/library-20261118/$gid"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    printf '%s %s\n' "$gid" "$name"
  done
done | xargs -n 2 -P 4 bash -c 'run_one "$0" "$1"'

echo "DONE $(date -u +%FT%TZ)"
