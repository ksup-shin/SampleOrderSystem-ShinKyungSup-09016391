from sample_order_system.app.formatting import format_sample_row, format_summary, format_queue_row


def test_format_sample_row_includes_all_five_fields():
    sample = {
        "id": "S-001", "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5, "yield_rate": 0.92, "stock": 480,
    }

    row = format_sample_row(sample)

    assert "S-001" in row
    assert "실리콘 웨이퍼-8인치" in row
    assert "0.5" in row
    assert "0.92" in row
    assert "480" in row


def test_format_summary_counts_registered_samples_and_total_stock():
    samples = [
        {"id": "S-001", "stock": 100},
        {"id": "S-002", "stock": 50},
    ]
    orders = [{"status": "RESERVED"}, {"status": "RELEASE"}]
    queue = [{"id": "ORD-1"}]

    summary = format_summary(samples, orders, queue)

    assert summary["sample_count"] == 2
    assert summary["total_stock"] == 150
    assert summary["order_count"] == 2
    assert summary["queue_length"] == 1


def test_format_queue_row_shows_progress_percent_and_remaining_minutes():
    item = {
        "id": "ORD-000001", "sample_id": "S-001", "order_quantity": 200,
        "shortage": 170, "actual_quantity": 185,
        "total_minutes": 148.0, "elapsed_minutes": 37.0,
    }

    row = format_queue_row(item)

    assert "25%" in row
    assert "111.0" in row  # 남은 시간 = 148.0 - 37.0
    assert "ORD-000001" in row
    assert "185" in row
