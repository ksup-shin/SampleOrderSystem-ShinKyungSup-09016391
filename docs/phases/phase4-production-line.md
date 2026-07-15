# Phase 4 — 생산 라인 (FIFO)

`docs/PRD.md` 4.6절, `docs/PLAN.md` Phase 4를 상세화한 문서. Phase 0에서 결정한 "수동 tick" 방식을 사용한다.

## 1. 생산 큐 항목 스키마

생산 큐 자체는 `data/production_queue.json`(id_field=`"id"`, id는 `order_id`와 동일하게 사용)에 저장한다.

| 필드 | 설명 |
| --- | --- |
| `id` (=`order_id`) | 연결된 주문번호 |
| `sample_id` | 시료 ID |
| `order_quantity` | 주문 수량 |
| `shortage` | 부족분 (`quantity - stock`, 등록 시점 값 고정) |
| `actual_quantity` | 실 생산량 = `ceil(shortage / yield_rate)` |
| `total_minutes` | 총 생산 시간 = `avg_production_time * actual_quantity` |
| `elapsed_minutes` | 누적 진행 시간 (초기 0) |

## 2. 모듈

`sample_order_system/production/queue.py`

```python
def enqueue(order_id, sample_id, shortage, avg_production_time, yield_rate, order_quantity) -> dict
def list_queue() -> list[dict]        # FIFO 순서 = 저장(등록) 순서
def current_item() -> dict | None     # 큐의 맨 앞(list_queue()[0])
def estimate_wait_minutes() -> float  # 큐에 있는 모든 항목의 (total_minutes - elapsed_minutes) 합
def advance(minutes: float) -> dict | None
    # 맨 앞 항목의 elapsed_minutes += minutes
    # 완료(elapsed_minutes >= total_minutes)되면: 완료 항목을 큐에서 제거하고 반환,
    # 아니면 None
```

- `actual_quantity = math.ceil(shortage / yield_rate)`.
- `advance()`가 완료 항목을 반환하면, 호출자(Controller/Model)가 다음을 수행:
  1. `samples.repository`의 재고를 `actual_quantity`만큼 증가.
  2. 해당 `order_id`의 주문 상태를 `PRODUCING -> CONFIRMED`로 변경.
- `advance()`는 한 번에 한 항목만 완료시킨다(같은 호출에서 여러 항목이 동시에 끝나는 경우는 다루지 않음 — 다음 `advance()` 호출에서 다음 항목이 이어서 진행).

## 2-1. 화면 표시용 조립 — `production/service.py`의 `production_status()` (UX 2차 검토 반영)

`queue.py`는 `sample_id`만 알고 "시료 이름"/"현재 재고량"은 모른다. 콘솔에 보여줄 정보(PRD 4.6 + 사용성 검토)는 시료 저장소와 조인해야 하므로, `production/service.py`에 순수 함수로 추가한다.

```python
def production_status(queue_file=..., samples_file=...) -> dict:
    # {"current": {...} | None, "waiting": [...]}
```

- `current` (생산 큐 맨 앞 1건, 없으면 `None`): `order_id`, `sample_name`, `order_quantity`, `stock`(현재 재고), `shortage`, `actual_quantity`, `remaining_minutes`(=`total_minutes - elapsed_minutes`, 콘솔에서는 "완료 예정 시간"으로 라벨링).
- `waiting` (큐의 2번째 항목부터, FIFO 순서 유지): 각 항목에 `sequence`(1부터), `order_id`, `sample_name`, `order_quantity`, `shortage`, `actual_quantity`, `estimated_minutes`(콘솔에서는 "예상 완료 시간"으로 라벨링). `estimated_minutes`는 "현재 처리 중 항목의 남은 시간 + 자신보다 앞선 대기 항목들의 총 생산시간 누적"으로 계산한다(기존 `estimate_wait_minutes()`와 동일한 누적 방식, 항목별로 나눠서 계산).

## 3. TDD 테스트 목록 (`tests/test_production_queue.py`)

1. `test_enqueue_computes_actual_quantity_with_ceil` — 예: shortage=170, yield_rate=0.92 → `ceil(170/0.92)=185`.
2. `test_enqueue_computes_total_minutes` — `avg_production_time * actual_quantity`.
3. `test_list_queue_preserves_fifo_order` — 3건 순서대로 enqueue 후 순서 그대로 반환되는지.
4. `test_current_item_is_the_first_enqueued`
5. `test_advance_accumulates_elapsed_minutes_without_completing` — `total_minutes`보다 적은 시간만큼 advance → 완료 안 됨, `elapsed_minutes`만 증가.
6. `test_advance_completes_and_removes_item_when_elapsed_reaches_total` — 정확히/초과로 advance → 완료 항목 반환 + 큐에서 제거.
7. `test_advance_promotes_next_item_after_completion` — 완료 후 `current_item()`이 다음 항목으로 바뀌는지.
8. `test_estimate_wait_minutes_sums_remaining_time_of_all_items`
9. `test_advance_on_empty_queue_returns_none`

## 4. 검증 방법 (사람이 직접 확인)

- [x] Phase 3에서 `PRODUCING`이 된 주문이 `생산 라인 조회`의 "현재 처리 중"에 나오는지. (`production_status()` + 콘솔 앱 구동으로 확인 — 승인 후 "[생산 중]" 표에 해당 주문이 시료 이름/재고량/부족량/실생산량/완료예정시간과 함께 표시됨)
- [x] 부족분/실생산량 계산이 `ceil(부족분/수율)` 공식과 일치하는지 손계산으로 검증. (`170/0.92 = 184.78... → ceil = 185`를 직접 계산해 테스트 값과 일치 확인)
- [x] 여러 건 승인 후 대기 목록이 승인한 순서(FIFO)대로 나오는지. (자동화 테스트 `test_list_queue_preserves_fifo_order`로 검증 — 3건을 순서대로 enqueue한 뒤 그 순서 그대로 반환됨을 확인)
- [x] "진행" 명령(또는 tick 트리거)을 반복 입력해 진행율/남은 시간이 줄어들다가, 완료 시 주문 상태가 `CONFIRMED`로 바뀌고 재고가 늘어나는지, 다음 대기 항목이 처리 중으로 넘어가는지 확인. (`production/service.py`의 `advance_production()`으로 오케스트레이션 구현. 재현: 재고 30/부족분 170/수율 0.92 → `advance(1)`은 미완료(재고 불변), `advance(10000)`은 완료되어 `actual_quantity=185`만큼 재고가 215로 증가하고 주문이 `CONFIRMED`로 전환, 큐가 빔을 확인. 콘솔 화면에서의 진행율/남은시간 "표시"는 Phase 7에서 재검증.)
