import pytest

from sample_order_system.samples.repository import register_sample, get_sample
from sample_order_system.orders.repository import reserve_order
from sample_order_system.orders.approval import approve_order
from sample_order_system.orders.shipment import list_shippable_orders, ship_order
from poc_json import update_item


@pytest.fixture
def files(tmp_path):
    return {
        "samples_file": tmp_path / "samples.json",
        "orders_file": tmp_path / "orders.json",
        "queue_file": tmp_path / "queue.json",
    }


def _confirmed_order(files, stock=100, quantity=50):
    register_sample("S-001", "A", 0.5, 0.9, initial_stock=stock, file_path=files["samples_file"])
    order = reserve_order(
        "S-001", "고객", quantity,
        orders_file=files["orders_file"], samples_file=files["samples_file"],
    )
    return approve_order(order["id"], **files)


def test_list_shippable_orders_returns_only_confirmed(files):
    confirmed = _confirmed_order(files)
    reserved = reserve_order(
        "S-001", "다른고객", 5,
        orders_file=files["orders_file"], samples_file=files["samples_file"],
    )

    shippable = list_shippable_orders(orders_file=files["orders_file"])

    assert [o["id"] for o in shippable] == [confirmed["id"]]


def test_ship_order_transitions_to_release(files):
    confirmed = _confirmed_order(files)

    shipped = ship_order(
        confirmed["id"], orders_file=files["orders_file"], samples_file=files["samples_file"],
    )

    assert shipped["status"] == "RELEASE"


def test_ship_order_decrements_sample_stock_by_quantity(files):
    confirmed = _confirmed_order(files, stock=100, quantity=50)

    ship_order(
        confirmed["id"], orders_file=files["orders_file"], samples_file=files["samples_file"],
    )

    assert get_sample("S-001", file_path=files["samples_file"])["stock"] == 50


@pytest.mark.parametrize("status", ["RESERVED", "PRODUCING", "REJECTED", "RELEASE"])
def test_ship_order_rejects_when_not_confirmed(files, status):
    confirmed = _confirmed_order(files)
    update_item(files["orders_file"], confirmed["id"], {"status": status})

    with pytest.raises(ValueError):
        ship_order(
            confirmed["id"], orders_file=files["orders_file"], samples_file=files["samples_file"],
        )
