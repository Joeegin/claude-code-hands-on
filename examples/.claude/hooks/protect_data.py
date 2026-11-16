#!/usr/bin/env python3
"""PreToolUse Hook：禁止 Claude 编辑 data/ 下的测试数据。

Claude Code 通过 stdin 传入 JSON（含 tool_name、tool_input）。
退出码 2 = 阻止本次工具调用，stderr 的内容会反馈给 Claude。
"""
import json
import sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("file_path", "")
if "/data/" in path and path.endswith(".jsonl"):
    print("data/*.jsonl 是测试数据，禁止直接修改。需要新数据请用 scripts/gen_data.py 生成。", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
