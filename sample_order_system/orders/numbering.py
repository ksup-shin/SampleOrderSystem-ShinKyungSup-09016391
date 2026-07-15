"""주문번호 채번 규칙: ORD-000001 형식."""

PREFIX = "ORD-"
WIDTH = 6


def next_order_id(existing_orders):
    max_seq = 0
    for order in existing_orders:
        seq = int(order["id"][len(PREFIX):])
        max_seq = max(max_seq, seq)
    return f"{PREFIX}{max_seq + 1:0{WIDTH}d}"
