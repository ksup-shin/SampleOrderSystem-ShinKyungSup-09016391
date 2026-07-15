"""생산 라인의 FIFO 큐. 진행 시간은 수동 tick(advance)으로 흐른다."""

import math

from poc_json import create_item, read_all, delete_item, update_item

from ..paths import PRODUCTION_QUEUE_FILE


def enqueue(
    order_id, sample_id, shortage, avg_production_time, yield_rate,
    order_quantity, file_path=PRODUCTION_QUEUE_FILE,
):
    actual_quantity = math.ceil(shortage / yield_rate)
    item = {
        "id": order_id,
        "sample_id": sample_id,
        "order_quantity": order_quantity,
        "shortage": shortage,
        "actual_quantity": actual_quantity,
        "total_minutes": avg_production_time * actual_quantity,
        "elapsed_minutes": 0,
    }
    return create_item(file_path, item)


def list_queue(file_path=PRODUCTION_QUEUE_FILE):
    return read_all(file_path)


def current_item(file_path=PRODUCTION_QUEUE_FILE):
    queue = list_queue(file_path=file_path)
    return queue[0] if queue else None


def estimate_wait_minutes(file_path=PRODUCTION_QUEUE_FILE):
    return sum(
        item["total_minutes"] - item["elapsed_minutes"]
        for item in list_queue(file_path=file_path)
    )


def advance(minutes, file_path=PRODUCTION_QUEUE_FILE):
    item = current_item(file_path=file_path)
    if item is None:
        return None

    elapsed = item["elapsed_minutes"] + minutes
    if elapsed >= item["total_minutes"]:
        delete_item(file_path, item["id"])
        item["elapsed_minutes"] = item["total_minutes"]
        return item

    update_item(file_path, item["id"], {"elapsed_minutes": elapsed})
    return None
