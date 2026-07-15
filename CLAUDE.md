# CLAUDE.md

이 파일은 이 저장소에서 작업하는 Claude Code(claude.ai/code)에게 제공하는 가이드입니다.

## 프로젝트 개요

S-Semi(가상의 반도체 회사)의 "반도체 시료 생산주문관리 시스템"(SampleOrderSystem)을 만드는 저장소입니다. 시료 등록, 고객 주문 접수/승인/거절, 단일 생산 라인(FIFO), 모니터링, 출고 처리를 다루는 콘솔(CUI) 애플리케이션입니다.

**요구사항(비즈니스 규칙, 기능 명세, 상태 흐름 등)은 전부 `docs/PRD.md`에 있습니다.** 기능을 구현하기 전에 반드시 그 문서를 먼저 확인하세요. 이 파일(CLAUDE.md)에는 기술스택/아키텍처/개발 방법만 다룹니다.

이 저장소에는 재사용 라이브러리 3개(`mvc`, `poc_json`, `dummy_data_generator`)와, 이를 조합해 만든 실제 애플리케이션 `sample_order_system/`가 있습니다 — 실제 한계가 발견되지 않는 한 세 라이브러리는 수정하지 마세요. `sample_order_system/`의 모듈 구조와 구현 순서는 `docs/phases/phase0-foundation.md`~`phase9-finalize.md`에 상세히 정리되어 있습니다.

## 기술 스택

- Python (표준 라이브러리 위주, 외부 의존성 없음), 로컬 `.venv` 사용. pytest만 `requirements-dev.txt`로 관리되는 유일한 개발 의존성.
- 영속성: `poc_json`을 통한 JSON 파일 기반 저장/조회 (DB 없음). 데이터 파일 경로는 `sample_order_system/paths.py`에 상수로 정의(`data/samples.json`, `data/orders.json`, `data/production_queue.json`). 이 파일들은 `.gitignore`로 제외되어 있으므로(`data/*.json`), 앱 실행/테스트 후 남은 데이터는 커밋 대상이 아님.
- git 저장소 있음(`main` 브랜치). 린터/포매터/CI는 아직 없음.

## 명령어

- 앱 실행: `.venv/Scripts/python.exe -m sample_order_system.main`
- 모듈 실행: `.venv/Scripts/python.exe -m <module.path>` (예: `.venv/Scripts/python.exe -m dummy_data_generator.cli schema.json out.json --count 20`)
- 데모 데이터 시딩: `.venv/Scripts/python.exe -m sample_order_system.seed_demo_data --samples 20 --orders 30 --seed 42`
- JSON 관리자/모니터링 도구(대화형): `.venv/Scripts/python.exe -m poc_json.admin_tool <data.json>`
- JSON 관리자/모니터링 도구(실시간 감시): `.venv/Scripts/python.exe -m poc_json.admin_tool <data.json> --watch`
- 더미 데이터 생성 CLI: `.venv/Scripts/python.exe -m dummy_data_generator.cli <schema.json> <output.json> --count N [--seed N] [--id-field id] [--start-id 1]`

### 테스트

- 테스트 프레임워크는 **pytest**를 사용합니다(unittest 대신 pytest 채택).
- 전체 테스트 실행: `.venv/Scripts/python.exe -m pytest`
- 단일 파일 실행: `.venv/Scripts/python.exe -m pytest tests/test_x.py`
- 단일 테스트 함수 실행: `.venv/Scripts/python.exe -m pytest tests/test_x.py::test_name`
- 더미 데이터 생성기의 `seed` 옵션을 활용하면 재현 가능한 테스트 픽스처를 만들 수 있습니다.
- **TDD(테스트 주도 개발) 필수**: 새 기능 구현이나 버그 수정 시 프로덕션 코드보다 실패하는 테스트를 먼저 작성해야 합니다. 자세한 절차는 `test-driven-development` 스킬(`.claude/skills/test-driven-development/SKILL.md`)을 따르세요 — 구현 코드를 작성하기 전에 반드시 이 스킬을 먼저 로드/적용합니다.

## 아키텍처

### `mvc` — 재사용 가능한 콘솔 MVC 스켈레톤

추상 베이스 클래스만 제공하며, 실제 앱은 세 클래스를 모두 상속받아 `Application`으로 연결합니다.

- `Model` (`mvc/model.py`): 상태 + 옵저버 패턴. View/Controller를 절대 import하지 않습니다. 상태가 바뀔 때마다 `self.notify(event, data)`를 호출해야 합니다.
- `View` (`mvc/view.py`): 콘솔 입출력(`print`/`input`)만 담당합니다. 비즈니스 로직이 있으면 안 되며, `render(state)`를 구현해야 합니다.
- `Controller` (`mvc/controller.py`): 추상 메서드 `dispatch(command, *args) -> bool`. `__init__`에서 자기 자신을 모델 옵저버로 등록하며, 모델이 변경되면 기본적으로 뷰를 다시 렌더링합니다(더 세밀한 제어가 필요하면 `on_model_changed`를 오버라이드). `dispatch`가 `False`를 반환하면 앱 루프가 종료됩니다.
- `Application` (`mvc/app.py`): 하나의 Model/View/Controller 조합을 소유하고 read-eval-render 루프를 실행합니다 — 한 줄을 입력받아 `command, *args`로 분리한 뒤 `controller.dispatch(...)`를 호출하고, 핸들러에서 발생한 예외는 잡아서 `view.show_error`로 전달합니다. `controller`는 클래스(`(model, view)`로 생성됨) 또는 이미 만들어진 인스턴스 둘 다 받을 수 있습니다.

도메인 앱(SampleOrderSystem)은 필요에 따라 화면/도메인 영역별로 `Model`/`View`/`Controller`를 나누어 상속할 수 있지만, 모두 하나의 `Application` 루프를 공유합니다 — 메뉴 동작(등록, 주문, 승인/거절, 모니터링, 생산라인, 출고)을 추가하는 지점은 command dispatch입니다.

### `poc_json` — JSON 파일 영속성 + CRUD + 모니터링 도구

플랫 파일 "데이터베이스": 각 JSON 파일은 dict 레코드의 리스트를 담고 있으며, 각 레코드는 고유한 id 성격의 필드(`id_field`, 기본값 `"id"`)를 가집니다.

- `json_lib.py`: 원시 load/parse/save/문자열 변환(`load_json`, `parse_json`, `save_json`, `to_json_string`). `save_json`은 상위 디렉토리를 자동 생성하며, `ensure_ascii=False`를 사용합니다(한글이 이스케이프 없이 그대로 저장됨).
- `json_crud.py`: `create_item`/`read_all`/`read_by_id`/`update_item`/`delete_item`, 모두 `id_field` 기준으로 동작합니다. 파일이 없으면 빈 리스트로 취급합니다(`_load_records`). 읽을 때마다 파일 전체를 새로 로드합니다(메모리 캐시 없음) — 항상 최신 상태를 읽지만, 파일당 매 호출마다 O(n)이며 동시 쓰기에 대해 안전하지 않습니다.
- `admin_tool.py`: "데이터 모니터링 Tool" — REPL(`list`/`get <id>`/`refresh`/`watch [interval]`/`quit`) 또는 파일 mtime을 폴링해서 변경 시 다시 출력하는 `--watch` 모드. 데이터 파일마다 별도로 실행합니다(예: 주문용 하나, 시료용 하나).

도메인 영속성(시료, 주문, 생산 큐)은 각각 별도의 JSON 파일/`id_field`로 관리하고, `json_crud`의 함수들을 그대로 활용해서 구현하세요 — CRUD를 다시 만들지 마세요.

### `dummy_data_generator` — 스키마 기반 더미 데이터 생성기

`poc_json`에 의존합니다(`storage.py`가 `poc_json.json_lib.save_json`/`load_json`을 직접 호출합니다 — 이 두 패키지는 함께 다녀야 합니다).

- `generator.py`: 필드 타입 레지스트리(`FIELD_GENERATORS`: `int`, `float`, `bool`, `str`, `choice`, `name`, `email`, `uuid`, `date`, `constant`). 이 파일 내부를 건드리지 않고 도메인 전용 타입(예: 반도체 시료명 생성기)을 추가하려면 `register_field_type(name, func)`를 사용하세요. `generate_records(schema, count, seed=None, ...)` — 재현 가능한 테스트 픽스처가 필요하면 `seed`를 지정하고, `id_field`/`start_id`로 생성되는 기본키를 제어합니다.
- `storage.py`: `save_dummy_data`는 데이터를 생성한 뒤 `poc_json.save_json`으로 저장하며, `load_dummy_data`는 `poc_json.load_json`을 그대로 감싼 얇은 래퍼입니다.
- `cli.py`: `python -m dummy_data_generator.cli <schema.json> <output.json> --count N`

반도체 시료 주문관리 시스템의 테스트 데이터를 만들 때는 엔티티별(시료 카탈로그, 주문)로 스키마 dict를 하나씩 정의하고, 앱의 `poc_json` 기반 영속성 계층이 읽는 것과 동일한 JSON 파일에 대해 `save_dummy_data`/CLI를 실행하면 됩니다.

### `sample_order_system` — SampleOrderSystem 앱 (위 세 라이브러리로 구현됨)

콘솔 I/O 없이도 pytest로 검증 가능하도록, 비즈니스 로직은 도메인별 순수 모듈에 두고 `mvc`는 그 위의 얇은 UI 계층으로만 사용한다.

- `paths.py`: 데이터 파일 경로 상수.
- `samples/repository.py`: 시료 CRUD(`register_sample`/`list_samples`/`search_samples`/`get_sample`/`adjust_stock`), `poc_json` 위의 검증 포함 래퍼.
- `orders/`: `numbering.py`(주문번호 채번 `ORD-NNNNNN`), `repository.py`(예약/조회), `approval.py`(승인 시 재고 판정→`CONFIRMED`/`PRODUCING` 분기, 거절), `shipment.py`(출고: `CONFIRMED`→`RELEASE`, 재고 차감).
- `production/`: `queue.py`(FIFO 큐, `enqueue`/`advance` — 진행 시간은 실제 시계가 아니라 **수동 tick**(`advance(minutes)`)으로 흐름), `service.py`(`advance_production`: 완료된 항목의 재고 반영 + 주문 상태 전환까지 오케스트레이션 / `production_status`: 큐를 시료 저장소와 조인해 현재 처리 중 항목·대기 항목을 화면 표시용 필드(시료 이름, 재고량, 완료/예상 완료 시간 등)로 조립).
- `monitoring/service.py`: 상태별 주문 집계(`REJECTED` 제외), 시료별 재고 상태(여유/부족/고갈, "미출고 수요" = `RESERVED`+`PRODUCING`+`CONFIRMED` 주문 수량 합) 분류.
- `app/`: `model.py`(`mvc.Model`을 상속한 얇은 퍼사드, 화면 상태(`screen`)만 보유), `menus.py`(화면별 `(번호, 라벨)` 메뉴 정의 — view/controller가 함께 참조하는 단일 출처), `view.py`(`mvc.View`, 번호 선택 메뉴 출력), `controller.py`(`mvc.Controller`, 화면별 번호 라우팅. 자유 명령어 문자열은 쓰지 않고, 값이 필요한 동작은 `self.view.input("필드명: ")`을 필드마다 순차 호출해 받으며, 승인/거절/출고처럼 레코드를 고르는 동작은 번호 매긴 목록을 먼저 보여준 뒤 인덱스를 입력받아 처리한다), `formatting.py`(순수 포맷팅 함수 — 콘솔 I/O 없이 테스트 가능).
- `main.py`: `mvc.Application` 조립 진입점.
- `seed_demo_data.py`: `dummy_data_generator.generate_records()`로 필드 값만 생성하고, 저장은 검증 로직이 있는 `register_sample`/`reserve_order`를 통해서만 수행(도메인 검증을 우회하지 않기 위함).

각 모듈의 상세 설계/검증 근거는 `docs/phases/phaseN-*.md`를 참고하세요 — 특히 "수동 tick" 진행 방식과 "미출고 수요" 정의는 `docs/phases/phase0-foundation.md`에서 확정된 설계 결정입니다.
