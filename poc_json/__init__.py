"""JSON 파일 파싱/저장, CRUD, 실시간 조회용 관리자 도구를 제공하는 라이브러리.

다른 프로젝트에서 사용하려면 이 poc_json 폴더를 그대로 복사해 넣으면 된다.

사용 예:

    from poc_json import load_json, save_json, create_item, read_all

    create_item("items.json", {"id": 1, "name": "사과"})
    items = read_all("items.json")

콘솔 관리자 도구:

    python -m poc_json.admin_tool items.json          # 대화형 조회
    python -m poc_json.admin_tool items.json --watch  # 실시간 감시 모드
"""

from .json_lib import load_json, parse_json, save_json, to_json_string
from .json_crud import create_item, read_all, read_by_id, update_item, delete_item

__version__ = "0.1.0"

__all__ = [
    "load_json",
    "parse_json",
    "save_json",
    "to_json_string",
    "create_item",
    "read_all",
    "read_by_id",
    "update_item",
    "delete_item",
]
