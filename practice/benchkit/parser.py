import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class Request:
    id: str
    start: float
    first_token: Optional[float]
    end: float
    prompt_tokens: int
    output_tokens: int
    status: str


def load_requests(path):
    requests = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            requests.append(Request(**d))
    return requests
