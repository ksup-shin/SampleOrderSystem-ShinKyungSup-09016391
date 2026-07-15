"""스키마 기반으로 테스트용 더미 데이터를 생성하고, poc_json 라이브러리를 통해
JSON 파일로 저장하는 라이브러리.

다른 프로젝트에서 사용하려면 이 dummy_data_generator 폴더와 poc_json 폴더를
함께 그대로 복사해 넣으면 된다 (poc_json의 save_json/load_json에 의존한다).

사용 예:

    from dummy_data_generator import generate_records, save_dummy_data

    schema = {
        "name": {"type": "name"},
        "age": {"type": "int", "min": 20, "max": 60},
        "email": {"type": "email"},
    }

    records = generate_records(schema, count=5, seed=42)
    save_dummy_data(schema, "users.json", count=5, seed=42)

콘솔 CLI:

    python -m dummy_data_generator.cli schema.json output.json --count 10
"""

from .generator import generate_record, generate_records, register_field_type
from .storage import load_dummy_data, save_dummy_data

__version__ = "0.1.0"

__all__ = [
    "generate_record",
    "generate_records",
    "register_field_type",
    "load_dummy_data",
    "save_dummy_data",
]
