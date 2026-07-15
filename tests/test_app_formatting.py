from sample_order_system.app.formatting import (
    render_table,
    format_summary,
    format_samples_table,
    format_orders_table,
    format_indexed_orders_table,
    format_order_counts_table,
    format_stock_levels_table,
    format_production_current_table,
    format_production_waiting_table,
)


def test_render_table_aligns_headers_and_rows_with_korean_width():
    table = render_table(["이름", "수량"], [["실리콘", 10], ["GaN", 5]])

    lines = table.splitlines()
    assert lines[0].startswith("이름")
    assert "수량" in lines[0]
    assert any("실리콘" in line and "10" in line for line in lines)
    assert any("GaN" in line and "5" in line for line in lines)


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


def test_format_samples_table_has_korean_headers():
    samples = [{
        "id": "S-001", "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5, "yield_rate": 0.92, "stock": 480,
    }]

    table = format_samples_table(samples)

    header = table.splitlines()[0]
    assert "시료 ID" in header
    assert "이름" in header
    assert "평균 생산시간" in header
    assert "수율" in header
    assert "재고" in header
    assert "S-001" in table
    assert "실리콘 웨이퍼-8인치" in table


def test_format_orders_table_has_korean_headers():
    orders = [{
        "id": "ORD-000001", "sample_id": "S-001",
        "customer": "삼성전자", "quantity": 200, "status": "RESERVED",
    }]

    table = format_orders_table(orders)

    header = table.splitlines()[0]
    assert "주문 번호" in header
    assert "시료 ID" in header
    assert "고객명" in header
    assert "수량" in header
    assert "상태" in header
    assert "ORD-000001" in table


def test_format_indexed_orders_table_prefixes_row_number():
    orders = [
        {"id": "ORD-000001", "sample_id": "S-001", "customer": "A", "quantity": 10, "status": "RESERVED"},
        {"id": "ORD-000002", "sample_id": "S-001", "customer": "B", "quantity": 20, "status": "RESERVED"},
    ]

    table = format_indexed_orders_table(orders)

    header = table.splitlines()[0]
    assert "번호" in header
    lines = table.splitlines()
    assert any(line.strip().startswith("1") and "ORD-000001" in line for line in lines)
    assert any(line.strip().startswith("2") and "ORD-000002" in line for line in lines)


def test_format_order_counts_table_has_korean_headers():
    counts = {"RESERVED": 1, "CONFIRMED": 2, "PRODUCING": 0, "RELEASE": 3}

    table = format_order_counts_table(counts)

    header = table.splitlines()[0]
    assert "상태" in header
    assert "건수" in header
    assert "RESERVED" in table
    assert "1" in table


def test_format_stock_levels_table_has_korean_headers():
    levels = [{"sample_id": "S-001", "name": "A", "stock": 10, "demand": 5, "level": "여유"}]

    table = format_stock_levels_table(levels)

    header = table.splitlines()[0]
    assert "시료 ID" in header
    assert "이름" in header
    assert "재고" in header
    assert "수요" in header
    assert "상태" in header
    assert "여유" in table


def test_format_production_current_table_has_korean_headers():
    current = {
        "order_id": "ORD-000001", "sample_name": "실리콘 웨이퍼", "order_quantity": 200,
        "stock": 30, "shortage": 170, "actual_quantity": 185, "remaining_minutes": 111.0,
    }

    table = format_production_current_table(current)

    header = table.splitlines()[0]
    assert "주문 번호" in header
    assert "시료 이름" in header
    assert "주문량" in header
    assert "재고량" in header
    assert "부족량" in header
    assert "실 생산량" in header
    assert "완료 예정 시간" in header
    assert "ORD-000001" in table


def test_format_production_waiting_table_has_korean_headers():
    waiting = [{
        "sequence": 1, "order_id": "ORD-000002", "sample_name": "GaN",
        "order_quantity": 50, "shortage": 20, "actual_quantity": 22, "estimated_minutes": 200.0,
    }]

    table = format_production_waiting_table(waiting)

    header = table.splitlines()[0]
    assert "순서" in header
    assert "주문 번호" in header
    assert "시료 이름" in header
    assert "주문량" in header
    assert "부족분" in header
    assert "실 생산량" in header
    assert "예상 완료 시간" in header
    assert "ORD-000002" in table
