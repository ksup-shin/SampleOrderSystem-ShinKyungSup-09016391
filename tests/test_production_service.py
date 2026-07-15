import pytest

from sample_order_system.samples.repository import register_sample, get_sample
from sample_order_system.orders.repository import reserve_order, get_order
from sample_order_system.orders.approval import approve_order
from sample_order_system.production.service import advance_production, production_status


@pytest.fixture
def files(tmp_path):
    return {
        "samples_file": tmp_path / "samples.json",
        "orders_file": tmp_path / "orders.json",
        "queue_file": tmp_path / "queue.json",
    }


def _producing_order(files, stock=30, quantity=200):
    register_sample("S-001", "A", 0.8, 0.92, initial_stock=stock, file_path=files["samples_file"])
    order = reserve_order(
        "S-001", "고객", quantity,
        orders_file=files["orders_file"], samples_file=files["samples_file"],
    )
    return approve_order(order["id"], **files)


def test_advance_production_returns_none_when_not_complete(files):
    order = _producing_order(files)

    result = advance_production(1, **files)

    assert result is None
    assert get_order(order["id"], file_path=files["orders_file"])["status"] == "PRODUCING"
    assert get_sample("S-001", file_path=files["samples_file"])["stock"] == 30


def test_advance_production_increments_stock_and_confirms_order_when_complete(files):
    order = _producing_order(files, stock=30, quantity=200)

    result = advance_production(10_000, **files)

    assert result["id"] == order["id"]
    assert get_order(order["id"], file_path=files["orders_file"])["status"] == "CONFIRMED"
    updated_sample = get_sample("S-001", file_path=files["samples_file"])
    assert updated_sample["stock"] == 30 + result["actual_quantity"]


def test_production_status_returns_none_current_and_empty_waiting_when_queue_empty(files):
    register_sample("S-001", "A", 0.8, 0.92, initial_stock=100, file_path=files["samples_file"])

    status = production_status(**files)

    assert status["current"] is None
    assert status["waiting"] == []


def test_production_status_enriches_current_item_with_sample_name_and_stock(files):
    order = _producing_order(files, stock=30, quantity=200)

    status = production_status(**files)

    current = status["current"]
    assert current["order_id"] == order["id"]
    assert current["sample_name"] == "A"
    assert current["stock"] == 30
    assert current["shortage"] == 170
    import math
    assert current["actual_quantity"] == math.ceil(170 / 0.92)
    assert current["remaining_minutes"] == pytest.approx(0.8 * math.ceil(170 / 0.92))


def test_production_status_computes_cumulative_estimated_minutes_for_waiting_items(files):
    register_sample("S-001", "A", 1.0, 1.0, initial_stock=0, file_path=files["samples_file"])
    order1 = reserve_order("S-001", "C1", 10, orders_file=files["orders_file"], samples_file=files["samples_file"])
    order2 = reserve_order("S-001", "C2", 20, orders_file=files["orders_file"], samples_file=files["samples_file"])
    approve_order(order1["id"], **files)  # total_minutes = 10
    approve_order(order2["id"], **files)  # total_minutes = 20

    status = production_status(**files)

    assert status["current"]["order_id"] == order1["id"]
    assert len(status["waiting"]) == 1
    waiting_item = status["waiting"][0]
    assert waiting_item["sequence"] == 1
    assert waiting_item["order_id"] == order2["id"]
    assert waiting_item["estimated_minutes"] == pytest.approx(10 + 20)
