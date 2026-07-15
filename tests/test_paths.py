from sample_order_system import paths
from poc_json import read_all


def test_samples_file_and_orders_file_start_empty_when_missing(tmp_path):
    samples_file = tmp_path / "samples.json"
    orders_file = tmp_path / "orders.json"

    assert read_all(samples_file) == []
    assert read_all(orders_file) == []


def test_default_data_paths_are_under_data_directory():
    assert paths.SAMPLES_FILE.name == "samples.json"
    assert paths.ORDERS_FILE.name == "orders.json"
    assert paths.PRODUCTION_QUEUE_FILE.name == "production_queue.json"
    assert paths.DATA_DIR.name == "data"
