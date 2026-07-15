# Phase 2 — 주문 예약(Reserve)

`docs/PRD.md` 4.3절, `docs/PLAN.md` Phase 2를 상세화한 문서.

## 1. 모듈

`sample_order_system/orders/numbering.py`

```python
def next_order_id(existing_orders: list[dict]) -> str
    # "ORD-000001" 형식, 기존 최댓값 + 1
```

`sample_order_system/orders/repository.py`

```python
def reserve_order(sample_id: str, customer: str, quantity: int) -> dict
def list_orders(status: str | None = None) -> list[dict]
def get_order(order_id: str) -> dict | None
```

- `reserve_order`는 내부에서 `samples.repository.get_sample(sample_id)`로 존재 여부를 확인한다. 없으면 `ValueError`.
- `quantity`는 1 이상 정수, 아니면 `ValueError`.
- 생성된 레코드는 `status="RESERVED"`로 `orders.json`에 저장.

## 2. TDD 테스트 목록 (`tests/test_orders_repository.py`, `tests/test_order_numbering.py`)

1. `test_next_order_id_starts_at_000001_when_empty`
2. `test_next_order_id_increments_from_max_existing`
3. `test_reserve_order_creates_reserved_order` — 반환값과 저장된 레코드 상태가 `RESERVED`인지.
4. `test_reserve_order_rejects_unknown_sample` — 등록되지 않은 `sample_id` → `ValueError`.
5. `test_reserve_order_rejects_non_positive_quantity` — `quantity<=0` → `ValueError` (parametrize: 0, -1).
6. `test_list_orders_filters_by_status` — 여러 상태가 섞였을 때 `status="RESERVED"`로 필터링되는지.
7. `test_get_order_returns_none_when_missing`

## 3. 검증 방법 (사람이 직접 확인)

- [ ] Phase 1에서 등록한 시료 ID로 주문(고객 "삼성전자 파운드리", 수량 200) 생성 → 주문번호 + `RESERVED` 상태 확인.
- [ ] 없는 시료 ID(`S-999`)로 주문 시도 → 에러로 거부.
- [ ] `poc_json.admin_tool data/orders.json`의 `list`로 저장된 내용 확인.
