import math

import pytest

from sample_order_system.samples.repository import register_sample
from sample_order_system.orders.repository import reserve_order
from sample_order_system.orders.approval import (
    preview_approval,
    approve_order,
    reject_order,
)
from sample_order_system.production.queue import list_queue


@pytest.fixture
def files(tmp_path):
    return {
        "samples_file": tmp_path / "samples.json",
        "orders_file": tmp_path / "orders.json",
        "queue_file": tmp_path / "queue.json",
    }


def _reserve(files, stock, quantity):
    register_sample(
        "S-001", "실리콘 웨이퍼-8인치", 0.8, 0.92,
        initial_stock=stock, file_path=files["samples_file"],
    )
    return reserve_order(
        "S-001", "고객", quantity,
        orders_file=files["orders_file"], samples_file=files["samples_file"],
    )


def test_preview_approval_reports_no_shortage_when_stock_sufficient(files):
    order = _reserve(files, stock=100, quantity=50)

    preview = preview_approval(order["id"], **files)

    assert preview["shortage"] == 0
    assert preview["stock"] == 100
    assert preview["estimated_minutes"] is None


def test_preview_approval_reports_shortage_and_estimated_minutes_when_insufficient(files):
    order = _reserve(files, stock=30, quantity=200)

    preview = preview_approval(order["id"], **files)

    actual_quantity = math.ceil(170 / 0.92)
    assert preview["shortage"] == 170
    assert preview["estimated_minutes"] == pytest.approx(0.8 * actual_quantity)


def test_approve_order_confirms_immediately_when_stock_sufficient(files):
    order = _reserve(files, stock=100, quantity=50)

    updated = approve_order(order["id"], **files)

    assert updated["status"] == "CONFIRMED"
    assert list_queue(file_path=files["queue_file"]) == []


def test_approve_order_enqueues_production_and_marks_producing_when_insufficient(files):
    order = _reserve(files, stock=30, quantity=200)

    updated = approve_order(order["id"], **files)

    assert updated["status"] == "PRODUCING"
    queue = list_queue(file_path=files["queue_file"])
    assert len(queue) == 1
    assert queue[0]["id"] == order["id"]


def test_approve_order_does_not_change_stock_immediately(files):
    order = _reserve(files, stock=30, quantity=200)

    approve_order(order["id"], **files)

    from sample_order_system.samples.repository import get_sample
    sample = get_sample("S-001", file_path=files["samples_file"])
    assert sample["stock"] == 30


def test_reject_order_marks_rejected(files):
    order = _reserve(files, stock=100, quantity=50)

    updated = reject_order(order["id"], orders_file=files["orders_file"])

    assert updated["status"] == "REJECTED"


@pytest.mark.parametrize("final_status", ["CONFIRMED", "REJECTED"])
def test_approve_order_rejects_when_order_not_reserved(files, final_status):
    order = _reserve(files, stock=100, quantity=50)
    from poc_json import update_item
    update_item(files["orders_file"], order["id"], {"status": final_status})

    with pytest.raises(ValueError):
        approve_order(order["id"], **files)


@pytest.mark.parametrize("final_status", ["CONFIRMED", "REJECTED"])
def test_reject_order_rejects_when_order_not_reserved(files, final_status):
    order = _reserve(files, stock=100, quantity=50)
    from poc_json import update_item
    update_item(files["orders_file"], order["id"], {"status": final_status})

    with pytest.raises(ValueError):
        reject_order(order["id"], orders_file=files["orders_file"])
