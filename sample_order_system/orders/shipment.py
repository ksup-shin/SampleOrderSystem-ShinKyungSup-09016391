"""출고 처리 — CONFIRMED 주문을 RELEASE로 전환하고 재고를 차감한다."""

from poc_json import read_by_id, update_item

from ..paths import ORDERS_FILE, SAMPLES_FILE
from ..samples.repository import adjust_stock
from .repository import list_orders


def list_shippable_orders(orders_file=ORDERS_FILE):
    return list_orders(status="CONFIRMED", file_path=orders_file)


def ship_order(order_id, orders_file=ORDERS_FILE, samples_file=SAMPLES_FILE):
    order = read_by_id(orders_file, order_id)
    if order is None or order["status"] != "CONFIRMED":
        status = order["status"] if order else "없음"
        raise ValueError(f"CONFIRMED 상태의 주문만 출고할 수 있습니다 (현재 상태: {status})")

    adjust_stock(order["sample_id"], -order["quantity"], file_path=samples_file)
    return update_item(orders_file, order_id, {"status": "RELEASE"})
