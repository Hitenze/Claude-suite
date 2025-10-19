#!/usr/bin/env bash
set -u

pass_count=0
fail_count=0

assert_exit() {
  local got=$1 expected=$2 name=$3
  if [ "$got" -eq "$expected" ]; then
    echo "[PASS] $name (exit $got)"
    pass_count=$((pass_count+1))
  else
    echo "[FAIL] $name: expected exit $expected, got $got" >&2
    fail_count=$((fail_count+1))
  fi
}

assert_contains() {
  local haystack=$1 needle=$2 name=$3
  if printf "%s" "$haystack" | grep -q "$needle"; then
    echo "[PASS] $name (contains '$needle')"
    pass_count=$((pass_count+1))
  else
    echo "[FAIL] $name: missing '$needle'" >&2
    fail_count=$((fail_count+1))
  fi
}

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p tests/tmp

########################################
# filename_ban_hook.py
########################################
json_block='{"tool_input":{"file_path":"final_v2.py"}}'
out=$(printf '%s' "$json_block" | python3 hooks/filename_ban_hook.py 2>tests/tmp/err1.txt); rc=$?
assert_exit "$rc" 2 "filename_ban: block bad pattern"
assert_contains "$out" '"decision": "block"' "filename_ban: block decision JSON"

json_ok='{"tool_input":{"file_path":"good_name.py"}}'
out=$(printf '%s' "$json_ok" | python3 hooks/filename_ban_hook.py 2>tests/tmp/err2.txt); rc=$?
assert_exit "$rc" 0 "filename_ban: allow good name"

########################################
# check_chinese_hook.py
########################################
json_cn='{"tool_input":{"file_path":"main.py","content":"# 注释 with Chinese"}}'
out=$(CHECK_MODE=comments CHECK_CHINESE=true BLOCK_ON_DETECTION=true \
      printf '%s' "$json_cn" | python3 hooks/check_chinese_hook.py 2>tests/tmp/err3.txt); rc=$?
assert_exit "$rc" 2 "check_chinese: block on Chinese in comments"

json_ascii='{"tool_input":{"file_path":"main.py","content":"# comment"}}'
out=$(CHECK_MODE=comments CHECK_CHINESE=true BLOCK_ON_DETECTION=true \
      printf '%s' "$json_ascii" | python3 hooks/check_chinese_hook.py 2>tests/tmp/err4.txt); rc=$?
assert_exit "$rc" 0 "check_chinese: allow ASCII comments"

########################################
# no_show_in_python_hook.py
########################################
json_show='{"tool_input":{"file_path":"plot.py","content":"import matplotlib\\nimport matplotlib.pyplot as plt\\nplt.show()"}}'
out=$(printf '%s' "$json_show" | python3 hooks/no_show_in_python_hook.py 2>tests/tmp/err5.txt); rc=$?
assert_exit "$rc" 2 "no_show: block plt.show()"

########################################
# protect_phase_file.py
########################################
json_phase='{"tool_input":{"file_path":"/home/user/project/.claude/current_phase"}}'
out=$(printf '%s' "$json_phase" | python3 local_hooks/templates/hooks/protect_phase_file.py 2>tests/tmp/err6.txt); rc=$?
assert_exit "$rc" 2 "protect_phase: block direct phase file edit"

########################################
# formatting_hook.sh (wrapper)
########################################
echo 'x=1' > tests/tmp/sample.py
json_fmt='{"tool_input":{"file_path":"tests/tmp/sample.py"}}'
out=$(printf '%s' "$json_fmt" | bash hooks/formatting_hook.sh 2>tests/tmp/err7.txt); rc=$?
# Even without formatters installed, should not fail
assert_exit "$rc" 0 "formatting_hook: run without error"

echo ""
echo "Summary: $pass_count passed, $fail_count failed"
if [ "$fail_count" -gt 0 ]; then
  exit 1
fi
exit 0
