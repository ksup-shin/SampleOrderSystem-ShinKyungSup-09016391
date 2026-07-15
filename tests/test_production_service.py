import pytest

from sample_order_system.samples.repository import register_sample, get_sample
from sample_order_system.orders.repository import reserve_order, get_order
from sample_order_system.orders.approval import approve_order
from sample_order_system.production.service import advance_production


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
