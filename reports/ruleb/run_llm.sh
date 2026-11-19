#!/bin/bash
# 对 5 个边界样本 skill 跑「含 LLM 完整扫描」两轮对照（挂 B vs 不挂 B）
set -u
cd /Users/yangyuhan/ai-agent-agent-skills || exit 1

run() {
  local s="$1" mode="$2"
  local out="reports/ruleb/$s.llm.$mode.json"
  local err="reports/ruleb/$s.llm.$mode.stderr"
  if [ "$mode" = "withb" ]; then
    docker compose run --rm skillspector scan "/scan/ruleb-range/$s" \
      --yara-rules-dir /custom-rules/staged --format json > "$out" 2> "$err"
  else
    docker compose run --rm skillspector scan "/scan/ruleb-range/$s" \
      --format json > "$out" 2> "$err"
  fi
  local rc=$?
  echo "[$(date +%T)] DONE $s $mode rc=$rc"
  return 0
}

# gitlab-api 的 baseline 已单独跑过（smoke test），这里跳过
for s in c-dev jira-api bytebase-submit biz-view-query gitlab-api; do
  for mode in baseline withb; do
    if [ "$s" = "gitlab-api" ] && [ "$mode" = "baseline" ]; then
      echo "[$(date +%T)] SKIP gitlab-api baseline (已跑)"
      continue
    fi
    run "$s" "$mode"
  done
done

echo "ALL DONE $(date +%T)"
