#!/usr/bin/env python3
"""benchkit 自动验收脚本。

用法（在 agent-learn 仓库根目录运行）:
    python3 grader/check.py [练习目录]          默认 ~/benchkit-practice
    python3 grader/check.py [练习目录] --perf   额外检查 10 万行数据的性能

它用一份独立的参考实现计算期望结果，和你的 `python -m benchkit <log> --format json` 输出逐项对比。

⚠️ 不要让 Claude 在练习时读这个文件——里面就是标准答案。
   练习目录放在仓库外面（setup.sh 默认放在 ~/benchkit-practice）就是为了这个。
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import time

KEYS = ["count", "error_rate",
        "ttft_p50", "ttft_p90", "ttft_p99", "ttft_max",
        "tpot_p50", "tpot_p90", "tpot_p99", "tpot_max", "throughput"]


def reference(path):
    last = {}
    for line in open(path):
        line = line.strip()
        if line:
            d = json.loads(line)
            last.pop(d["id"], None)
            last[d["id"]] = d                      # 规格 4：同 id 以最后一次为准
    reqs = list(last.values())
    ok = [r for r in reqs if r["status"] == "ok"]  # 规格 3

    def pct(vals, p):                              # 规格 5：nearest-rank
        s = sorted(vals)
        return s[max(math.ceil(p / 100 * len(s)), 1) - 1]

    ttfts = [r["first_token"] - r["start"] for r in ok]
    tpots = [(r["end"] - r["first_token"]) / (r["output_tokens"] - 1)
             for r in ok if r["output_tokens"] > 1]   # 规格 2
    wall = max(r["end"] for r in reqs) - min(r["start"] for r in reqs)   # 规格 6
    out = {"count": len(ok), "error_rate": (len(reqs) - len(ok)) / len(reqs)}
    for name, vals in (("ttft", ttfts), ("tpot", tpots)):
        for q, p in (("p50", 50), ("p90", 90), ("p99", 99), ("max", 100)):
            out[f"{name}_{q}"] = pct(vals, p)
    out["throughput"] = sum(r["output_tokens"] for r in ok) / wall
    return out


def edge_case_file(tmpdir):
    """手工构造的边界数据：重复 id、output_tokens=1、失败请求、并发重叠。"""
    rows = [
        dict(id="a", start=0.0, first_token=0.1, end=1.0, prompt_tokens=10, output_tokens=10, status="ok"),
        dict(id="b", start=0.5, first_token=0.7, end=0.7, prompt_tokens=10, output_tokens=1, status="ok"),
        dict(id="c", start=0.6, first_token=None, end=0.8, prompt_tokens=10, output_tokens=0, status="error"),
        dict(id="d", start=0.2, first_token=0.5, end=2.5, prompt_tokens=10, output_tokens=21, status="ok"),
        dict(id="a", start=1.2, first_token=1.25, end=3.0, prompt_tokens=10, output_tokens=8, status="ok"),
        dict(id="e", start=1.0, first_token=1.3, end=1.9, prompt_tokens=10, output_tokens=4, status="ok"),
    ]
    path = os.path.join(tmpdir, "edge.jsonl")
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return path


def run_benchkit(workdir, log):
    p = subprocess.run([sys.executable, "-m", "benchkit", log, "--format", "json"],
                       cwd=workdir, capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        return None, p.stderr.strip().splitlines()[-1] if p.stderr.strip() else f"exit {p.returncode}"
    try:
        return json.loads(p.stdout), None
    except json.JSONDecodeError:
        return None, "输出不是合法 JSON"


def check(workdir, log, label):
    got, err = run_benchkit(workdir, log)
    if err:
        print(f"  ❌ {label}: 运行失败 —— {err}")
        return False
    exp = reference(log)
    ok = True
    for k in KEYS:
        if k not in got:
            print(f"  ❌ {label}: 缺少字段 {k}")
            ok = False
        elif not math.isclose(got[k], exp[k], rel_tol=1e-6, abs_tol=1e-9):
            print(f"  ❌ {label}: {k} = {got[k]!r}，期望 {exp[k]!r}")
            ok = False
    if ok:
        print(f"  ✅ {label}")
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    workdir = os.path.expanduser(args[0] if args else "~/benchkit-practice")
    if not os.path.isdir(os.path.join(workdir, "benchkit")):
        sys.exit(f"找不到练习项目: {workdir}（先运行 ./setup.sh）")

    print(f"验收目录: {workdir}\n")
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        print("[正确性]")
        results.append(check(workdir, edge_case_file(tmp), "边界数据（重复 id / output_tokens=1 / 失败请求）"))
        for name in ("sample.jsonl", "after_upgrade.jsonl"):
            path = os.path.join(workdir, "data", name)
            if os.path.exists(path):
                results.append(check(workdir, path, f"data/{name}"))

        if "--perf" in sys.argv:
            print("\n[性能]")
            big = os.path.join(tmp, "big.jsonl")
            subprocess.run([sys.executable, "scripts/gen_data.py", "-n", "100000", "-o", big],
                           cwd=workdir, check=True)
            t = time.time()
            good = check(workdir, big, "10 万行数据结果正确")
            dt = time.time() - t
            fast = dt < 5
            print(f"  {'✅' if fast else '❌'} 耗时 {dt:.1f}s（要求 < 5s）")
            results.append(good and fast)

    passed = sum(results)
    print(f"\n通过 {passed}/{len(results)}")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
