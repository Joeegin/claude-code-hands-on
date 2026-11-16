#!/usr/bin/env bash
# PostToolUse Hook：每次 Claude 编辑 .py 文件后自动跑测试。
# 测试通过 → 静默（exit 0）；失败 → 把最后 20 行输出写到 stderr 并 exit 2，Claude 会看到并据此继续修。
event=$(cat)
case "$event" in
  *'.py"'*) ;;          # 只对 .py 文件生效
  *) exit 0 ;;
esac
cd "$CLAUDE_PROJECT_DIR" || exit 0
if out=$(python3 -m pytest -q -x 2>&1); then
  exit 0
fi
echo "自动测试失败（如果你正在按 TDD 先写失败测试，这是预期的）：" >&2
echo "$out" | tail -n 20 >&2
exit 2
