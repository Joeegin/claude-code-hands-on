def ttft(r):
    return r.first_token - r.start


def tpot(r):
    return (r.end - r.first_token) / r.output_tokens


def percentile(values, p):
    s = sorted(values)
    return s[int(len(s) * p / 100)]


def throughput(reqs):
    total_tokens = sum(r.output_tokens for r in reqs)
    total_time = sum(r.end - r.start for r in reqs)
    return total_tokens / total_time


def summarize(reqs):
    ttfts = [ttft(r) for r in reqs]
    tpots = [tpot(r) for r in reqs]
    return {
        "count": len(reqs),
        "ttft_p50": percentile(ttfts, 50),
        "ttft_p90": percentile(ttfts, 90),
        "ttft_p99": percentile(ttfts, 99),
        "ttft_max": percentile(ttfts, 100),
        "tpot_p50": percentile(tpots, 50),
        "tpot_p90": percentile(tpots, 90),
        "tpot_p99": percentile(tpots, 99),
        "tpot_max": percentile(tpots, 100),
        "throughput": throughput(reqs),
    }
