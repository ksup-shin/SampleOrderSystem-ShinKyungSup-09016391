# Phase 1 — 시료(Sample) 도메인

`docs/PRD.md` 4.2절, `docs/PLAN.md` Phase 1을 상세화한 문서.

## 1. 모듈

`sample_order_system/samples/repository.py`

```python
def register_sample(sample_id: str, name: str, avg_production_time: float, yield_rate: float, initial_stock: int = 0) -> dict
def list_samples() -> list[dict]          # id 등록 순서
def search_samples(keyword: str) -> list[dict]   # name에 keyword 포함(대소문자 무시)
def get_sample(sample_id: str) -> dict | None
```

내부적으로 `poc_json.json_crud.create_item/read_all/read_by_id`를 `data/samples.json`, `id_field="id"`로 호출한다.

## 2. 검증 규칙

- `sample_id`, `name`: 빈 문자열 불가.
- `avg_production_time`: 0보다 커야 함.
- `yield_rate`: 0 초과 1 이하 (`0 < yield_rate <= 1`).
- `initial_stock`: 0 이상 정수.
- 중복된 `sample_id` 등록 시 `ValueError` (이미 `poc_json.create_item`이 던지는 예외를 그대로 전파하되, 메시지는 도메인 용어로 감쌀지 여부는 구현 시 결정 — 최소 구현에서는 그대로 전파해도 무방).
- 위 검증 실패 시 모두 `ValueError`로 통일(콘솔 Controller에서 일괄적으로 잡아 `view.show_error`로 보여줄 수 있도록).

## 3. TDD 테스트 목록 (`tests/test_samples_repository.py`)

각 항목을 개별 테스트로 분리한다 (한 테스트 = 한 동작).

1. `test_register_sample_persists_record` — 등록 후 `list_samples()`에 해당 레코드가 그대로 나오는지.
2. `test_register_sample_rejects_duplicate_id` — 같은 id로 두 번 등록 시 `ValueError`.
3. `test_register_sample_rejects_invalid_yield_rate` — `yield_rate=0`, `yield_rate=1.5` 등 범위 밖 값에서 `ValueError` (parametrize).
4. `test_register_sample_rejects_non_positive_production_time` — `avg_production_time=0` 또는 음수에서 `ValueError`.
5. `test_list_samples_returns_all_registered_samples` — 여러 건 등록 후 개수/내용 일치.
6. `test_search_samples_matches_partial_name_case_insensitively` — 부분 일치 + 대소문자 무시.
7. `test_search_samples_returns_empty_when_no_match` — 매치 없으면 빈 리스트.
8. `test_get_sample_returns_none_when_missing` — 없는 id 조회 시 `None`.

테스트 격리: 각 테스트는 임시 디렉토리(pytest `tmp_path` 픽스처)에 자체 `samples.json`을 사용하도록, repository 함수들이 파일 경로를 인자로 받거나(권장) 모듈 레벨 경로를 monkeypatch 할 수 있게 설계한다. **권장**: 함수들이 `file_path` 파라미터를 받고, `sample_order_system/paths.py`의 기본값을 default arg로 사용 — 프로덕션에서는 기본값을 쓰고, 테스트에서는 `tmp_path`를 명시적으로 넘긴다.

## 4. 검증 방법 (사람이 직접 확인 — 콘솔 앱 완성 후)

- [ ] `시료 관리 → 시료 등록`에서 `S-001`/"실리콘 웨이퍼-8인치"/0.5/0.92 등록 → 성공 메시지 확인.
- [ ] 동일 ID 재등록 시도 → 에러로 거부.
- [ ] `시료 조회` → ID/이름/평균 생산시간/수율/재고 5개 항목이 모두 표시되는지 확인.
- [ ] `시료 검색`에서 "실리콘" 검색 → 매치, "없는이름" 검색 → 빈 결과.
- [ ] `data/samples.json` 또는 `poc_json.admin_tool data/samples.json`의 `list`로 실제 저장 내용 확인.
