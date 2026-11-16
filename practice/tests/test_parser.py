from benchkit.parser import load_requests


def test_load_sample():
    reqs = load_requests("data/sample.jsonl")
    assert len(reqs) > 0
    assert reqs[0].id.startswith("req-")
