# Phase 3 — 주문 승인/거절

`docs/PRD.md` 4.4절, `docs/PLAN.md` Phase 3을 상세화한 문서. 재고 판정과 생산 큐 등록이 갈리는 핵심 분기점.

## 1. 모듈

`sample_order_system/orders/approval.py`

```python
def preview_approval(order_id: str) -> dict
    # {"sample": {...}, "shortage": int, "stock": int,
    #  "estimated_minutes": float | None}   # 부족하지 않으면 None

def approve_order(order_id: str) -> dict
    # 재고 충분 -> status="CONFIRMED"
    # 재고 부족 -> status="PRODUCING", production.queue.enqueue(...) 호출
    # 반환값: 갱신된 order 레코드

def reject_order(order_id: str) -> dict
    # status="REJECTED"
```

- `preview_approval`/`approve_order`/`reject_order`는 대상 주문이 `RESERVED`가 아니면 `ValueError` (이미 처리된 주문 재처리 방지).
- `shortage = max(0, quantity - stock)`.
- `estimated_minutes`(부족한 경우만): "현재 생산 큐에 이미 대기 중인 모든 항목의 총 생산시간 합 + 이번 건 총 생산시간"(Phase 4의 `production.queue.estimate_wait_minutes()` 사용, FIFO이므로 맨 뒤에 붙는다고 가정하고 미리보기).

## 2. TDD 테스트 목록 (`tests/test_order_approval.py`)

1. `test_preview_approval_reports_no_shortage_when_stock_sufficient`
2. `test_preview_approval_reports_shortage_and_estimated_minutes_when_stock_insufficient`
3. `test_approve_order_confirms_immediately_when_stock_sufficient` — 상태가 `CONFIRMED`, 생산 큐에는 등록되지 않음.
4. `test_approve_order_enqueues_production_and_marks_producing_when_stock_insufficient` — 상태가 `PRODUCING`, 생산 큐에 정확히 1건 등록.
5. `test_approve_order_does_not_change_stock_immediately` — 승인 직후에는 재고가 변하지 않음(차감은 출고, 증가는 생산완료 시점).
6. `test_reject_order_marks_rejected`
7. `test_approve_order_rejects_when_order_not_reserved` — 이미 `CONFIRMED`/`REJECTED` 등인 주문에 다시 승인 시도 → `ValueError` (parametrize).
8. `test_reject_order_rejects_when_order_not_reserved` — 동일하게 거절도 재처리 방지.

## 3. 검증 방법 (사람이 직접 확인)

- [x] **재고 충분**: 재고를 주문 수량 이상으로 맞춘 뒤 승인 → `CONFIRMED`로 즉시 전환, 재고는 그대로. (재고 100/주문 50로 재현 — `approve_order` 결과 `CONFIRMED`, 생산 큐 `[]` 확인)
- [x] **재고 부족**: 재고보다 큰 수량 주문 → 승인 화면에서 부족분/예상 소요시간 확인 → 승인 후 `PRODUCING`, 생산 큐에 등록됨. (재고 30/주문 200으로 재현 — `preview_approval`에서 부족분 170, 예상소요시간 148.0분(=0.8×ceil(170/0.92)) 확인, 승인 후 상태 `PRODUCING`, 큐에 1건 등록, 재고는 30 그대로 유지됨을 확인. 단, "생산 큐 화면"은 Phase 7 콘솔 앱 완성 후 별도로 시각적 확인 필요.)
- [x] **거절**: `RESERVED` 주문 거절 → `REJECTED`로 전환. (재현 확인)
- [x] 이미 처리된 주문을 다시 선택하면 에러로 막히는지 확인. (거절된 주문을 다시 승인 시도 → `ValueError` 발생 확인. "목록에 없는지"는 콘솔 UI의 목록 필터링 로직이라 Phase 7에서 재검증 필요.)
