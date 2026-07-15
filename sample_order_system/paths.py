"""데이터 파일 경로 상수."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLES_FILE = DATA_DIR / "samples.json"
ORDERS_FILE = DATA_DIR / "orders.json"
PRODUCTION_QUEUE_FILE = DATA_DIR / "production_queue.json"
