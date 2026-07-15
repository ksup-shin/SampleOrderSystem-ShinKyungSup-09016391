# Phase 6 — 모니터링

`docs/PRD.md` 4.5절, `docs/PLAN.md` Phase 6을 상세화한 문서. "미출고 수요" 기준은 Phase 0 문서(§4)에서 확정: `RESERVED`+`PRODUCING`+`CONFIRMED` 주문 수량 합.

## 1. 모듈

`sample_order_system/monitoring/service.py`

```python
def order_counts_by_status() -> dict[str, int]
    # {"RESERVED": n, "CONFIRMED": n, "PRODUCING": n, "RELEASE": n}
    # REJECTED는 키 자체를 포함하지 않음

def stock_levels() -> list[dict]
    # [{"sample_id", "name", "stock", "demand", "level": "여유"|"부족"|"고갈"}, ...]
    # stock 내림차순 정렬
```

- `level` 판정 (Phase 0 §4 재확인):
  - `stock == 0` → `"고갈"`
  - `0 < stock < demand` → `"부족"`
  - `stock >= demand` (즉 `stock > 0`) → `"여유"`

## 2. TDD 테스트 목록 (`tests/test_monitoring_service.py`)

1. `test_order_counts_by_status_excludes_rejected`
2. `test_order_counts_by_status_counts_each_status_independently`
3. `test_stock_levels_classifies_ample_when_stock_covers_demand`
4. `test_stock_levels_classifies_low_when_stock_below_demand` (재고>0, 수요>재고)
5. `test_stock_levels_classifies_depleted_when_stock_is_zero`
6. `test_stock_levels_sorted_by_stock_descending`
7. `test_stock_levels_demand_ignores_released_and_rejected_orders` — RELEASE/REJECTED 상태 주문 수량은 demand에 포함되지 않는지.

## 3. 검증 방법 (사람이 직접 확인)

- [ ] 지금까지 만든 데이터 상태에서 `모니터링 → 주문량 확인` → 각 상태별 건수를 손으로 센 값과 비교, `REJECTED`는 집계에서 빠지는지 확인.
- [ ] `재고량 확인` → 재고 내림차순 정렬 확인.
- [ ] 재고 0(고갈)/부족/여유 케이스를 각각 하나씩 만들어 표시가 맞는지 확인.
