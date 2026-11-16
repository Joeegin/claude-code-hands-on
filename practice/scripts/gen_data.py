"""生成模拟的推理 Benchmark 日志。用法: python scripts/gen_data.py -n 500 -o data/sample.jsonl"""
import argparse
import json
import random


def gen(n, seed, slow_decode=1.0):
    rng = random.Random(seed)
    t = 1_700_000_000.0
    rows = []
    for i in range(n):
        t += rng.expovariate(20)  # 平均每秒 20 个请求到达
        start = t
        prompt = rng.randint(64, 2048)
        if rng.random() < 0.03:
            rows.append(dict(id=f"req-{i}", start=start, first_token=None,
                             end=start + rng.uniform(0.01, 0.5), prompt_tokens=prompt,
                             output_tokens=0, status="error"))
            continue
        out = 1 if rng.random() < 0.02 else rng.randint(16, 512)
        ttft = 0.02 + prompt * 0.00004 + rng.expovariate(30)
        tpot = rng.gauss(0.012, 0.002) * slow_decode
        first = start + ttft
        end = first + tpot * max(out - 1, 0)
        rows.append(dict(id=f"req-{i}", start=start, first_token=first, end=end,
                         prompt_tokens=prompt, output_tokens=out, status="ok"))
        if rng.random() < 0.02:  # 模拟客户端重试：同一 id 再出现一次，以最后一次为准
            s2 = end + 0.1
            f2 = s2 + ttft
            rows.append(dict(id=f"req-{i}", start=s2, first_token=f2,
                             end=f2 + tpot * max(out - 1, 0), prompt_tokens=prompt,
                             output_tokens=out, status="ok"))
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--slow-decode", type=float, default=1.0, help="TPOT 放大倍数，用来模拟性能回退")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    with open(a.out, "w") as f:
        for row in gen(a.n, a.seed, a.slow_decode):
            f.write(json.dumps(row) + "\n")
