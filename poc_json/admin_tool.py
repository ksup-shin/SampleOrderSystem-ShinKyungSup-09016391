"""저장된 JSON 데이터 상태를 콘솔에서 실시간으로 조회하는 관리자 도구.

다른 프로젝트에서 사용하려면:
    python -m poc_json.admin_tool <데이터파일.json>            # 대화형 조회
    python -m poc_json.admin_tool <데이터파일.json> --watch    # 실시간 감시 모드
"""

import argparse
import time
from pathlib import Path

from .json_crud import read_all, read_by_id
from .json_lib import to_json_string


def _print_records(records):
    print(to_json_string(records))


def _coerce(value):
    """id 값이 숫자면 int로 변환하고, 아니면 문자열 그대로 사용한다."""
    try:
        return int(value)
    except ValueError:
        return value


def watch(file_path, id_field, interval):
    """파일 변경을 감지하여 바뀔 때마다 전체 상태를 출력한다."""
    path = Path(file_path)
    last_mtime = None
    print(f"[watch] {path} 감시 시작 (Ctrl+C로 종료)")
    try:
        while True:
            mtime = path.stat().st_mtime if path.exists() else None
            if mtime != last_mtime:
                last_mtime = mtime
                records = read_all(file_path)
                print(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} 변경 감지 (레코드 {len(records)}개) ===")
                _print_records(records)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[watch] 종료")


def repl(file_path, id_field):
    """대화형 콘솔에서 조회 명령을 받는다."""
    print(f"관리자 도구 - {file_path}")
    print("명령어: list / get <id> / refresh / watch [interval] / quit")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue
        parts = cmd.split()
        action = parts[0]

        if action in ("quit", "exit", "q"):
            break
        elif action in ("list", "refresh"):
            records = read_all(file_path)
            print(f"레코드 {len(records)}개")
            _print_records(records)
        elif action == "get" and len(parts) == 2:
            record = read_by_id(file_path, _coerce(parts[1]), id_field)
            if record is None:
                print("해당 id의 레코드가 없습니다.")
            else:
                _print_records(record)
        elif action == "watch":
            interval = float(parts[1]) if len(parts) > 1 else 1.0
            watch(file_path, id_field, interval)
        else:
            print("알 수 없는 명령입니다. list / get <id> / refresh / watch / quit 중 하나를 입력하세요.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="저장된 JSON 데이터 상태를 콘솔에서 조회하는 관리자 도구")
    parser.add_argument("file", help="조회할 JSON 데이터 파일 경로")
    parser.add_argument("--id-field", default="id", help="레코드 식별자 필드명 (기본값: id)")
    parser.add_argument("--watch", action="store_true", help="대화형 대신 바로 실시간 감시 모드로 시작")
    parser.add_argument("--interval", type=float, default=1.0, help="감시 모드 폴링 주기(초, 기본값: 1)")
    args = parser.parse_args(argv)

    if args.watch:
        watch(args.file, args.id_field, args.interval)
    else:
        repl(args.file, args.id_field)


if __name__ == "__main__":
    main()
