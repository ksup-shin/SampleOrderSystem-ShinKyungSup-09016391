"""dummy_data_generator를 이용해 데모/테스트용 시료·주문 데이터를 시딩한다.

사용 예:
    python -m sample_order_system.seed_demo_data --samples 20 --orders 30 --seed 42
"""

import argparse
import random

from dummy_data_generator.generator import generate_records

from .paths import SAMPLES_FILE, ORDERS_FILE
from .samples.repository import register_sample
from .orders.repository import reserve_order

SAMPLE_NAMES = [
    "실리콘 웨이퍼-8인치", "GaN 에피탁셜-4인치", "SiC 파워기판-6인치",
    "포토레지스트-PR7", "산화막 웨이퍼-SiO2",
]

SAMPLE_SCHEMA = {
    "name": {"type": "choice", "values": SAMPLE_NAMES},
    "avg_production_time": {"type": "float", "min": 0.2, "max": 1.0, "ndigits": 2},
    "yield_rate": {"type": "float", "min": 0.7, "max": 0.99, "ndigits": 2},
    "stock": {"type": "int", "min": 0, "max": 500},
}

CUSTOMER_NAMES = ["삼성전자 파운드리", "SK하이닉스", "LG이노텍", "DB하이텍", "대학 연구실"]

ORDER_SCHEMA = {
    "customer": {"type": "choice", "values": CUSTOMER_NAMES},
    "quantity": {"type": "int", "min": 1, "max": 300},
}


def build_sample_id(index):
    return f"S-{index + 1:03d}"


def seed_samples(count, seed=None, samples_file=SAMPLES_FILE):
    records = generate_records(SAMPLE_SCHEMA, count, seed=seed)
    return [
        register_sample(
            build_sample_id(index), record["name"], record["avg_production_time"],
            record["yield_rate"], initial_stock=record["stock"], file_path=samples_file,
        )
        for index, record in enumerate(records)
    ]


def seed_orders(sample_ids, count, seed=None, orders_file=ORDERS_FILE, samples_file=SAMPLES_FILE):
    records = generate_records(ORDER_SCHEMA, count, seed=seed)
    rng = random.Random(seed)
    return [
        reserve_order(
            rng.choice(sample_ids), record["customer"], record["quantity"],
            orders_file=orders_file, samples_file=samples_file,
        )
        for record in records
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description="데모용 시료/주문 더미 데이터 시딩")
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--orders", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)

    samples = seed_samples(args.samples, seed=args.seed)
    sample_ids = [sample["id"] for sample in samples]
    orders = seed_orders(sample_ids, args.orders, seed=args.seed)
    print(f"시료 {len(samples)}건, 주문 {len(orders)}건 시딩 완료")


if __name__ == "__main__":
    main()
