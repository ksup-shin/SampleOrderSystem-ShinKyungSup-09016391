# CLAUDE.md

이 파일은 이 저장소에서 작업하는 Claude Code(claude.ai/code)에게 제공하는 가이드입니다.

## 프로젝트 개요

S-Semi(가상의 반도체 회사)의 "반도체 시료 생산주문관리 시스템"(SampleOrderSystem)을 만드는 저장소입니다. 시료 등록, 고객 주문 접수/승인/거절, 단일 생산 라인(FIFO), 모니터링, 출고 처리를 다루는 콘솔(CUI) 애플리케이션입니다.

**요구사항(비즈니스 규칙, 기능 명세, 상태 흐름 등)은 전부 `docs/PRD.md`에 있습니다.** 기능을 구현하기 전에 반드시 그 문서를 먼저 확인하세요. 이 파일(CLAUDE.md)에는 기술스택/아키텍처/개발 방법만 다룹니다.

이 저장소에는 현재 재사용 가능한 라이브러리 패키지 3개(`mvc`, `poc_json`, `dummy_data_generator`)만 존재하며, 이를 기반으로 한 실제 애플리케이션은 아직 없습니다. 해야 할 일은 이 세 라이브러리를 그대로 재사용하여 SampleOrderSystem 앱을 만드는 것입니다 — 실제 한계가 발견되지 않는 한 이 라이브러리들을 수정하지 마세요.

## 기술 스택

- Python (표준 라이브러리 위주, 외부 의존성 없음), 로컬 `.venv` 사용.
- 영속성: `poc_json`을 통한 JSON 파일 기반 저장/조회 (DB 없음).
- 테스트: **pytest** 사용 (아래 "테스트" 참고). 아직 `pytest`가 의존성으로 선언되어 있지 않으므로, 테스트를 추가할 때 `.venv`에 설치하고 의존성 관리 파일(예: `requirements.txt` 또는 `pyproject.toml`)을 함께 만들 것.
- 아직 git 저장소, 린터/포매터, CI 설정은 없습니다. 필요 시 구성하고 이 문서에 반영하세요.

## 명령어

- 모듈 실행: `.venv/Scripts/python.exe -m <module.path>` (예: `.venv/Scripts/python.exe -m dummy_data_generator.cli schema.json out.json --count 20`)
- JSON 관리자/모니터링 도구(대화형): `.venv/Scripts/python.exe -m poc_json.admin_tool <data.json>`
- JSON 관리자/모니터링 도구(실시간 감시): `.venv/Scripts/python.exe -m poc_json.admin_tool <data.json> --watch`
- 더미 데이터 생성 CLI: `.venv/Scripts/python.exe -m dummy_data_generator.cli <schema.json> <output.json> --count N [--seed N] [--id-field id] [--start-id 1]`

### 테스트

- 테스트 프레임워크는 **pytest**를 사용합니다(unittest 대신 pytest 채택).
- 전체 테스트 실행: `.venv/Scripts/python.exe -m pytest`
- 단일 파일 실행: `.venv/Scripts/python.exe -m pytest tests/test_x.py`
- 단일 테스트 함수 실행: `.venv/Scripts/python.exe -m pytest tests/test_x.py::test_name`
- 더미 데이터 생성기의 `seed` 옵션을 활용하면 재현 가능한 테스트 픽스처를 만들 수 있습니다.

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
