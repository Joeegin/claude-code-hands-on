---
name: bench-report
description: 分析推理 Benchmark 日志并给出结论。用户要求分析 benchmark 结果、对比性能、排查性能回退时使用。
---

# Benchmark 分析

参数：$ARGUMENTS（一个或两个 jsonl 日志路径；两个时第一个是基线）

1. 先用 `wc -l` 和 `head -3` 了解数据规模和格式，不要把整个日志读进上下文。
2. 用 `python -m benchkit <日志> --format json` 拿到指标（有两个日志就分别运行）。
3. 输出一张 markdown 表：指标 / 基线 / 新值 / 变化%。
4. 结论区分三类，不得混淆：
   - **实测事实**（表里的数字）
   - **推断**（例如"TPOT 变差而 TTFT 不变，说明问题更可能在 decode 阶段"）
   - **需要进一步验证的假设**，并给出验证方法
5. 不要编造日志里没有的信息（比如 GPU 型号、batch size）。
