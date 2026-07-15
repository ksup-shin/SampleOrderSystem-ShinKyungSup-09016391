"""생산 완료 시 재고 반영 + 주문 상태 전환을 담당하는 오케스트레이션."""

from poc_json import update_item

from ..paths import PRODUCTION_QUEUE_FILE, SAMPLES_FILE, ORDERS_FILE
from ..samples.repository import adjust_stock, get_sample
from . import queue


def advance_production(
    minutes, queue_file=PRODUCTION_QUEUE_FILE,
    samples_file=SAMPLES_FILE, orders_file=ORDERS_FILE,
):
    completed = queue.advance(minutes, file_path=queue_file)
    if completed is None:
        return None

    adjust_stock(completed["sample_id"], completed["actual_quantity"], file_path=samples_file)
    update_item(orders_file, completed["id"], {"status": "CONFIRMED"})
    return completed


def production_status(
    queue_file=PRODUCTION_QUEUE_FILE, samples_file=SAMPLES_FILE, **_ignored,
):
    """생산 큐를 시료 저장소와 조인해 콘솔에 보여줄 형태로 조립한다.

    반환값: {"current": {...} | None, "waiting": [...]}
    """
    items = queue.list_queue(file_path=queue_file)
    if not items:
        return {"current": None, "waiting": []}

    def sample_name(sample_id):
        sample = get_sample(sample_id, file_path=samples_file)
        return sample["name"] if sample else sample_id

    current_item = items[0]
    current_sample = get_sample(current_item["sample_id"], file_path=samples_file)
    remaining_minutes = current_item["total_minutes"] - current_item["elapsed_minutes"]
    current = {
        "order_id": current_item["id"],
        "sample_name": sample_name(current_item["sample_id"]),
        "order_quantity": current_item["order_quantity"],
        "stock": current_sample["stock"],
        "shortage": current_item["shortage"],
        "actual_quantity": current_item["actual_quantity"],
        "remaining_minutes": remaining_minutes,
    }

    waiting = []
    cumulative = remaining_minutes
    for sequence, item in enumerate(items[1:], start=1):
        cumulative += item["total_minutes"]
        waiting.append({
            "sequence": sequence,
            "order_id": item["id"],
            "sample_name": sample_name(item["sample_id"]),
            "order_quantity": item["order_quantity"],
            "shortage": item["shortage"],
            "actual_quantity": item["actual_quantity"],
            "estimated_minutes": cumulative,
        })

    return {"current": current, "waiting": waiting}
