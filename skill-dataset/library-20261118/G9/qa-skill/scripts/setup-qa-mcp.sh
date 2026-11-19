#!/bin/sh
set -eu

SERVER_NAME='aiTroubleShot'
SERVER_URL='https://ai-trouble-shot.test.seewo.com/api/mcp'
TOKEN_ENV_NAME='AI_TROUBLE_SHOT_MCP_TOKEN'
CLAUDE_JSON='{"type":"http","url":"https://ai-trouble-shot.test.seewo.com/api/mcp","headers":{"Authorization":"Bearer ${AI_TROUBLE_SHOT_MCP_TOKEN}"}}'

confirmed=0
agent='auto'

usage() {
  printf '%s\n' 'usage: setup-qa-mcp.sh --yes [--agent auto|claude-code|codex|all]' >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --yes) confirmed=1; shift ;;
    --agent)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      agent=$2
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
done

case "$agent" in
  auto|claude-code|codex|all) ;;
  *) usage; exit 2 ;;
esac

[ "$confirmed" -eq 1 ] || {
  printf '%s\n' 'setup requires prior user confirmation; rerun with --yes' >&2
  exit 2
}

token=${AI_TROUBLE_SHOT_MCP_TOKEN-}
carriage_return=$(printf '\r')
case "$token" in
  ''|*'
'*|*"$carriage_return"*)
    printf '%s\n' 'AI_TROUBLE_SHOT_MCP_TOKEN must be set to a non-empty single-line value' >&2
    exit 2
    ;;
esac
unset token

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/qa-mcp-setup.XXXXXX")
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

want_claude=0
want_codex=0
case "$agent" in
  auto|all) want_claude=1; want_codex=1 ;;
  claude-code) want_claude=1 ;;
  codex) want_codex=1 ;;
esac

compatible_count=0
detected_count=0
has_conflict=0
has_failure=0

is_absent_result() {
  grep -Eiq 'no mcp server (found|named)|mcp server .* (not found|does not exist)' "$1"
}

claude_compatible() {
  grep -Eq 'URL:[[:space:]]*https://ai-trouble-shot\.test\.seewo\.com/api/mcp([[:space:]]|$)' "$1" &&
    grep -Eq 'Authorization:[[:space:]]*Bearer[[:space:]]+\$\{AI_TROUBLE_SHOT_MCP_TOKEN\}' "$1" &&
    [ "$(grep -Eic '^[[:space:]]*Scope:[[:space:]]*User[[:space:]]*$' "$1")" -eq 1 ] &&
    [ "$(grep -Eic '^[[:space:]]*Scope:' "$1")" -eq 1 ]
}

codex_compatible() {
  grep -Eq '"enabled"[[:space:]]*:[[:space:]]*true' "$1" &&
    grep -Eq '"url"[[:space:]]*:[[:space:]]*"https://ai-trouble-shot\.test\.seewo\.com/api/mcp"' "$1" &&
    grep -Eq '"bearer_token_env_var"[[:space:]]*:[[:space:]]*"AI_TROUBLE_SHOT_MCP_TOKEN"' "$1"
}

setup_claude() {
  inspect_file="$work_dir/claude-get"
  if claude mcp get "$SERVER_NAME" >"$inspect_file" 2>&1; then
    if claude_compatible "$inspect_file"; then
      printf '%s\n' 'claude-code: already-configured'
      compatible_count=$((compatible_count + 1))
    else
      printf '%s\n' 'claude-code: conflict (url, auth, or scope differs)'
      has_conflict=1
    fi
    return
  fi
  if ! is_absent_result "$inspect_file"; then
    printf '%s\n' 'claude-code: failed (unable to inspect configuration)'
    has_failure=1
    return
  fi
  if claude mcp add-json --scope user "$SERVER_NAME" "$CLAUDE_JSON" >"$work_dir/claude-add" 2>&1 &&
      claude mcp get "$SERVER_NAME" >"$work_dir/claude-verify" 2>&1 &&
      claude_compatible "$work_dir/claude-verify"; then
    printf '%s\n' 'claude-code: installed'
    compatible_count=$((compatible_count + 1))
  else
    printf '%s\n' 'claude-code: failed (registration or verification failed)'
    has_failure=1
  fi
}

setup_codex() {
  inspect_file="$work_dir/codex-get"
  if codex mcp get "$SERVER_NAME" --json >"$inspect_file" 2>&1; then
    if codex_compatible "$inspect_file"; then
      printf '%s\n' 'codex: already-configured'
      compatible_count=$((compatible_count + 1))
    else
      printf '%s\n' 'codex: conflict (url, auth, or enabled state differs)'
      has_conflict=1
    fi
    return
  fi
  if ! is_absent_result "$inspect_file"; then
    printf '%s\n' 'codex: failed (unable to inspect configuration)'
    has_failure=1
    return
  fi
  if codex mcp add "$SERVER_NAME" --url "$SERVER_URL" --bearer-token-env-var "$TOKEN_ENV_NAME" >"$work_dir/codex-add" 2>&1 &&
      codex mcp get "$SERVER_NAME" --json >"$work_dir/codex-verify" 2>&1 &&
      codex_compatible "$work_dir/codex-verify"; then
    printf '%s\n' 'codex: installed'
    compatible_count=$((compatible_count + 1))
  else
    printf '%s\n' 'codex: failed (registration or verification failed)'
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

[ "$compatible_count" -eq 0 ] || printf '%s\n' 'MCP_SESSION_RESTART_REQUIRED'
[ "$has_failure" -eq 0 ] || exit 5
[ "$has_conflict" -eq 0 ] || exit 4
[ "$detected_count" -ne 0 ] || exit 3
exit 0
