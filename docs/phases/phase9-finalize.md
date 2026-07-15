# Phase 9 — 테스트 정리 & 마감

`docs/PRD.md` 6장, `docs/PLAN.md` Phase 9를 상세화한 문서.

## 체크리스트

- [x] `tests/` 아래 도메인별로 파일이 정리되어 있는가. (`test_paths`, `test_samples_repository`, `test_orders_repository`/`test_order_numbering`/`test_order_approval`/`test_order_shipment`, `test_production_queue`/`test_production_service`, `test_monitoring_service`, `test_app_formatting`/`test_app_controller`, `test_seed_demo_data` — 도메인별로 분리되어 있음)
- [x] `.venv/Scripts/python.exe -m pytest -q` 전체 통과, 경고 없음. (Phase 9 최초 마감 시점 스냅샷: 73 passed. 이후 UX 재작업 등으로 테스트가 계속 추가되었으므로, 최신 통과 개수는 `pytest -q` 실행 결과를 직접 확인할 것 — 항상 이 숫자와 일치할 필요는 없음)
- [x] Model에는 비즈니스 로직이 없고 순수 로직 모듈(`samples`, `orders`, `production`, `monitoring`)을 호출만 하는지 재확인. (`app/model.py` 확인 — 검증/계산 로직은 전부 도메인 모듈에 있고, Model은 파일 경로를 넘겨 호출한 뒤 `notify()`만 함)
- [x] View는 출력만, Controller는 라우팅만 하는지 재확인. (`app/view.py`는 화면별 메뉴 문자열 출력과 요약 표시만 담당. `app/controller.py`는 화면 상태에 따른 명령 분기 + 타입 변환(int/float 파싱) + `ValueError`를 `view.show_error`로 전달하는 역할만 하며, 승인/재고 판정 등 실제 비즈니스 결정은 하지 않음)
- [x] `git log --oneline`이 논리적 단위로 잘 쪼개져 있고, 각 커밋이 "왜"를 설명하는지. (Phase 단위/재작업 단위로 분리되어 있으며 — Phase 9 최초 마감 시점 11개 커밋, 이후 UX 재작업 등이 추가 커밋으로 이어짐 — 각 커밋 메시지에 검증 근거를 함께 기록)
- [x] `CLAUDE.md`/`docs/PRD.md`/`docs/PLAN.md`/`docs/phases/*`가 실제 구현과 어긋나지 않는지 최종 동기화. (`CLAUDE.md`에 "애플리케이션 없음" 문구를 제거하고 `sample_order_system` 아키텍처 섹션을 새로 추가, git 저장소 상태 문구 갱신. `docs/phases/phase8-dummy-data.md`는 실제 구현(파일 위치, 스키마 방식 변경)에 맞춰 갱신 완료)
- [x] `docs/PLAN.md` 부록의 End-to-End 시나리오를 처음부터 끝까지 다시 한번 수동으로 수행. (콘솔 앱을 파이프 입력으로 재구동 — 시료등록→예약→승인(부족)→생산완료→출고→모니터링까지 이전 실행과 동일한 결과(재고 15, RELEASE 1건, 여유)를 재현하여 회귀 없음을 확인)
