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

- [x] 상태별 건수를 손으로 센 값과 비교, `REJECTED`는 집계에서 빠지는지 확인. (재현: 주문 3건 중 승인+출고 1건, 거절 1건, 예약 유지 1건 → `order_counts_by_status()` 결과 `{RESERVED:1, CONFIRMED:0, PRODUCING:0, RELEASE:1}`로 손으로 센 값과 일치, `REJECTED` 키 자체가 없음을 확인)
- [x] 재고 내림차순 정렬 확인. (재고 100/5/0인 시료 3개 등록 후 `stock_levels()` 결과가 90(출고 반영)/5/0 순서로 나옴을 확인)
- [x] 재고 0(고갈)/부족/여유 케이스 표시 확인. (동일 재현에서 `['여유', '부족', '고갈']` 순서로 정확히 분류됨을 assert로 확인)
- [ ] 콘솔 화면(표/진행바 등) 형태로 보기 좋게 나오는지는 Phase 7 콘솔 앱 완성 후 재검증 필요.
