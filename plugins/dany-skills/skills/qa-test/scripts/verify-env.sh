#!/usr/bin/env bash
# Step 1 of the qa-test skill: confirm or refute a handoff's environment
# claims before dispatching anything. Read-only. Prints a report, changes
# nothing, and never signals a process.
#
# Usage: verify-env.sh [-p port,port,...] [worktree ...]
# Repo-specific checks (toolchain versions, schemas) belong in your repo
# reference; add them below the REMINDER block if you fork this script.

set -uo pipefail

PORTS=""
if [ "${1:-}" = "-p" ]; then PORTS="$2"; shift 2; fi

hr() { printf '\n=== %s ===\n' "$1"; }

hr "CONTAINERS (shared with other work: never 'docker compose down')"
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null \
  || echo "  docker not running"

hr "PORTS a QA pass tends to want"
if [ -z "$PORTS" ]; then
  echo "  (pass -p 5001,5002 to check specific ports)"
else
  for p in ${PORTS//,/ }; do
    owner=$(lsof -nP -iTCP:"$p" -sTCP:LISTEN 2>/dev/null | awk 'NR==2 {print $1" pid "$2}')
    printf '  %s: %s\n' "$p" "${owner:-free}"
  done
fi

hr "ORPHANED STUBS (a listener whose source file is gone)"
found=0
for pid in $(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk 'NR>1 && $1 ~ /[Pp]ython|node/ {print $2}' | sort -u); do
  script=$(ps -o command= -p "$pid" 2>/dev/null | awk '{for(i=1;i<=NF;i++) if ($i ~ /\.(py|js|mjs)$/) print $i}' | head -1)
  [ -z "$script" ] && continue
  found=1
  if [ -f "$script" ]; then
    echo "  pid $pid: $script (source present)"
  else
    echo "  pid $pid: $script — SOURCE GONE. Do not kill it and do not send it"
    echo "           a config write; rebuild your stub on a fresh port and leave"
    echo "           this one as a fallback."
  fi
done
[ "$found" -eq 0 ] && echo "  none"

hr "WORKTREES"
for d in "$@"; do
  if [ -d "$d" ]; then
    printf '  %s\n' "$d"
    printf '    branch : %s\n' "$(git -C "$d" branch --show-current 2>&1)"
    printf '    HEAD   : %s\n' "$(git -C "$d" log -1 --format='%h %s' 2>&1)"
    printf '    dirty  : %s file(s)\n' "$(git -C "$d" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
    printf '    vs @{u}: %s\n' "$(git -C "$d" rev-list --left-right --count '@{u}...HEAD' 2>/dev/null || echo 'no upstream')"
  else
    printf '  %s — MISSING\n' "$d"
  fi
done
[ "$#" -eq 0 ] && echo "  (pass worktree paths as arguments to check them)"

hr "REMINDER"
cat <<'TXT'
  A handoff is a map, not a verdict. Re-fetch every pipeline status and every
  SHA before dispatching, and assume last session's scratchpad scripts are gone.
TXT
