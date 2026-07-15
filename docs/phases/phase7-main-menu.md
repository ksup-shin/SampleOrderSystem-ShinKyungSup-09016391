# Phase 7 — 메인 메뉴 & 앱 통합

`docs/PRD.md` 4.1절, `docs/PLAN.md` Phase 7을 상세화한 문서. Phase 1~6에서 만든 순수 로직 계층을 `mvc` 위에 얹는 단계.

> **UX 변경 1(재작업)**: 최초 구현은 `register S-001 ...`처럼 명령어+공백구분 인자를 한 줄에 입력받는 방식이었으나, PRD의 예시 UI([1]/[2] 번호 선택, 필드별 순차 프롬프트)에 맞춰 다음과 같이 재작업했다.
> - 모든 화면은 숫자 번호로 선택하는 메뉴([1] Action1 [2] Action2 ... [0] 뒤로)로만 조작한다. 자유 명령어 문자열은 쓰지 않는다.
> - 여러 값이 필요한 동작(등록/예약 등)은 한 줄에 인자를 몰아 받지 않고, 필드마다 별도 줄로 순차 입력받는다. `mvc.Application`은 한 줄만 읽어 `dispatch(command, *args)`를 호출하지만, Controller가 `dispatch` 내부에서 `self.view.input(...)`을 필요한 만큼 반복 호출하면 되므로 `mvc` 라이브러리 자체는 수정할 필요가 없다.
> - 승인/거절/출고처럼 "대상 레코드를 고르는" 동작은 주문번호를 직접 타이핑하지 않고, 먼저 번호가 매겨진 목록을 보여준 뒤 "번호: "를 입력받아 목록에서 골라 처리한다.

> **UX 변경 2(2차 검토 반영)**: 1차 재작업 이후 사용성 검토에서 아래 문제가 지적되어 다시 반영한다.
> - **표 형식 + 헤더**: 지금까지는 `str(dict)` 또는 `"a | b | c"`처럼 값만 나열해 각 값이 무엇을 뜻하는지 알 수 없었다. 모든 목록/현황 출력은 **컬럼 제목이 있는 표**로 나오도록 `app/formatting.py`에 `render_table(headers, rows)` 공통 함수를 만들고, 시료/주문/모니터링/생산 현황 각각 전용 표 포맷 함수를 그 위에 둔다. (한글 문자가 영문의 2배 폭을 차지하는 점을 고려해 `unicodedata.east_asian_width` 기반으로 정렬한다.)
> - **필드/프롬프트 라벨은 한글로**: `Sample ID:`/`Name:`/`Customer:`/`Quantity:` 등 영어 프롬프트를 전부 한글(`시료 ID:`/`이름:`/`고객명:`/`수량:` 등)로 바꾼다. 상태값 자체(`RESERVED`/`CONFIRMED`/`PRODUCING`/`REJECTED`/`RELEASE`)는 PRD가 정의한 도메인 용어이므로 그대로 유지한다.
> - **시료 검색 프롬프트**: `Keyword:` → **`시료 이름:`** 로 변경 (검색 대상이 이름이라는 것을 명확히 함).
> - **승인/거절 결과 재출력**: 번호를 입력해 승인/거절을 실행한 뒤, 해당 주문 정보를 표로 한 번 더 보여주고 `상태 변경: RESERVED → PRODUCING`(또는 `CONFIRMED`/`REJECTED`)처럼 상태 전이를 명시적으로 보여준다. 출고도 동일하게 `상태 변경: CONFIRMED → RELEASE`를 보여준다.
> - **모니터링 표 형식**: 주문량 확인/재고량 확인 모두 `dict` 그대로 출력하지 않고 표로 보여준다.
> - **생산 현황/대기열 분리 표시**: 이 메뉴에 들어가면(번호 선택 즉시) 현재 생산 중인 1건과 대기 중인 나머지를 **별도의 표 2개**로 보여준다.
>   - 생산 중 표 컬럼: 주문 번호 / 시료 이름 / 주문량 / 재고량 / 부족량 / 실 생산량 / 완료 예정 시간(분)
>   - 대기 중 표 컬럼: 순서 / 주문 번호 / 시료 이름 / 주문량 / 부족분 / 실 생산량 / 예상 완료 시간(분)
>   - 이 정보는 생산 큐 원본(`queue.py`)에 없는 "시료 이름"/"재고량"을 시료 저장소와 조인해야 하므로, `production/service.py`에 `production_status()`를 새로 추가해 조립한다(순수 함수, TDD 대상).
> - **생산 진행 메뉴 설명**: `[2] 생산 진행` 메뉴 자체에 "테스트용으로 임의의 시간(분)이 흐른 것으로 처리한다"는 설명을 덧붙인다(실제 시계가 아니라 Phase 0에서 정한 수동 tick 방식이라는 것을 화면에서도 알 수 있도록).

## 1. mvc 연결

- `sample_order_system/app/menus.py`: 화면별 `(번호, 라벨)` 목록을 딱 한 곳에 정의한다. `view.py`(메뉴 출력)와 `controller.py`가 함께 참조한다. `production` 화면의 `2번` 라벨에는 tick 방식 설명이 괄호로 포함된다.
- `sample_order_system/app/model.py`의 `SampleOrderModel(mvc.Model)`: Phase 1~6 모듈들의 얇은 퍼사드 + `production_status()` 위임 추가.
- `sample_order_system/app/view.py`: `render(state)`에서 `menus.MENUS_BY_SCREEN[state.screen]`을 `[번호] 라벨` 형태로 출력. 표 렌더링 자체는 `formatting.py`가 만든 완성된 문자열을 `show_message`로 그대로 출력하므로 View는 여전히 "출력만" 담당.
- `sample_order_system/app/controller.py`: 목록/현황성 출력은 전부 `formatting.py`의 표 함수를 거쳐 `view.show_message(table_text)`로 한 번에 출력한다. 필드 프롬프트 라벨은 한글로 통일.
- `sample_order_system/production/service.py`: `production_status()` 추가 — 큐를 시료 저장소와 조인해 현재/대기 항목을 사람이 읽을 수 있는 필드로 조립.
- `sample_order_system/main.py`: 변경 없음.

## 2. 화면별 메뉴 (번호 → 동작)

| 화면 | 번호 | 동작 | 추가 입력 프롬프트(한글) |
| --- | --- | --- | --- |
| main | 1~6 | 서브메뉴 진입 | - |
| main | 0 | 종료 | - |
| samples | 1 | 시료 등록 | `시료 ID:` `이름:` `평균 생산시간(분):` `수율:` `초기 재고:` |
| samples | 2 | 시료 조회 | - (표로 출력) |
| samples | 3 | 시료 검색 | `시료 이름:` |
| samples | 0 | 뒤로 | - |
| reserve | 1 | 시료 예약 | `시료 ID:` `고객명:` `수량:` |
| reserve | 0 | 뒤로 | - |
| approval | 1 | 접수된 주문 목록 | - (표로 출력) |
| approval | 2 | 주문 승인 | (번호 매긴 RESERVED 목록 표 출력 후) `번호:` → 처리 후 주문 정보 재출력 + 상태 변경 표시 |
| approval | 3 | 주문 거절 | 위와 동일(거절) |
| approval | 0 | 뒤로 | - |
| monitoring | 1 | 주문량 확인 | - (상태별 건수 표) |
| monitoring | 2 | 재고량 확인 | - (시료별 재고/수요/상태 표) |
| monitoring | 0 | 뒤로 | - |
| production | 1 | 생산 현황/대기열 조회 | - (진입 즉시 "생산 중"/"대기 중" 표 2개 출력) |
| production | 2 | 생산 진행 (테스트용: 임의의 시간(분)이 흐른 것으로 처리) | `진행 시간(분):` |
| production | 0 | 뒤로 | - |
| shipment | 1 | 출고 가능 목록 | - (표로 출력) |
| shipment | 2 | 출고 처리 | (번호 매긴 CONFIRMED 목록 표 출력 후) `번호:` → 처리 후 주문 정보 재출력 + 상태 변경 표시 |
| shipment | 0 | 뒤로 | - |

## 3. TDD 대상

`tests/test_app_formatting.py`
1. `test_render_table_aligns_headers_and_rows_with_korean_width`
2. `test_format_samples_table_has_korean_headers`
3. `test_format_orders_table_has_korean_headers`
4. `test_format_indexed_orders_table_prefixes_row_number`
5. `test_format_order_counts_table_has_korean_headers`
6. `test_format_stock_levels_table_has_korean_headers`
7. `test_format_production_current_table_has_korean_headers`
8. `test_format_production_waiting_table_has_korean_headers`
9. `test_format_summary_counts_registered_samples_and_total_stock` (기존 유지)

`tests/test_production_service.py` (추가)
1. `test_production_status_returns_none_current_and_empty_waiting_when_queue_empty`
2. `test_production_status_enriches_current_item_with_sample_name_and_stock`
3. `test_production_status_computes_cumulative_estimated_minutes_for_waiting_items`

`tests/test_app_controller.py` (라벨/표/재출력 관련 항목 갱신)
1. 기존 항목 유지, 프롬프트 문자열만 한글로 변경(`"시료 ID: "`, `"이름: "` 등).
2. `test_approval_approve_shows_order_and_status_transition_after_processing` — 승인 후 메시지에 주문번호와 `RESERVED`, 새 상태가 모두 포함되는지.
3. `test_shipment_ship_shows_order_and_status_transition_after_processing`

## 4. 검증 방법 (사람이 직접 확인)

모두 `printf`로 번호/필드 값을 한 줄씩 표준입력에 흘려보내 `python -m sample_order_system.main`을 실제로 구동하는 방식으로 재현·확인.

- [x] 시료 조회/검색/모니터링/생산현황/승인목록/출고목록 등 모든 목록성 출력에 컬럼 제목이 있는 표로 나오는지(값만 나열되지 않는지). (실제 구동에서 모든 화면이 헤더+구분선+데이터 행으로 정렬된 표로 출력되는 것을 확인)
- [x] 모든 입력 프롬프트가 한글 라벨(`시료 ID:`, `이름:`, `평균 생산시간(분):`, `수율:`, `초기 재고:`, `고객명:`, `수량:`, `시료 이름:`, `번호:`, `진행 시간(분):`)로 나오는지. (실제 구동 + `test_samples_register_prompts_each_field_in_order_and_persists`/`test_reserve_prompts_each_field_and_creates_order`/`test_production_advance_prompts_minutes`로 프롬프트 문자열 자체를 단위 검증)
- [x] 시료 검색 프롬프트가 `시료 이름:` 인지 (`Keyword:`가 아닌지). (`test_samples_search_prompts_with_sample_name_label` + 실제 구동에서 확인)
- [x] 승인/거절 시 번호 입력 후, 해당 주문 정보가 표로 한 번 더 나오고 `상태 변경: RESERVED → PRODUCING`(또는 `CONFIRMED`/`REJECTED`) 문구가 나오는지. (`test_approval_approve_shows_order_and_status_transition_after_processing`, `test_approval_reject_shows_order_and_status_transition_after_processing` + 실제 구동에서 `상태 변경: RESERVED → PRODUCING` 출력 확인)
- [x] 출고 시에도 동일하게 주문 정보 재출력 + `상태 변경: CONFIRMED → RELEASE` 확인. (`test_shipment_ship_shows_order_and_status_transition_after_processing` + 실제 구동으로 확인)
- [x] 생산 라인 조회 진입 시 "생산 중" 표(주문번호/시료이름/주문량/재고량/부족량/실생산량/완료예정시간)와 "대기 중" 표(순서/주문번호/시료이름/주문량/부족분/실생산량/예상완료시간)가 각각 분리되어 나오는지. (`test_production_list_shows_current_and_waiting_tables_separately` + 실제 구동에서 `[생산 중]`/`[대기 중]` 섹션과 표가 분리 출력됨을 확인)
- [x] `[2] 생산 진행` 메뉴 라벨 자체에 "테스트용 임의 시간 경과" 설명이 포함되어 있는지. (실제 구동에서 `[2] 생산 진행 (테스트용: 임의의 시간(분)이 흐른 것으로 처리)` 출력 확인)
- [x] End-to-End: 새 표시 방식으로 전체 시나리오(등록→예약→승인→생산진행/완료→출고→모니터링)를 다시 수행해 최종 수치(재고/상태)가 이전과 동일한지. (콘솔 앱 재구동 — 최종 재고 15, `RELEASE` 1건, 재고상태 `여유`로 이전 실행과 완전히 동일한 결과를 확인, 표시 방식만 바뀌고 계산 결과는 회귀 없음)
