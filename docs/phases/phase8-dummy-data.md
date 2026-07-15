# Phase 8 — 더미 데이터 연동

`docs/PLAN.md` Phase 8을 상세화한 문서. `dummy_data_generator`를 그대로 재사용한다.

## 1. 시료 스키마 예시 (`schemas/sample_schema.json`)

```json
{
  "name": {"type": "choice", "values": [
    "실리콘 웨이퍼-8인치", "GaN 에피탁셜-4인치", "SiC 파워기판-6인치",
    "포토레지스트-PR7", "산화막 웨이퍼-SiO2"
  ]},
  "avg_production_time": {"type": "float", "min": 0.2, "max": 1.0, "ndigits": 2},
  "yield_rate": {"type": "float", "min": 0.7, "max": 0.99, "ndigits": 2},
  "stock": {"type": "int", "min": 0, "max": 500}
}
```

- `id` 필드는 `dummy_data_generator`가 자동으로 `1, 2, 3, ...`(정수)로 채번하므로, 우리 도메인의 문자열 ID(`S-001`)와 형식이 다르다. `--id-field id`는 그대로 두되, 생성 후 별도 스크립트에서 `f"S-{id:03d}"` 형태로 변환하거나, `register_field_type("sample_id", ...)`으로 커스텀 타입을 등록해 처음부터 문자열 ID를 생성하는 방식 중 택1 (권장: 커스텀 타입 등록 — 데이터 파일 후처리 없이 한 번에 끝남).

## 2. 주문 스키마

시료 ID는 실제 등록된 시료 목록에 의존하므로, `dummy_data_generator`의 단순 `choice` 타입만으로는 부족하다. **권장 접근**: 더미 시료를 먼저 생성해 `samples.json`을 만든 뒤, 그 파일에서 ID 목록을 읽어 주문 스키마의 `choice.values`를 동적으로 채워 넣는 짧은 시딩 스크립트(`scripts/seed_demo_data.py`)를 작성한다. 이 스크립트는 `poc_json.load_json` + `dummy_data_generator.generate_records`를 조합하는 얇은 글루 코드이며, 새 비즈니스 로직이 아니므로 TDD 필수 대상은 아니다(다만 손상된 입력에 대한 방어적 테스트 1~2개는 추가 가능).

## 3. 검증 방법 (사람이 직접 확인)

- [ ] `python -m dummy_data_generator.cli schemas/sample_schema.json data/samples.json --count 20 --seed 42` 실행 후 `시료 조회`에서 20개가 보이는지.
- [ ] 동일 `--seed`로 재실행 시 완전히 동일한 데이터가 생성되는지(재현성).
- [ ] 시딩된 데이터로 Phase 2~6 시나리오를 다시 수행해도 문제없이 동작하는지.
