import pytest

from sample_order_system.samples.repository import register_sample
from sample_order_system.orders.repository import (
    reserve_order,
    list_orders,
    get_order,
)


@pytest.fixture
def samples_file(tmp_path):
    return tmp_path / "samples.json"


@pytest.fixture
def orders_file(tmp_path):
    return tmp_path / "orders.json"


@pytest.fixture
def registered_sample(samples_file):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, initial_stock=100, file_path=samples_file)
    return "S-001"


def test_reserve_order_creates_reserved_order(samples_file, orders_file, registered_sample):
    order = reserve_order(
        registered_sample, "삼성전자 파운드리", 200,
        orders_file=orders_file, samples_file=samples_file,
    )

    assert order["status"] == "RESERVED"
    assert order["sample_id"] == "S-001"
    assert order["customer"] == "삼성전자 파운드리"
    assert order["quantity"] == 200
    assert get_order(order["id"], file_path=orders_file)["status"] == "RESERVED"


def test_reserve_order_rejects_unknown_sample(samples_file, orders_file):
    with pytest.raises(ValueError):
        reserve_order("S-999", "고객", 10, orders_file=orders_file, samples_file=samples_file)


@pytest.mark.parametrize("quantity", [0, -1])
def test_reserve_order_rejects_non_positive_quantity(
    samples_file, orders_file, registered_sample, quantity
):
    with pytest.raises(ValueError):
        reserve_order(
            registered_sample, "고객", quantity,
            orders_file=orders_file, samples_file=samples_file,
        )


def test_list_orders_filters_by_status(samples_file, orders_file, registered_sample):
    reserve_order(registered_sample, "A", 10, orders_file=orders_file, samples_file=samples_file)
    reserve_order(registered_sample, "B", 20, orders_file=orders_file, samples_file=samples_file)

    reserved = list_orders(status="RESERVED", file_path=orders_file)
    confirmed = list_orders(status="CONFIRMED", file_path=orders_file)

    assert len(reserved) == 2
    assert confirmed == []


def test_get_order_returns_none_when_missing(orders_file):
    assert get_order("ORD-999999", file_path=orders_file) is None
