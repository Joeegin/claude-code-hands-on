#!/usr/bin/env bash
# 把练习项目复制到一个独立目录，并初始化为 git 仓库（初始状态打标签 start）。
# 用法: ./setup.sh [目标目录]     默认 ~/benchkit-practice
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/practice"
DEST="${1:-$HOME/benchkit-practice}"

if [ -e "$DEST" ]; then
  echo "目标目录已存在: $DEST"
  echo "如需重新开始，请先手动删除或换一个目录: ./setup.sh <新目录>"
  exit 1
fi

cp -r "$SRC" "$DEST"
cd "$DEST"
python3 scripts/gen_data.py -n 500 -o data/sample.jsonl
python3 scripts/gen_data.py -n 500 --seed 7 --slow-decode 1.25 -o data/after_upgrade.jsonl
git init -q
git add -A
git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name || echo learner)}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo learner@example.com)}" \
    commit -q -m "benchkit: initial practice project"
git tag start
echo "✅ 练习项目已就绪: $DEST"
echo "下一步: cd $DEST && claude"
