#!/bin/sh
set -eu

SERVER_NAME='aiTroubleShot'
SERVER_URL='https://ai-trouble-shot.test.seewo.com/api/mcp'
PLATFORM_URL='https://ai-trouble-shot.test.seewo.com/web/'
TOKEN_ENV_NAME='AI_TROUBLE_SHOT_MCP_TOKEN'
CLAUDE_JSON='{"type":"http","url":"https://ai-trouble-shot.test.seewo.com/api/mcp","headers":{"Authorization":"Bearer ${AI_TROUBLE_SHOT_MCP_TOKEN}"}}'

confirmed=0
agent='auto'

usage() {
  printf '%s\n' 'usage: setup-mcp.sh --yes [--agent auto|claude-code|codex|all]' >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --yes)
      confirmed=1
      shift
      ;;
    --agent)
      if [ "$#" -lt 2 ]; then
        usage
        exit 2
      fi
      agent=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

case "$agent" in
  auto|claude-code|codex|all) ;;
  *)
    usage
    exit 2
    ;;
esac

if [ "$confirmed" -ne 1 ]; then
  printf '%s\n' 'setup requires prior user confirmation; rerun with --yes' >&2
  exit 2
fi

token=${AI_TROUBLE_SHOT_MCP_TOKEN-}
carriage_return=$(printf '\r')
case "$token" in
  ''|*'
'*|*"$carriage_return"*)
    printf '%s\n' 'MCP_API_KEY_REQUIRED' >&2
    printf '%s\n' '请先登录问题排查平台：' "$PLATFORM_URL" >&2
    printf '%s\n' '登录后打开右上角用户名菜单 → API Key 管理，创建个人 API Key。' >&2
    printf '%s\n' '仅在启动 Claude Code/Codex 的环境中设置 AI_TROUBLE_SHOT_MCP_TOKEN，然后重新执行本脚本。' >&2
    exit 2
    ;;
esac
unset token

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/unified-support-mcp-setup.XXXXXX")
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

want_claude=0
want_codex=0
case "$agent" in
  auto|all)
    want_claude=1
    want_codex=1
    ;;
  claude-code) want_claude=1 ;;
  codex) want_codex=1 ;;
esac

compatible_count=0
detected_count=0
has_conflict=0
has_failure=0

is_absent_result() {
  output_file=$1
  grep -Eiq 'no mcp server (found|named)|mcp server .* (not found|does not exist)' "$output_file"
}

claude_compatible() {
  output_file=$1
  grep -Eq 'URL:[[:space:]]*https://ai-trouble-shot\.test\.seewo\.com/api/mcp([[:space:]]|$)' "$output_file" &&
    grep -Eq 'Authorization:[[:space:]]*Bearer[[:space:]]+\$\{AI_TROUBLE_SHOT_MCP_TOKEN\}' "$output_file" &&
    [ "$(grep -Eic '^[[:space:]]*Scope:[[:space:]]*User[[:space:]]*$' "$output_file")" -eq 1 ] &&
    [ "$(grep -Eic '^[[:space:]]*Scope:' "$output_file")" -eq 1 ]
}

claude_conflict_details() {
  output_file=$1
  conflict_details=''
  grep -Eq 'URL:[[:space:]]*https://ai-trouble-shot\.test\.seewo\.com/api/mcp([[:space:]]|$)' "$output_file" || conflict_details='url'
  if ! grep -Eq 'Authorization:[[:space:]]*Bearer[[:space:]]+\$\{AI_TROUBLE_SHOT_MCP_TOKEN\}' "$output_file"; then
    conflict_details="${conflict_details}${conflict_details:+,}auth"
  fi
  if [ "$(grep -Eic '^[[:space:]]*Scope:[[:space:]]*User[[:space:]]*$' "$output_file")" -ne 1 ] ||
      [ "$(grep -Eic '^[[:space:]]*Scope:' "$output_file")" -ne 1 ]; then
    conflict_details="${conflict_details}${conflict_details:+,}scope"
  fi
  printf '%s' "${conflict_details:-unknown}"
}

codex_compatible() {
  output_file=$1
  grep -Eq '"enabled"[[:space:]]*:[[:space:]]*true' "$output_file" &&
    grep -Eq '"url"[[:space:]]*:[[:space:]]*"https://ai-trouble-shot\.test\.seewo\.com/api/mcp"' "$output_file" &&
    grep -Eq '"bearer_token_env_var"[[:space:]]*:[[:space:]]*"AI_TROUBLE_SHOT_MCP_TOKEN"' "$output_file"
}

codex_conflict_details() {
  output_file=$1
  conflict_details=''
  grep -Eq '"enabled"[[:space:]]*:[[:space:]]*true' "$output_file" || conflict_details='disabled'
  if ! grep -Eq '"url"[[:space:]]*:[[:space:]]*"https://ai-trouble-shot\.test\.seewo\.com/api/mcp"' "$output_file"; then
    conflict_details="${conflict_details}${conflict_details:+,}url"
  fi
  if ! grep -Eq '"bearer_token_env_var"[[:space:]]*:[[:space:]]*"AI_TROUBLE_SHOT_MCP_TOKEN"' "$output_file"; then
    conflict_details="${conflict_details}${conflict_details:+,}auth"
  fi
  printf '%s' "${conflict_details:-unknown}"
}

setup_claude() {
  inspect_file="$work_dir/claude-get"
  verify_file="$work_dir/claude-verify"
  add_file="$work_dir/claude-add"

  if claude mcp get "$SERVER_NAME" >"$inspect_file" 2>&1; then
    if claude_compatible "$inspect_file"; then
      printf '%s\n' 'claude-code: already-configured'
      compatible_count=$((compatible_count + 1))
    else
      printf 'claude-code: conflict (%s differs; inspect with claude mcp get %s)\n' "$(claude_conflict_details "$inspect_file")" "$SERVER_NAME"
      has_conflict=1
    fi
    return
  fi
  if ! is_absent_result "$inspect_file"; then
    printf '%s\n' 'claude-code: failed (unable to inspect configuration)'
    has_failure=1
    return
  fi
  if ! claude mcp add-json --scope user "$SERVER_NAME" "$CLAUDE_JSON" >"$add_file" 2>&1; then
    printf '%s\n' 'claude-code: failed (registration command failed)'
    has_failure=1
    return
  fi
  if claude mcp get "$SERVER_NAME" >"$verify_file" 2>&1 && claude_compatible "$verify_file"; then
    printf '%s\n' 'claude-code: installed'
    compatible_count=$((compatible_count + 1))
  else
    printf '%s\n' 'claude-code: failed (verification failed)'
    has_failure=1
  fi
}

setup_codex() {
  inspect_file="$work_dir/codex-get"
  verify_file="$work_dir/codex-verify"
  add_file="$work_dir/codex-add"

  if codex mcp get "$SERVER_NAME" --json >"$inspect_file" 2>&1; then
    if codex_compatible "$inspect_file"; then
      printf '%s\n' 'codex: already-configured'
      compatible_count=$((compatible_count + 1))
    else
      printf 'codex: conflict (%s differs; inspect with codex mcp get %s --json)\n' "$(codex_conflict_details "$inspect_file")" "$SERVER_NAME"
      has_conflict=1
    fi
    return
  fi
  if ! is_absent_result "$inspect_file"; then
    printf '%s\n' 'codex: failed (unable to inspect configuration)'
    has_failure=1
    return
  fi
  if ! codex mcp add "$SERVER_NAME" --url "$SERVER_URL" --bearer-token-env-var "$TOKEN_ENV_NAME" >"$add_file" 2>&1; then
    printf '%s\n' 'codex: failed (registration command failed)'
    has_failure=1
    return
  fi
  if codex mcp get "$SERVER_NAME" --json >"$verify_file" 2>&1 && codex_compatible "$verify_file"; then
    printf '%s\n' 'codex: installed'
    compatible_count=$((compatible_count + 1))
  else
    printf '%s\n' 'codex: failed (verification failed)'
    has_failure=1
  fi
}

if [ "$want_claude" -eq 1 ]; then
  if command -v claude >/dev/null 2>&1; then
    detected_count=$((detected_count + 1))
    setup_claude
  else
    printf '%s\n' 'claude-code: skipped (host not found)'
  fi
fi

if [ "$want_codex" -eq 1 ]; then
  if command -v codex >/dev/null 2>&1; then
    detected_count=$((detected_count + 1))
    setup_codex
  else
    printf '%s\n' 'codex: skipped (host not found)'
  fi
fi

if [ "$compatible_count" -gt 0 ]; then
  printf '%s\n' 'MCP_SESSION_RESTART_REQUIRED'
fi
if [ "$has_failure" -ne 0 ]; then
  exit 5
fi
if [ "$has_conflict" -ne 0 ]; then
  exit 4
fi
if [ "$detected_count" -eq 0 ]; then
  exit 3
fi
exit 0
