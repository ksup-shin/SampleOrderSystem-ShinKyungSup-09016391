"""생산 완료 시 재고 반영 + 주문 상태 전환을 담당하는 오케스트레이션."""

from poc_json import update_item

from ..paths import PRODUCTION_QUEUE_FILE, SAMPLES_FILE, ORDERS_FILE
from ..samples.repository import adjust_stock
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
