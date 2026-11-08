#!/usr/bin/env bash
# Copy into <project>/scripts/checkpoint.sh. Anyone may run it - you or the agent.
#
#     scripts/checkpoint.sh N              run step N: every check narrated, output saved
#     scripts/checkpoint.sh N --explain    what step N will check; runs nothing
#     scripts/checkpoint.sh all            run every checkpoint that exists, then a summary
#
# The run is shown in the terminal and saved to evidence/SNN.log, so a reviewer in a
# later session can read what happened.
set -euo pipefail

usage="usage: scripts/checkpoint.sh <N | all> [--explain]   e.g. scripts/checkpoint.sh 7"
NN="${1:?$usage}"

if [ "$NN" = "all" ]; then
  passed=0; failed=0; summary=""
  for c in scripts/checks/S[0-9]*.sh; do
    [ -f "$c" ] || continue
    n="$(basename "$c" .sh)"; n="${n#S}"
    if "$0" "$n"; then
      passed=$((passed + 1)); summary="${summary}  ok    S${n}"$'\n'
    else
      failed=$((failed + 1)); summary="${summary}  FAIL  S${n}"$'\n'
    fi
    echo
  done
  echo "== all checkpoints"
  printf '%s' "$summary"
  echo
  if [ "$failed" -gt 0 ]; then
    echo "FAIL: ${failed} of $((passed + failed)) checkpoints failed"
    exit 1
  fi
  if [ "$passed" -eq 0 ]; then
    echo "FAIL: no checkpoints found in scripts/checks/"
    exit 1
  fi
  echo "PASS: ${passed} of ${passed} checkpoints passed"
  exit 0
fi

# Accept 7 as well as 07.
case "$NN" in
  ''|*[!0-9]*) ;;
  *) NN="$(printf '%02d' "$((10#$NN))")" ;;
esac
check="scripts/checks/S${NN}.sh"

if [ ! -f "$check" ]; then
  echo "FAIL: $check does not exist yet - it is written when step S${NN} starts"
  exit 1
fi

# --explain: the summary and the list of checks. Nothing executed, nothing saved.
if [ "${2:-}" = "--explain" ]; then
  CHECKPOINT_EXPLAIN=1 bash "$check"
  echo "   It will check, in order:"
  grep -E '^[[:space:]]*(check|check_eq|require|require_eq)[[:space:]]+"' "$check" \
    | sed -E 's/^[[:space:]]*(require[a-z_]*)[[:space:]]+"([^"]*)".*/     - \2   (stops the run if it fails)/; s/^[[:space:]]*check[a-z_]*[[:space:]]+"([^"]*)".*/     - \1/' \
    || echo "     (none found - this checkpoint asserts nothing)"
  echo
  echo "   Nothing was run. To run it: scripts/checkpoint.sh ${NN}"
  exit 0
fi

log="evidence/S${NN}.log"
mkdir -p evidence

{
  echo "# S${NN} checkpoint run"
  echo "# started  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# commit   $(git rev-parse --short HEAD 2>/dev/null || echo 'no commit yet')"
  echo "# check    $(git hash-object "$check" 2>/dev/null || echo unknown)"
  echo "# ---"
} >"$log"

# Shown and saved at once. The exit code is the checkpoint's, not tee's.
set +e
bash "$check" 2>&1 | tee -a "$log"
rc="${PIPESTATUS[0]}"
set -e
echo "# exit     $rc" >>"$log"

if [ "$rc" -ne 0 ]; then
  exit "$rc"
fi

# Exit 0 is not enough: the verdict line is printed only by finish in lib.sh, after at
# least one check ran and none failed.
if ! grep -q "^PASS: S${NN} " "$log"; then
  echo "FAIL: S${NN} exited 0 but reached no PASS verdict - it asserts nothing"
  exit 1
fi
