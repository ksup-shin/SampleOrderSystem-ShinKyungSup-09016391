import math

import pytest

from sample_order_system.production.queue import (
    enqueue,
    list_queue,
    current_item,
    estimate_wait_minutes,
    advance,
)


@pytest.fixture
def queue_file(tmp_path):
    return tmp_path / "production_queue.json"


def test_enqueue_computes_actual_quantity_with_ceil(queue_file):
    item = enqueue(
        "ORD-000001", "S-003", shortage=170,
        avg_production_time=0.8, yield_rate=0.92, order_quantity=200,
        file_path=queue_file,
    )

    assert item["actual_quantity"] == math.ceil(170 / 0.92)


def test_enqueue_computes_total_minutes(queue_file):
    item = enqueue(
        "ORD-000001", "S-003", shortage=170,
        avg_production_time=0.8, yield_rate=0.92, order_quantity=200,
        file_path=queue_file,
    )

    assert item["total_minutes"] == pytest.approx(0.8 * item["actual_quantity"])


def test_enqueue_starts_with_zero_elapsed_minutes(queue_file):
    item = enqueue(
        "ORD-000001", "S-003", shortage=170,
        avg_production_time=0.8, yield_rate=0.92, order_quantity=200,
        file_path=queue_file,
    )

    assert item["elapsed_minutes"] == 0


def test_list_queue_preserves_fifo_order(queue_file):
    enqueue("ORD-1", "S-001", 10, 1.0, 1.0, 10, file_path=queue_file)
    enqueue("ORD-2", "S-002", 20, 1.0, 1.0, 20, file_path=queue_file)
    enqueue("ORD-3", "S-003", 30, 1.0, 1.0, 30, file_path=queue_file)

    assert [item["id"] for item in list_queue(file_path=queue_file)] == [
        "ORD-1", "ORD-2", "ORD-3",
    ]


def test_current_item_is_the_first_enqueued(queue_file):
    enqueue("ORD-1", "S-001", 10, 1.0, 1.0, 10, file_path=queue_file)
    enqueue("ORD-2", "S-002", 20, 1.0, 1.0, 20, file_path=queue_file)

    assert current_item(file_path=queue_file)["id"] == "ORD-1"


def test_current_item_is_none_when_queue_empty(queue_file):
    assert current_item(file_path=queue_file) is None


def test_advance_accumulates_elapsed_minutes_without_completing(queue_file):
    enqueue("ORD-1", "S-001", 10, 2.0, 1.0, 10, file_path=queue_file)  # total_minutes=20

    completed = advance(5, file_path=queue_file)

    assert completed is None
    assert current_item(file_path=queue_file)["elapsed_minutes"] == 5


def test_advance_completes_and_removes_item_when_elapsed_reaches_total(queue_file):
    enqueue("ORD-1", "S-001", 10, 2.0, 1.0, 10, file_path=queue_file)  # total_minutes=20

    completed = advance(25, file_path=queue_file)

    assert completed["id"] == "ORD-1"
    assert list_queue(file_path=queue_file) == []


def test_advance_promotes_next_item_after_completion(queue_file):
    enqueue("ORD-1", "S-001", 10, 2.0, 1.0, 10, file_path=queue_file)  # total_minutes=20
    enqueue("ORD-2", "S-002", 20, 1.0, 1.0, 20, file_path=queue_file)  # total_minutes=20

    advance(25, file_path=queue_file)

    assert current_item(file_path=queue_file)["id"] == "ORD-2"


def test_estimate_wait_minutes_sums_remaining_time_of_all_items(queue_file):
    enqueue("ORD-1", "S-001", 10, 2.0, 1.0, 10, file_path=queue_file)  # total_minutes=20
    enqueue("ORD-2", "S-002", 20, 1.0, 1.0, 20, file_path=queue_file)  # total_minutes=20
    advance(5, file_path=queue_file)  # ORD-1 elapsed=5, remaining=15

    assert estimate_wait_minutes(file_path=queue_file) == pytest.approx(15 + 20)


def test_advance_on_empty_queue_returns_none(queue_file):
    assert advance(10, file_path=queue_file) is None
