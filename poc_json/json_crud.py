"""JSON 파일을 데이터 저장소로 사용하는 CRUD 기능.

레코드는 각각 고유한 id 필드를 가진 dict 이며, 파일 전체는 그 dict들의 list다.
예: [{"id": 1, "name": "..."}, {"id": 2, "name": "..."}]
"""

from .json_lib import load_json, save_json


def _load_records(file_path):
    """파일이 없으면 빈 목록으로 시작한다."""
    try:
        return load_json(file_path)
    except FileNotFoundError:
        return []


def _find_index(records, id_value, id_field):
    for i, record in enumerate(records):
        if record.get(id_field) == id_value:
            return i
    return -1


def create_item(file_path, item, id_field="id"):
    """새 레코드를 추가한다. 같은 id_field 값이 이미 있으면 에러를 발생시킨다."""
    records = _load_records(file_path)

    if id_field not in item:
        raise ValueError(f"item에 '{id_field}' 필드가 필요합니다.")

    if _find_index(records, item[id_field], id_field) != -1:
        raise ValueError(f"{id_field}={item[id_field]!r} 값이 이미 존재합니다.")

    records.append(item)
    save_json(records, file_path)
    return item


def read_all(file_path):
    """전체 레코드 목록을 반환한다."""
    return _load_records(file_path)


def read_by_id(file_path, id_value, id_field="id"):
    """id_field 값으로 레코드 하나를 찾는다. 없으면 None을 반환한다."""
    records = _load_records(file_path)
    index = _find_index(records, id_value, id_field)
    return records[index] if index != -1 else None


def update_item(file_path, id_value, updates, id_field="id"):
    """id_value에 해당하는 레코드의 필드를 updates 내용으로 수정한다.

    레코드가 없으면 None을 반환하고, id_field 자체는 수정하지 않는다.
    """
    records = _load_records(file_path)
    index = _find_index(records, id_value, id_field)
    if index == -1:
        return None

    updates = {k: v for k, v in updates.items() if k != id_field}
    records[index].update(updates)
    save_json(records, file_path)
    return records[index]


def delete_item(file_path, id_value, id_field="id"):
    """id_value에 해당하는 레코드를 삭제한다.

    삭제 전 존재 여부를 확인하므로, 없는 id를 지우려 해도 예외 없이 False를 반환한다.
    성공 시 True, 대상이 없으면 False.
    """
    records = _load_records(file_path)
    index = _find_index(records, id_value, id_field)
    if index == -1:
        return False

    del records[index]
    save_json(records, file_path)
    return True
