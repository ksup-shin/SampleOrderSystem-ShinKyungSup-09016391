"""생성된 더미 데이터를 poc_json 라이브러리를 통해 JSON 파일로 저장/조회한다."""

from poc_json.json_lib import load_json, save_json

from .generator import generate_records


def save_dummy_data(schema, file_path, count, seed=None, id_field="id", start_id=1):
    """스키마로 더미 데이터를 생성한 뒤 poc_json.save_json으로 파일에 저장한다.

    반환값은 저장된 레코드 목록이다.
    """
    records = generate_records(
        schema, count, seed=seed, id_field=id_field, start_id=start_id
    )
    save_json(records, file_path)
    return records


def load_dummy_data(file_path):
    """poc_json.load_json으로 저장된 더미 데이터를 읽어온다."""
    return load_json(file_path)
