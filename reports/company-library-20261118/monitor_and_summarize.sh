#!/bin/bash
# 等待 Tier1 静态扫描完成（最多 20 分钟），超时则停止，最后汇总。
ROOT=/Users/yangyuhan/ai-agent-agent-skills
STATUS="$ROOT/reports/company-library-20261118/tier1-status.txt"
TOTAL=37
DEADLINE=$((SECONDS + 1200))   # 20 分钟

stop_scan() {
  echo "=== 停止扫描 ==="
  pkill -f 'run_tier1_static.sh' 2>/dev/null
  pkill -f 'xargs -n 2 -P 4' 2>/dev/null
  pkill -f 'bash -c run_one' 2>/dev/null
  docker ps -q --filter 'name=skillevaluator-run' | xargs -r docker rm -f 2>/dev/null
  echo "=== 已停止 ==="
}

while :; do
  n=$(wc -l < "$STATUS" 2>/dev/null | tr -d ' ')
  if [ "$n" -ge "$TOTAL" ]; then
    echo "ALL_DONE $n/$TOTAL  (elapsed $((1200 - (DEADLINE - SECONDS)))s)"
    break
  fi
  if [ "$SECONDS" -ge "$DEADLINE" ]; then
    echo "TIMEOUT: 只有 $n/$TOTAL 完成，20 分钟已到"
    stop_scan
    break
  fi
  sleep 20
done

# 最终汇总（缺失的 skill 会标记为 MISSING）
python3 "$ROOT/reports/company-library-20261118/summarize_tier1.py"
echo "SUMMARIZE_DONE $(wc -l < "$STATUS" | tr -d ' ')/$TOTAL"
