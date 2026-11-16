import json


def dedupe(reqs):
    seen_ids = []
    out = []
    for r in reqs:
        if r.id not in seen_ids:
            seen_ids.append(r.id)
            out.append(r)
    return out


def render_markdown(summary):
    lines = ["| 指标 | 值 |", "|---|---|"]
    lines.append(f"| 请求数 | {summary['count']} |")
    for key in ["ttft", "tpot"]:
        for q in ["p50", "p90", "p99", "max"]:
            v = summary[f"{key}_{q}"] * 1000
            lines.append(f"| {key.upper()} {q} | {v:.2f} ms |")
    lines.append(f"| 吞吐 | {summary['throughput']:.1f} tok/s |")
    return "\n".join(lines)


def render_json(summary):
    return json.dumps(summary, indent=2, ensure_ascii=False)
