"""주문 승인/거절 — 재고 판정에 따른 CONFIRMED/PRODUCING 분기."""

import math

from poc_json import read_by_id, update_item

from ..paths import ORDERS_FILE, SAMPLES_FILE, PRODUCTION_QUEUE_FILE
from ..samples.repository import get_sample
from ..production.queue import enqueue, estimate_wait_minutes


def _require_reserved_order(order):
    if order is None:
        raise ValueError("주문을 찾을 수 없습니다.")
    if order["status"] != "RESERVED":
        raise ValueError(
            f"RESERVED 상태의 주문만 처리할 수 있습니다 (현재 상태: {order['status']})"
        )
    return order


def preview_approval(
    order_id, orders_file=ORDERS_FILE, samples_file=SAMPLES_FILE,
    queue_file=PRODUCTION_QUEUE_FILE,
):
    order = _require_reserved_order(read_by_id(orders_file, order_id))
    sample = get_sample(order["sample_id"], file_path=samples_file)
    shortage = max(0, order["quantity"] - sample["stock"])

    estimated_minutes = None
    if shortage > 0:
        actual_quantity = math.ceil(shortage / sample["yield_rate"])
        this_order_minutes = sample["avg_production_time"] * actual_quantity
        estimated_minutes = (
            estimate_wait_minutes(file_path=queue_file) + this_order_minutes
        )

    return {
        "sample": sample,
        "shortage": shortage,
        "stock": sample["stock"],
        "estimated_minutes": estimated_minutes,
    }


def approve_order(
    order_id, orders_file=ORDERS_FILE, samples_file=SAMPLES_FILE,
    queue_file=PRODUCTION_QUEUE_FILE,
):
    order = _require_reserved_order(read_by_id(orders_file, order_id))
    sample = get_sample(order["sample_id"], file_path=samples_file)
    shortage = max(0, order["quantity"] - sample["stock"])

    if shortage > 0:
        enqueue(
            order_id, sample["id"], shortage,
            sample["avg_production_time"], sample["yield_rate"],
            order["quantity"], file_path=queue_file,
        )
        new_status = "PRODUCING"
    else:
        new_status = "CONFIRMED"

    return update_item(orders_file, order_id, {"status": new_status})


def reject_order(order_id, orders_file=ORDERS_FILE):
    _require_reserved_order(read_by_id(orders_file, order_id))
    return update_item(orders_file, order_id, {"status": "REJECTED"})
