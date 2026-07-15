"""주문(Order) CRUD — 예약(Reserve) 및 조회."""

from poc_json import create_item, read_all, read_by_id

from ..paths import ORDERS_FILE, SAMPLES_FILE
from ..samples.repository import get_sample
from .numbering import next_order_id


def reserve_order(sample_id, customer, quantity, orders_file=ORDERS_FILE, samples_file=SAMPLES_FILE):
    if get_sample(sample_id, file_path=samples_file) is None:
        raise ValueError(f"등록되지 않은 시료 ID입니다: {sample_id!r}")
    if quantity <= 0:
        raise ValueError("주문 수량은 1 이상이어야 합니다.")

    existing = read_all(orders_file)
    order = {
        "id": next_order_id(existing),
        "sample_id": sample_id,
        "customer": customer,
        "quantity": quantity,
        "status": "RESERVED",
    }
    return create_item(orders_file, order)


def list_orders(status=None, file_path=ORDERS_FILE):
    orders = read_all(file_path)
    if status is None:
        return orders
    return [order for order in orders if order["status"] == status]


def get_order(order_id, file_path=ORDERS_FILE):
    return read_by_id(file_path, order_id)
