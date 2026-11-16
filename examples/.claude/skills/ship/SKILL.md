---
name: ship
description: 提交前的自审与提交流程：检查改动、跑测试、独立审查、提交。用户说"收尾""提交""ship"时使用。
disable-model-invocation: true
---

# 收尾并提交

按顺序执行，任何一步失败都停下来向我报告，不要跳过：

1. 运行 `git status` 和 `git diff`，确认所有改动都与本次任务相关。发现无关改动时先问我。
2. 运行 `python -m pytest -q`。有失败就停下，报告失败原因。
3. 使用 spec-reviewer 子代理独立审查当前 diff，重点检查正确性、边界情况、是否符合 README 规格。
4. 审查发现真实问题 → 修复后回到第 2 步；没有问题 → 用中文写 commit message 并提交。
5. 汇报：改了什么、测试结果、审查发现了什么。**不要 push。**

本次附加说明：$ARGUMENTS
