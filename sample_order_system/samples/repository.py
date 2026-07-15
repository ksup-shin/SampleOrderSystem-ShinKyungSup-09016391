"""시료(Sample) CRUD — poc_json 위의 얇은 도메인 래퍼."""

from poc_json import create_item, read_all, read_by_id

from ..paths import SAMPLES_FILE


def register_sample(
    sample_id, name, avg_production_time, yield_rate,
    initial_stock=0, file_path=SAMPLES_FILE,
):
    if not sample_id or not name:
        raise ValueError("시료 ID와 이름은 비어 있을 수 없습니다.")
    if avg_production_time <= 0:
        raise ValueError("평균 생산시간은 0보다 커야 합니다.")
    if not (0 < yield_rate <= 1):
        raise ValueError("수율은 0 초과 1 이하 값이어야 합니다.")
    if initial_stock < 0:
        raise ValueError("초기 재고는 0 이상이어야 합니다.")

    item = {
        "id": sample_id,
        "name": name,
        "avg_production_time": avg_production_time,
        "yield_rate": yield_rate,
        "stock": initial_stock,
    }
    return create_item(file_path, item)


def list_samples(file_path=SAMPLES_FILE):
    return read_all(file_path)


def search_samples(keyword, file_path=SAMPLES_FILE):
    keyword = keyword.lower()
    return [
        sample for sample in read_all(file_path)
        if keyword in sample["name"].lower()
    ]


def get_sample(sample_id, file_path=SAMPLES_FILE):
    return read_by_id(file_path, sample_id)
