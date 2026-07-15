# Phase 5 — 출고 처리

`docs/PRD.md` 4.7절, `docs/PLAN.md` Phase 5를 상세화한 문서.

## 1. 모듈

`sample_order_system/orders/shipment.py`

```python
def list_shippable_orders() -> list[dict]   # status == "CONFIRMED"
def ship_order(order_id: str) -> dict
    # order.status -> "RELEASE"
    # samples.repository의 재고를 order.quantity 만큼 차감
    # order가 CONFIRMED가 아니면 ValueError
```

- 재고 차감 후 음수가 되면 데이터 정합성 문제이므로 `AssertionError`(또는 `ValueError`)로 방어(정상 흐름에서는 발생하지 않아야 함 — Phase 3/4 로직이 올바르면 CONFIRMED 시점엔 항상 재고가 충분).

## 2. TDD 테스트 목록 (`tests/test_order_shipment.py`)

1. `test_list_shippable_orders_returns_only_confirmed`
2. `test_ship_order_transitions_to_release`
3. `test_ship_order_decrements_sample_stock_by_quantity`
4. `test_ship_order_rejects_when_not_confirmed` — `RESERVED`/`PRODUCING`/`REJECTED`/`RELEASE` 상태에서 시도 시 `ValueError` (parametrize).

## 3. 검증 방법 (사람이 직접 확인)

- [x] `CONFIRMED`가 된 주문이 `출고 처리` 목록에 나오는지. (재현 확인: 재고 100/주문 50 승인 후 `list_shippable_orders()`에 해당 주문번호가 나옴)
- [x] 출고 실행 전후로 재고가 정확히 주문 수량만큼 줄어드는지. (출고 전 100 → 출고 후 50 확인, `adjust_stock` 단위 테스트로도 증감 검증)
- [x] 출고 후 상태가 `RELEASE`로 바뀌고, 다시 출고 목록에는 나타나지 않는지. (재현 확인)
- [x] 재고가 음수가 되지 않는지. (`adjust_stock`이 결과가 음수가 되면 `ValueError`를 던지도록 방어 로직을 추가하고 테스트로 검증. 다만 이는 방어적 안전장치일 뿐이며, 실제로 이 경로를 타는 것은 Phase 3/4 로직에 결함이 있다는 뜻이므로 정상 흐름에서는 발생하면 안 됨.)
- [ ] 콘솔 화면에서 번호/주문번호/고객/시료이름/수량 형식으로 표시되는지 — Phase 7 콘솔 앱 완성 후 재검증 필요.
