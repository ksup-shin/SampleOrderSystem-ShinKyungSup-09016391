# Phase 0 — 프로젝트 뼈대 & 데이터 스키마 확정

`docs/PLAN.md`의 Phase 0을 상세화한 문서입니다. 여기서 확정한 내용은 이후 모든 Phase가 그대로 따릅니다.

## 1. 패키지 구조

```
sample_order_system/
  __init__.py
  paths.py            # 데이터 파일 경로 상수
  samples/
    __init__.py
    repository.py      # 시료 CRUD (poc_json 위에 얇게 래핑)
  orders/
    __init__.py
    repository.py       # 주문 CRUD
    numbering.py         # 주문번호 채번
  production/
    __init__.py
    queue.py            # 생산 큐(FIFO) + 실 생산량/시간 계산
  monitoring/
    __init__.py
    service.py           # 상태별 집계, 재고 상태 분류
  app/
    model.py             # mvc.Model 상속
    view.py               # mvc.View 상속
    controller.py         # mvc.Controller 상속, dispatch 라우팅
  main.py                 # 진입점 (mvc.Application 조립)

data/
  samples.json
  orders.json

tests/
  test_samples_repository.py
  test_orders_repository.py
  test_production_queue.py
  test_monitoring_service.py
  ...
```

- `mvc`, `poc_json`, `dummy_data_generator`는 그대로 재사용하며 수정하지 않는다.
- 비즈니스 로직(재고 판정, 생산량 계산, 상태 전이)은 `sample_order_system/*` 순수 함수/클래스에 두고, `mvc.Model`은 이 로직을 호출한 뒤 `notify()`만 담당한다 — 테스트는 대부분 `mvc` 없이 이 순수 로직 계층을 직접 호출해서 검증한다(콘솔 I/O 없이 빠르게 테스트하기 위함).

## 2. 데이터 파일 & 레코드 스키마

### `data/samples.json` (id_field = `"id"`)

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | str | 시료 ID (예: `"S-001"`), 사용자가 지정 |
| `name` | str | 시료명 |
| `avg_production_time` | float | 1ea당 평균 생산시간(분) |
| `yield_rate` | float | 0 초과 1 이하 |
| `stock` | int | 현재 재고 수량, 0 이상 |

### `data/orders.json` (id_field = `"id"`)

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | str | 주문번호 (예: `"ORD-000001"`) |
| `sample_id` | str | `samples.json`의 `id` 참조 |
| `customer` | str | 고객명 |
| `quantity` | int | 주문 수량, 1 이상 |
| `status` | str | `RESERVED`/`REJECTED`/`PRODUCING`/`CONFIRMED`/`RELEASE` |

주문번호 채번 규칙(설계 결정): `ORD-` + 6자리 0-padded 순번(`ORD-000001`, `ORD-000002`, ...). 기존 레코드 중 최댓값 다음 값을 사용한다(`orders/numbering.py`).

## 3. 설계 결정 — 생산 진행 시간 표현 방식

PLAN.md Phase 0에서 보류했던 결정. **수동 tick 방식**을 채택한다.

- 이유: 콘솔 앱이 항상 실행 중인 것이 아니고(사용자가 명령을 입력할 때만 반응), wall-clock 기반으로 하면 앱을 켜지 않은 사이의 "가짜 경과 시간"을 어떻게 다룰지 애매해진다. 과제 성격상 결정론적 테스트가 쉬운 tick 방식이 pytest로 검증하기도 유리하다.
- 동작: 생산 큐의 진행 상태는 "누적 생산 완료량(분 단위)"으로 저장한다. 사용자가 생산 라인 화면에서 `진행` 같은 명령을 입력하거나, 다른 화면 전환 시 일정 시간(예: 1분)이 자동으로 흐른 것으로 간주해 `production.queue.advance(minutes)`를 호출한다. 완료 조건은 `누적 진행 시간 >= 총 생산 시간`.
- `advance(minutes)`는 순수 함수형으로 pytest에서 임의의 분 단위를 넣어 결정론적으로 검증 가능하다 (예: `advance(1000)`으로 즉시 완료시키는 테스트도 가능).
- 진행율(%) = `min(1.0, 누적진행시간 / 총생산시간)`. 남은 시간 = `max(0, 총생산시간 - 누적진행시간)`.
- 예상 완료시간(대기열 항목): "현재 처리 중 항목의 남은 시간 + 대기열에서 자신보다 앞선 항목들의 총 생산시간 합"으로 계산(분 단위 숫자로 표기, 실제 시계 시각으로 변환하지 않음 — 시계 시각 변환은 사용자가 원하면 이후 Phase에서 추가 가능).

## 4. 설계 결정 — 모니터링 "미출고 수요" 기준

PLAN.md Phase 6에서 보류했던 결정. **시료별로 `RESERVED`/`PRODUCING`/`CONFIRMED` 상태인 주문 수량의 합**을 "미출고 수요"로 정의한다(`RELEASE`, `REJECTED`는 제외).

- 여유: `재고 >= 미출고 수요` 이고 `재고 > 0`
- 부족: `0 < 재고 < 미출고 수요`
- 고갈: `재고 == 0`

## 5. Phase 0에서 만들 것 (TDD 대상)

Phase 0 자체는 로직이 거의 없는 스캐폴딩이라 테스트는 최소한으로 둔다.

- [ ] `tests/test_paths.py`: 데이터 디렉토리 상수가 존재하고, `poc_json`으로 없는 파일을 읽으면 빈 리스트가 나오는지(이미 `poc_json`이 보장하는 동작이지만, 우리 경로 상수와 결합했을 때도 성립하는지) 확인하는 스모크 테스트 1개.
- [ ] `pyproject.toml` 또는 `pytest.ini`에 `testpaths = ["tests"]` 설정.
- [ ] `requirements.txt`(또는 `requirements-dev.txt`)에 `pytest` 고정.

## 6. 검증 방법 (사람이 직접 확인)

- [ ] `.venv/Scripts/python.exe -m pytest`가 에러 없이 실행되고, Phase 0 스모크 테스트가 통과하는지 확인.
- [ ] `python -c "import sample_order_system"`이 에러 없이 실행되는지 확인.
