import pytest

from sample_order_system.seed_demo_data import build_sample_id, seed_samples, seed_orders


@pytest.fixture
def files(tmp_path):
    return {
        "samples_file": tmp_path / "samples.json",
        "orders_file": tmp_path / "orders.json",
    }


def test_build_sample_id_formats_with_zero_padding():
    assert build_sample_id(0) == "S-001"
    assert build_sample_id(9) == "S-010"


def test_seed_samples_creates_requested_count_with_unique_ids(files):
    samples = seed_samples(5, seed=42, samples_file=files["samples_file"])

    assert len(samples) == 5
    assert len({s["id"] for s in samples}) == 5


def test_seed_samples_is_reproducible_with_same_seed(files, tmp_path):
    other_file = tmp_path / "other_samples.json"

    first = seed_samples(5, seed=42, samples_file=files["samples_file"])
    second = seed_samples(5, seed=42, samples_file=other_file)

    first_values = [{k: v for k, v in s.items()} for s in first]
    second_values = [{k: v for k, v in s.items()} for s in second]
    assert first_values == second_values


def test_seed_orders_only_references_provided_sample_ids(files):
    samples = seed_samples(3, seed=1, samples_file=files["samples_file"])
    sample_ids = [s["id"] for s in samples]

    orders = seed_orders(
        sample_ids, 10, seed=1,
        orders_file=files["orders_file"], samples_file=files["samples_file"],
    )

    assert len(orders) == 10
    assert all(order["sample_id"] in sample_ids for order in orders)
