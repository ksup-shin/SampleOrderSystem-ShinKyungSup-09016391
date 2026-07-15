# Phase 9 — 테스트 정리 & 마감

`docs/PRD.md` 6장, `docs/PLAN.md` Phase 9를 상세화한 문서.

## 체크리스트

- [ ] `tests/` 아래 도메인별로 파일이 정리되어 있는가 (samples/orders/production/monitoring/app).
- [ ] `.venv/Scripts/python.exe -m pytest -q` 전체 통과, 경고 없음.
- [ ] Model에는 비즈니스 로직이 없고 순수 로직 모듈(`samples`, `orders`, `production`, `monitoring`)을 호출만 하는지 재확인.
- [ ] View는 출력만, Controller는 라우팅만 하는지 재확인.
- [ ] `git log --oneline`이 논리적 단위로 잘 쪼개져 있고, 각 커밋이 "왜"를 설명하는지.
- [ ] `CLAUDE.md`/`docs/PRD.md`/`docs/PLAN.md`/`docs/phases/*`가 실제 구현과 어긋나지 않는지 최종 동기화.
- [ ] `docs/PLAN.md` 부록의 End-to-End 시나리오를 처음부터 끝까지 다시 한번 수동으로 수행.
