import argparse

from .metrics import summarize
from .parser import load_requests
from .report import dedupe, render_json, render_markdown


def main(argv=None):
    ap = argparse.ArgumentParser(prog="benchkit", description="分析推理 Benchmark 日志")
    ap.add_argument("log", help="jsonl 格式的请求日志")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args(argv)

    reqs = dedupe(load_requests(args.log))
    summary = summarize(reqs)
    print(render_markdown(summary) if args.format == "md" else render_json(summary))


if __name__ == "__main__":
    main()
