# Phase 7 — 메인 메뉴 & 앱 통합

`docs/PRD.md` 4.1절, `docs/PLAN.md` Phase 7을 상세화한 문서. Phase 1~6에서 만든 순수 로직 계층을 `mvc` 위에 얹는 단계.

## 1. mvc 연결

- `sample_order_system/app/model.py`의 `SampleOrderModel(mvc.Model)`: Phase 1~6 모듈들의 얇은 퍼사드. 메서드 호출 후 `self.notify(event, data)` 호출.
- `sample_order_system/app/view.py`의 `SampleOrderView(mvc.View)`: `render(state)`에서 현재 화면(메인 메뉴/서브 메뉴)에 맞는 표를 출력. 표 형식 함수는 별도 `app/formatting.py`로 분리해 pytest로 순수 함수 테스트 가능하게 한다.
- `sample_order_system/app/controller.py`의 `SampleOrderController(mvc.Controller)`: `dispatch(command, *args)`에서 메뉴 번호/명령어를 라우팅. 현재 화면 상태(메인/시료관리/주문/승인거절/모니터링/생산라인/출고)를 Controller가 들고 있다가 "뒤로" 명령으로 상위로 복귀.
- `sample_order_system/main.py`: `Application(SampleOrderModel(), SampleOrderView(), SampleOrderController).run()`.

## 2. 메뉴 라우팅 표

| 메인 메뉴 번호 | 이동 | 뒤로 |
| --- | --- | --- |
| 1 | 시료 관리 서브메뉴 | 0 |
| 2 | 시료 주문(예약) | 0 |
| 3 | 주문 승인/거절 | 0 |
| 4 | 모니터링 | 0 |
| 5 | 생산 라인 조회 | 0 |
| 6 | 출고 처리 | 0 |
| 0 | 종료 | - |

## 3. TDD 대상

이 Phase는 콘솔 I/O가 얽혀 있어 순수 함수 테스트가 상대적으로 적다. 그래도 TDD로 먼저 테스트를 작성한다.

`tests/test_app_formatting.py`
1. `test_format_sample_row_includes_all_five_fields`
2. `test_format_summary_counts_registered_samples_and_total_stock`

`tests/test_app_controller.py` (View를 더미/캡처 객체로 대체해 dispatch 라우팅만 검증)
1. `test_dispatch_main_menu_1_enters_sample_menu`
2. `test_dispatch_0_from_submenu_returns_to_main_menu`
3. `test_dispatch_unknown_command_shows_error_without_crashing`
4. `test_dispatch_exit_command_returns_false`

## 4. 검증 방법 (사람이 직접 확인)

- [ ] 앱 최초 실행 시 메인 메뉴 요약 정보가 실제 데이터와 일치하는지.
- [ ] 모든 서브 메뉴에서 "뒤로" 선택 시 메인 메뉴로 정확히 복귀하는지.
- [ ] 잘못된 번호/명령 입력 시 앱이 죽지 않고 에러 메시지만 나오는지.
- [ ] `종료` 선택 시 정상 종료.
- [ ] End-to-End: 시료 등록 → 주문 예약 → 승인(재고부족 유도) → 생산 진행/완료 → 출고 → 모니터링 반영까지 한 번에 이어서 확인 (`docs/PLAN.md` 부록 시나리오 참고).
