# Phase 7 — 메인 메뉴 & 앱 통합

`docs/PRD.md` 4.1절, `docs/PLAN.md` Phase 7을 상세화한 문서. Phase 1~6에서 만든 순수 로직 계층을 `mvc` 위에 얹는 단계.

> **UX 변경(재작업)**: 최초 구현은 `register S-001 ...`처럼 명령어+공백구분 인자를 한 줄에 입력받는 방식이었으나, PRD의 예시 UI([1]/[2] 번호 선택, 필드별 순차 프롬프트)에 맞춰 다음과 같이 재작업한다.
> - 모든 화면은 숫자 번호로 선택하는 메뉴([1] Action1 [2] Action2 ... [0] 뒤로)로만 조작한다. 자유 명령어 문자열은 쓰지 않는다.
> - 여러 값이 필요한 동작(등록/예약 등)은 한 줄에 인자를 몰아 받지 않고, 필드마다 별도 줄로 순차 입력받는다 (`Sample ID: `, `Name: `, `Avg Production Time: `, `Yield Rate: `, `Initial Stock: ` 처럼 한 필드당 한 번의 `input()` 호출). `mvc.Application`은 한 줄만 읽어 `dispatch(command, *args)`를 호출하지만, Controller가 `dispatch` 내부에서 `self.view.input(...)`을 필요한 만큼 반복 호출하면 되므로 `mvc` 라이브러리 자체는 수정할 필요가 없다.
> - 승인/거절/출고처럼 "대상 레코드를 고르는" 동작은 주문번호를 직접 타이핑하지 않고, 먼저 번호가 매겨진 목록을 보여준 뒤 "번호: "를 입력받아 목록에서 골라 처리한다(PRD 4.4의 "관리할 번호(1,2,3...)를 입력받는다" 요구와 일치).

## 1. mvc 연결

- `sample_order_system/app/menus.py`: 화면별 `(번호, 라벨)` 목록을 딱 한 곳에 정의한다. `view.py`(메뉴 출력)와 `controller.py`(어떤 번호가 유효한지 사람이 읽을 수 있는 근거)가 이 정의를 함께 참조해 화면-라우팅 불일치를 방지한다.
- `sample_order_system/app/model.py`의 `SampleOrderModel(mvc.Model)`: Phase 1~6 모듈들의 얇은 퍼사드. 메서드 호출 후 `self.notify(event, data)` 호출. (변경 없음)
- `sample_order_system/app/view.py`의 `SampleOrderView(mvc.View)`: `render(state)`에서 `menus.MENUS_BY_SCREEN[state.screen]`을 `[번호] 라벨` 형태로 출력.
- `sample_order_system/app/controller.py`의 `SampleOrderController(mvc.Controller)`: `dispatch(command, *args)`에서 화면별 번호를 라우팅. 값이 필요한 동작은 `self.view.input("필드명: ")`을 필드 수만큼 호출해 순차로 받는다. 레코드 선택이 필요한 동작은 먼저 목록을 번호와 함께 출력한 뒤 `self.view.input("번호: ")`로 인덱스를 받아 실제 ID로 변환한다.
- `sample_order_system/main.py`: 변경 없음.

## 2. 화면별 메뉴 (번호 → 동작)

| 화면 | 번호 | 동작 | 추가 입력 프롬프트 |
| --- | --- | --- | --- |
| main | 1~6 | 서브메뉴 진입 (아래 표와 동일) | - |
| main | 0 | 종료 | - |
| samples | 1 | 시료 등록 | `Sample ID:` `Name:` `Avg Production Time:` `Yield Rate:` `Initial Stock:` |
| samples | 2 | 시료 조회 | - |
| samples | 3 | 시료 검색 | `Keyword:` |
| samples | 0 | 뒤로 | - |
| reserve | 1 | 시료 예약 | `Sample ID:` `Customer:` `Quantity:` |
| reserve | 0 | 뒤로 | - |
| approval | 1 | 접수된 주문 목록 | - |
| approval | 2 | 주문 승인 | (번호 매긴 RESERVED 목록 출력 후) `번호:` |
| approval | 3 | 주문 거절 | (번호 매긴 RESERVED 목록 출력 후) `번호:` |
| approval | 0 | 뒤로 | - |
| monitoring | 1 | 주문량 확인 | - |
| monitoring | 2 | 재고량 확인 | - |
| monitoring | 0 | 뒤로 | - |
| production | 1 | 생산 현황/대기열 조회 | - |
| production | 2 | 생산 진행 | `진행 시간(분):` |
| production | 0 | 뒤로 | - |
| shipment | 1 | 출고 가능 목록 | - |
| shipment | 2 | 출고 처리 | (번호 매긴 CONFIRMED 목록 출력 후) `번호:` |
| shipment | 0 | 뒤로 | - |

메인 메뉴의 1~6은 기존과 동일하게 samples/reserve/approval/monitoring/production/shipment 화면으로 이동한다.

## 3. TDD 대상

`tests/test_app_formatting.py` (기존 유지)
1. `test_format_sample_row_includes_all_five_fields`
2. `test_format_summary_counts_registered_samples_and_total_stock`
3. `test_format_queue_row_shows_progress_percent_and_remaining_minutes`

`tests/test_app_controller.py` — `View`를 스크립트된 입력 큐(`inputs=[...]`)를 반환하는 더미 객체로 대체해 화면 전환 + 프롬프트 흐름 + 목록-선택 흐름을 검증한다.

1. `test_dispatch_main_menu_1_enters_sample_menu`
2. `test_dispatch_0_from_submenu_returns_to_main_menu`
3. `test_dispatch_unknown_command_shows_error_without_crashing`
4. `test_dispatch_exit_command_returns_false`
5. `test_samples_register_prompts_each_field_in_order_and_persists` — 프롬프트 문구 순서(`Sample ID:`→`Name:`→...)와 결과 레코드를 함께 검증.
6. `test_reserve_prompts_each_field_and_creates_order`
7. `test_approval_approve_lists_reserved_orders_then_prompts_index_and_approves` — 목록에 번호가 매겨져 출력되는지 + 잘못된 번호 입력 시 `ValueError`로 처리되는지.
8. `test_shipment_ship_lists_confirmed_orders_then_prompts_index_and_ships`
9. `test_production_advance_prompts_minutes`

## 4. 검증 방법 (사람이 직접 확인)

모두 `printf`로 번호/필드 값을 한 줄씩 표준입력에 흘려보내 `python -m sample_order_system.main`을 실제로 구동하는 방식으로 재현·확인함 (사람이 터미널에서 번호를 고르고 필드를 하나씩 입력하는 것과 동일한 흐름).

- [x] 메인 메뉴가 `[1] 시료 관리 [2] 시료 주문 ...` 형태로 번호와 라벨을 함께 보여주는지. (실제 앱 구동 출력에서 확인)
- [x] 시료 등록 시 `Sample ID:`/`Name:`/`Avg Production Time:`/`Yield Rate:`/`Initial Stock:`이 한 줄씩 순서대로 프롬프트되고, 등록 결과가 정확한지. (`test_samples_register_prompts_each_field_in_order_and_persists`로 프롬프트 순서까지 단위 검증 + 실제 앱 구동으로 재확인)
- [x] 시료 예약 시 `Sample ID:`/`Customer:`/`Quantity:`가 순서대로 프롬프트되는지. (동일하게 단위 테스트 + 실제 구동으로 확인)
- [x] 주문 승인/거절/출고 시 먼저 번호 매겨진 목록이 보이고, `번호:`를 입력하면 해당 레코드가 처리되는지. 목록에 없는 번호를 입력하면 에러로 처리되고 앱이 죽지 않는지. (`test_approval_approve_lists_reserved_orders_then_prompts_index_and_approves`, `test_approval_approve_rejects_out_of_range_index`, `test_shipment_ship_lists_confirmed_orders_then_prompts_index_and_ships`로 검증 + 실제 구동에서 `[1] ORD-000001 | ...` 목록 후 `번호:` 입력으로 승인/출고되는 것 확인)
- [x] 생산 진행 시 `진행 시간(분):` 프롬프트 후 큐가 정상적으로 진행/완료되는지. (`test_production_advance_prompts_minutes` + 실제 구동에서 확인)
- [x] 모든 서브 메뉴에서 "0" 선택 시 메인 메뉴로 정확히 복귀하는지. (실제 구동에서 각 서브메뉴마다 확인)
- [x] End-to-End: 시료 등록 → 주문 예약 → 승인(번호 선택, 재고부족 유도) → 생산 진행/완료 → 출고(번호 선택) → 모니터링 반영까지 새 UX로 한 번에 이어서 확인. 콘솔 앱을 번호/필드 입력 시퀀스로 재구동하여 이전 버전과 동일한 최종 결과(재고 15, `RELEASE` 1건, 재고상태 `여유`)를 확인 — 회귀 없음.
