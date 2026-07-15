from sample_order_system.orders.numbering import next_order_id


def test_next_order_id_starts_at_000001_when_empty():
    assert next_order_id([]) == "ORD-000001"


def test_next_order_id_increments_from_max_existing():
    existing = [{"id": "ORD-000001"}, {"id": "ORD-000003"}, {"id": "ORD-000002"}]

    assert next_order_id(existing) == "ORD-000004"
