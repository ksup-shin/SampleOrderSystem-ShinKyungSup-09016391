"""JSON 데이터를 파싱하고 다시 파일로 저장하는 간단한 라이브러리."""

import json
from pathlib import Path


def load_json(file_path):
    """JSON 파일을 읽어 파이썬 객체(dict/list 등)로 반환한다."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_json(text):
    """JSON 문자열을 파이썬 객체로 파싱한다."""
    return json.loads(text)


def save_json(data, file_path, indent=2, ensure_ascii=False):
    """파이썬 객체를 JSON 파일로 저장한다."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def to_json_string(data, indent=2, ensure_ascii=False):
    """파이썬 객체를 JSON 문자열로 변환한다."""
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
