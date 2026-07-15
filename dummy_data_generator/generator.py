"""스키마를 기반으로 더미(테스트용) 데이터를 생성하는 핵심 로직.

필드 타입별 생성기를 register 해두고, 스키마(dict)를 넘기면
그 스키마에 맞는 레코드(dict)들을 생성한다.

스키마 예:
    schema = {
        "name": {"type": "name"},
        "age": {"type": "int", "min": 20, "max": 60},
        "email": {"type": "email"},
        "is_active": {"type": "bool"},
        "role": {"type": "choice", "values": ["admin", "user", "guest"]},
        "score": {"type": "float", "min": 0, "max": 100, "ndigits": 2},
        "joined_at": {"type": "date", "start": "2020-01-01", "end": "2024-12-31"},
        "uid": {"type": "uuid"},
    }
"""

import random
import string
import uuid
from datetime import date, timedelta

_FIRST_NAMES = [
    "민준", "서연", "도윤", "하은", "지호", "지우", "예준", "채원",
    "시우", "수아", "유준", "지아", "준우", "서윤", "현우", "다은",
]
_LAST_NAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]

_EMAIL_DOMAINS = ["example.com", "test.com", "mail.com", "sample.org"]


def _gen_int(rng, field):
    return rng.randint(field.get("min", 0), field.get("max", 100))


def _gen_float(rng, field):
    value = rng.uniform(field.get("min", 0.0), field.get("max", 1.0))
    return round(value, field.get("ndigits", 2))


def _gen_bool(rng, field):
    return rng.random() < field.get("true_ratio", 0.5)


def _gen_str(rng, field):
    length = field.get("length", 8)
    charset = field.get("charset", string.ascii_lowercase + string.digits)
    return "".join(rng.choice(charset) for _ in range(length))


def _gen_choice(rng, field):
    values = field.get("values")
    if not values:
        raise ValueError("choice 타입 필드에는 'values' 목록이 필요합니다.")
    return rng.choice(values)


def _gen_name(rng, field):
    return rng.choice(_LAST_NAMES) + rng.choice(_FIRST_NAMES)


def _gen_email(rng, field):
    local = "".join(rng.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    domain = rng.choice(field.get("domains", _EMAIL_DOMAINS))
    return f"{local}@{domain}"


def _gen_uuid(rng, field):
    return str(uuid.UUID(int=rng.getrandbits(128)))


def _parse_date(value):
    return date.fromisoformat(value) if isinstance(value, str) else value


def _gen_date(rng, field):
    start = _parse_date(field.get("start", "2020-01-01"))
    end = _parse_date(field.get("end", "2024-12-31"))
    span = (end - start).days
    if span < 0:
        raise ValueError("date 타입 필드의 'start'는 'end'보다 이전이어야 합니다.")
    offset = rng.randint(0, span)
    return (start + timedelta(days=offset)).isoformat()


def _gen_constant(rng, field):
    return field.get("value")


FIELD_GENERATORS = {
    "int": _gen_int,
    "float": _gen_float,
    "bool": _gen_bool,
    "str": _gen_str,
    "choice": _gen_choice,
    "name": _gen_name,
    "email": _gen_email,
    "uuid": _gen_uuid,
    "date": _gen_date,
    "constant": _gen_constant,
}


def register_field_type(name, func):
    """새로운 필드 타입 생성기를 등록한다. func(rng, field_spec) -> value 형태여야 한다."""
    FIELD_GENERATORS[name] = func


def generate_record(schema, rng, index=0, id_field="id", start_id=1):
    """스키마에 맞는 레코드 하나를 생성한다."""
    record = {id_field: start_id + index}
    for field_name, field_spec in schema.items():
        field_type = field_spec.get("type")
        generator = FIELD_GENERATORS.get(field_type)
        if generator is None:
            raise ValueError(f"알 수 없는 필드 타입입니다: {field_type!r}")
        record[field_name] = generator(rng, field_spec)
    return record


def generate_records(schema, count, seed=None, id_field="id", start_id=1):
    """스키마에 맞는 더미 레코드를 count개 생성해 list로 반환한다.

    seed를 지정하면 항상 같은 결과가 재현된다(테스트 데이터의 결정성 확보용).
    """
    if count < 0:
        raise ValueError("count는 0 이상이어야 합니다.")

    rng = random.Random(seed)
    return [
        generate_record(schema, rng, index=i, id_field=id_field, start_id=start_id)
        for i in range(count)
    ]
