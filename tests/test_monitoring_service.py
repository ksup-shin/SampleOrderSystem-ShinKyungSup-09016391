import pytest

from sample_order_system.samples.repository import register_sample
from sample_order_system.orders.repository import reserve_order
from sample_order_system.orders.approval import approve_order, reject_order
from sample_order_system.orders.shipment import ship_order
from sample_order_system.monitoring.service import order_counts_by_status, stock_levels


@pytest.fixture
def files(tmp_path):
    return {
        "samples_file": tmp_path / "samples.json",
        "orders_file": tmp_path / "orders.json",
        "queue_file": tmp_path / "queue.json",
    }


def test_order_counts_by_status_excludes_rejected(files):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=100, file_path=files["samples_file"])
    o1 = reserve_order("S-001", "c1", 10, orders_file=files["orders_file"], samples_file=files["samples_file"])
    reject_order(o1["id"], orders_file=files["orders_file"])

    counts = order_counts_by_status(orders_file=files["orders_file"])

    assert "REJECTED" not in counts


def test_order_counts_by_status_counts_each_status_independently(files):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=100, file_path=files["samples_file"])
    o1 = reserve_order("S-001", "c1", 10, orders_file=files["orders_file"], samples_file=files["samples_file"])
    o2 = reserve_order("S-001", "c2", 10, orders_file=files["orders_file"], samples_file=files["samples_file"])
    o3 = reserve_order("S-001", "c3", 200, orders_file=files["orders_file"], samples_file=files["samples_file"])
    approve_order(o1["id"], **files)  # sufficient stock -> CONFIRMED
    approve_order(o3["id"], **files)  # insufficient -> PRODUCING
    ship_order(o1["id"], orders_file=files["orders_file"], samples_file=files["samples_file"])

    counts = order_counts_by_status(orders_file=files["orders_file"])

    assert counts == {"RESERVED": 1, "CONFIRMED": 0, "PRODUCING": 1, "RELEASE": 1}


def test_stock_levels_classifies_ample_when_stock_covers_demand(files):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=100, file_path=files["samples_file"])
    reserve_order("S-001", "c1", 10, orders_file=files["orders_file"], samples_file=files["samples_file"])

    levels = stock_levels(samples_file=files["samples_file"], orders_file=files["orders_file"])

    assert levels[0]["level"] == "여유"


def test_stock_levels_classifies_low_when_stock_below_demand(files):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=5, file_path=files["samples_file"])
    reserve_order("S-001", "c1", 10, orders_file=files["orders_file"], samples_file=files["samples_file"])

    levels = stock_levels(samples_file=files["samples_file"], orders_file=files["orders_file"])

    assert levels[0]["level"] == "부족"


def test_stock_levels_classifies_depleted_when_stock_is_zero(files):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=0, file_path=files["samples_file"])

    levels = stock_levels(samples_file=files["samples_file"], orders_file=files["orders_file"])

    assert levels[0]["level"] == "고갈"


def test_stock_levels_sorted_by_stock_descending(files):
    register_sample("S-001", "Low", 0.5, 0.9, initial_stock=10, file_path=files["samples_file"])
    register_sample("S-002", "High", 0.5, 0.9, initial_stock=90, file_path=files["samples_file"])

    levels = stock_levels(samples_file=files["samples_file"], orders_file=files["orders_file"])

    assert [level["sample_id"] for level in levels] == ["S-002", "S-001"]


def test_stock_levels_demand_ignores_released_and_rejected_orders(files):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=100, file_path=files["samples_file"])
    o1 = reserve_order("S-001", "c1", 50, orders_file=files["orders_file"], samples_file=files["samples_file"])
    approve_order(o1["id"], **files)
    ship_order(o1["id"], orders_file=files["orders_file"], samples_file=files["samples_file"])
    o2 = reserve_order("S-001", "c2", 20, orders_file=files["orders_file"], samples_file=files["samples_file"])
    reject_order(o2["id"], orders_file=files["orders_file"])

    levels = stock_levels(samples_file=files["samples_file"], orders_file=files["orders_file"])

    assert levels[0]["demand"] == 0
