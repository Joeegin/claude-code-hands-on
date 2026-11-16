# benchkit —— 推理 Benchmark 日志分析工具（练习项目）

> ⚠️ 这是《Claude Code 高效上手手册》的**练习项目**，代码里**故意埋了若干 Bug 和性能问题**。
> 不要自己先去读代码找 Bug——练习的目的是学会**指挥 Claude Code** 去找、去修、去验证。

## 用法

```bash
python -m benchkit data/sample.jsonl            # markdown 报告
python -m benchkit data/sample.jsonl --format json
python -m pytest -q                              # 跑测试
python scripts/gen_data.py -n 100000 -o data/big.jsonl   # 生成大数据集
```

## 日志格式（jsonl，每行一个请求）

```json
{"id": "req-0", "start": 1700000000.05, "first_token": 1700000000.12, "end": 1700000002.3,
 "prompt_tokens": 512, "output_tokens": 180, "status": "ok"}
```

时间单位为秒（Unix 时间戳）。`status` 为 `"ok"` 或 `"error"`；失败请求的 `first_token` 为 `null`。

## 指标规格（这是"需求文档"，代码应当符合它）

1. **TTFT**（首 token 延迟）= `first_token - start`。
2. **TPOT**（每个输出 token 的时间）= `(end - first_token) / (output_tokens - 1)`。
   `output_tokens <= 1` 的请求**不参与** TPOT 统计（但参与 TTFT 统计）。
3. 只有 `status == "ok"` 的请求参与延迟统计；报告中需额外给出**错误率** = error 请求数 / 总请求数。
4. 同一个 `id` 可能出现多次（客户端重试），**以最后一次出现的记录为准**。
5. 分位数使用 **nearest-rank** 方法：第 p 分位 = 排序后第 `ceil(p/100 * n)` 个值（从 1 开始计数）。`max` 即 p100。
6. **吞吐** = 所有 ok 请求的 `output_tokens` 之和 / 整个测试的墙钟时间（所有请求中最晚的 `end` − 最早的 `start`）。
7. 报告中时间以毫秒展示，保留两位小数。
8. `--format json` 输出一个 JSON 对象，**时间单位为秒**（不换算），字段为：
   `count`（ok 请求数）、`error_rate`、`ttft_p50`、`ttft_p90`、`ttft_p99`、`ttft_max`、
   `tpot_p50`、`tpot_p90`、`tpot_p99`、`tpot_max`、`throughput`。

## 数据文件

数据由 `scripts/gen_data.py` 生成（`setup.sh` 已经帮你生成好）：

- `data/sample.jsonl`：基线数据（约 500 个请求）
- `data/after_upgrade.jsonl`：模拟"升级后"的数据，用于性能回退对比练习
