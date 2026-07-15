"""더미 데이터를 커맨드라인에서 생성/저장하는 CLI.

다른 프로젝트에서 사용하려면:
    python -m dummy_data_generator.cli <스키마파일.json> <출력파일.json> --count 10
"""

import argparse

from poc_json.json_lib import load_json

from .storage import save_dummy_data


def main(argv=None):
    parser = argparse.ArgumentParser(description="스키마 기반 더미 데이터 생성기")
    parser.add_argument("schema", help="필드 스키마가 정의된 JSON 파일 경로")
    parser.add_argument("output", help="생성된 더미 데이터를 저장할 JSON 파일 경로")
    parser.add_argument("--count", type=int, default=10, help="생성할 레코드 개수 (기본값: 10)")
    parser.add_argument("--seed", type=int, default=None, help="난수 시드 (재현 가능한 데이터 생성용)")
    parser.add_argument("--id-field", default="id", help="레코드 식별자 필드명 (기본값: id)")
    parser.add_argument("--start-id", type=int, default=1, help="첫 레코드의 id 값 (기본값: 1)")
    args = parser.parse_args(argv)

    schema = load_json(args.schema)
    records = save_dummy_data(
        schema,
        args.output,
        args.count,
        seed=args.seed,
        id_field=args.id_field,
        start_id=args.start_id,
    )
    print(f"{args.output} 에 더미 레코드 {len(records)}개를 저장했습니다.")


if __name__ == "__main__":
    main()
