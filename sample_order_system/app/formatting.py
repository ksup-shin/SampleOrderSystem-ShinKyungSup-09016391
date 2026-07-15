"""콘솔 출력용 순수 포맷팅 함수 (I/O 없음, pytest로 직접 검증 가능).

모든 목록/현황 출력은 컬럼 제목이 있는 표(render_table)로 나온다.
한글은 터미널에서 영문의 2배 폭을 차지하므로 east_asian_width 기준으로 정렬한다.
"""

import unicodedata


def _display_width(text):
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in str(text))


def _pad(text, width):
    return str(text) + " " * (width - _display_width(text))


def render_table(headers, rows):
    str_rows = [[str(value) for value in row] for row in rows]
    widths = [_display_width(header) for header in headers]
    for row in str_rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], _display_width(value))

    lines = [" | ".join(_pad(h, widths[i]) for i, h in enumerate(headers))]
    lines.append("-+-".join("-" * w for w in widths))
    for row in str_rows:
        lines.append(" | ".join(_pad(v, widths[i]) for i, v in enumerate(row)))
    return "\n".join(lines)


def format_summary(samples, orders, queue):
    return {
        "sample_count": len(samples),
        "total_stock": sum(sample["stock"] for sample in samples),
        "order_count": len(orders),
        "queue_length": len(queue),
    }


SAMPLES_HEADERS = ["시료 ID", "이름", "평균 생산시간(분)", "수율", "재고"]


def format_samples_table(samples):
    rows = [
        [s["id"], s["name"], s["avg_production_time"], s["yield_rate"], s["stock"]]
        for s in samples
    ]
    return render_table(SAMPLES_HEADERS, rows)


ORDERS_HEADERS = ["주문 번호", "시료 ID", "고객명", "수량", "상태"]


def _order_row(order):
    return [order["id"], order["sample_id"], order["customer"], order["quantity"], order["status"]]


def format_orders_table(orders):
    return render_table(ORDERS_HEADERS, [_order_row(o) for o in orders])


def format_indexed_orders_table(orders):
    headers = ["번호", *ORDERS_HEADERS]
    rows = [[index, *_order_row(order)] for index, order in enumerate(orders, start=1)]
    return render_table(headers, rows)


def format_order_counts_table(counts):
    return render_table(["상태", "건수"], list(counts.items()))


def format_stock_levels_table(levels):
    headers = ["시료 ID", "이름", "재고", "수요", "상태"]
    rows = [[lvl["sample_id"], lvl["name"], lvl["stock"], lvl["demand"], lvl["level"]] for lvl in levels]
    return render_table(headers, rows)


def format_production_current_table(current):
    headers = ["주문 번호", "시료 이름", "주문량", "재고량", "부족량", "실 생산량", "완료 예정 시간(분)"]
    row = [
        current["order_id"], current["sample_name"], current["order_quantity"],
        current["stock"], current["shortage"], current["actual_quantity"],
        f"{current['remaining_minutes']:.1f}",
    ]
    return render_table(headers, [row])


def format_production_waiting_table(waiting):
    headers = ["순서", "주문 번호", "시료 이름", "주문량", "부족분", "실 생산량", "예상 완료 시간(분)"]
    rows = [
        [
            item["sequence"], item["order_id"], item["sample_name"], item["order_quantity"],
            item["shortage"], item["actual_quantity"], f"{item['estimated_minutes']:.1f}",
        ]
        for item in waiting
    ]
    return render_table(headers, rows)
