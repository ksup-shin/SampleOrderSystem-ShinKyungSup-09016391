"""모니터링 — 상태별 주문 집계, 시료별 재고 상태 분류."""

from poc_json import read_all

from ..paths import ORDERS_FILE, SAMPLES_FILE

_TRACKED_STATUSES = ("RESERVED", "CONFIRMED", "PRODUCING", "RELEASE")
_DEMAND_STATUSES = ("RESERVED", "PRODUCING", "CONFIRMED")


def order_counts_by_status(orders_file=ORDERS_FILE):
    orders = read_all(orders_file)
    return {
        status: sum(1 for order in orders if order["status"] == status)
        for status in _TRACKED_STATUSES
    }


def _demand_by_sample(orders):
    demand = {}
    for order in orders:
        if order["status"] in _DEMAND_STATUSES:
            demand[order["sample_id"]] = demand.get(order["sample_id"], 0) + order["quantity"]
    return demand


def _classify(stock, demand):
    if stock == 0:
        return "고갈"
    if stock < demand:
        return "부족"
    return "여유"


def stock_levels(samples_file=SAMPLES_FILE, orders_file=ORDERS_FILE):
    demand_by_sample = _demand_by_sample(read_all(orders_file))
    samples = read_all(samples_file)

    levels = [
        {
            "sample_id": sample["id"],
            "name": sample["name"],
            "stock": sample["stock"],
            "demand": demand_by_sample.get(sample["id"], 0),
            "level": _classify(sample["stock"], demand_by_sample.get(sample["id"], 0)),
        }
        for sample in samples
    ]
    return sorted(levels, key=lambda level: level["stock"], reverse=True)
