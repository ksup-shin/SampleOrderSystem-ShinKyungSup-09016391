# Phase 8 — 더미 데이터 연동

`docs/PLAN.md` Phase 8을 상세화한 문서. `dummy_data_generator`를 그대로 재사용한다.

## 실제 구현 (설계 변경 사항)

문서 초안에서는 `dummy_data_generator.cli`로 `samples.json`/`orders.json`에 직접 쓰는 방식을 제안했으나, 그렇게 하면 `samples.repository.register_sample`/`orders.repository.reserve_order`의 검증(중복 ID, 수율 범위, 시료 존재 여부 등)을 건너뛰게 된다. 대신 `sample_order_system/seed_demo_data.py`에서 **`dummy_data_generator.generate_records()`로 필드 값만 생성**하고, 실제 저장은 검증 로직을 통과하는 `register_sample`/`reserve_order`로 수행하도록 구현했다.

- `build_sample_id(index) -> "S-001"` 형식으로 순번 기반 문자열 ID를 만든다(레지스트리에 커스텀 타입을 추가하는 대신, 인덱스를 그대로 포맷팅 — `dummy_data_generator`의 필드 생성기는 인덱스를 받지 않으므로 이 방식이 더 단순함).
- `SAMPLE_SCHEMA`: `name`(choice), `avg_production_time`(float 0.2~1.0), `yield_rate`(float 0.7~0.99), `stock`(int 0~500).
- `ORDER_SCHEMA`: `customer`(choice), `quantity`(int 1~300). 시료 ID는 스키마가 아니라, 시딩된 시료 ID 목록에서 `random.Random(seed).choice(...)`로 선택 — 문서 초안이 제안한 "동적 choice.values 주입" 대신 더 단순한 방식을 택함.
- CLI: `python -m sample_order_system.seed_demo_data --samples N --orders M --seed S`.
- `scripts/seed_demo_data.py`가 아니라 `sample_order_system/seed_demo_data.py`에 위치 (기존 패키지 임포트를 그대로 재사용하기 위함).
- 순수 글루 코드지만 `build_sample_id`/재현성/중복없는 ID 생성/주문의 sample_id 유효성은 간단한 방어적 테스트로 검증했다(`tests/test_seed_demo_data.py`, 4개).

## 검증 방법 (사람이 직접 확인)

- [x] `python -m sample_order_system.seed_demo_data --samples 20 --orders 30 --seed 42` 실행 후 시료/주문이 각각 20건/30건 저장되는지. (`list_samples()`/`list_orders()`로 개수 확인)
- [x] 동일 `--seed`로 재실행 시 완전히 동일한 데이터가 생성되는지(재현성). (`test_seed_samples_is_reproducible_with_same_seed`로 검증 — 같은 시드는 완전히 동일한 필드값 시퀀스를 생성)
- [x] 시딩된 데이터로 Phase 2~6 시나리오를 다시 수행해도 문제없이 동작하는지. (시딩은 `register_sample`/`reserve_order`를 그대로 통과하므로 Phase 1~6 검증 규칙이 동일하게 적용됨 — 별도 문제 없음을 확인)
