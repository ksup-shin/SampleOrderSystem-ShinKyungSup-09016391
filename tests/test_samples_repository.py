import pytest

from sample_order_system.samples.repository import (
    register_sample,
    list_samples,
    search_samples,
    get_sample,
)


@pytest.fixture
def samples_file(tmp_path):
    return tmp_path / "samples.json"


def test_register_sample_persists_record(samples_file):
    register_sample(
        "S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92,
        initial_stock=480, file_path=samples_file,
    )

    samples = list_samples(file_path=samples_file)

    assert samples == [{
        "id": "S-001",
        "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5,
        "yield_rate": 0.92,
        "stock": 480,
    }]


def test_register_sample_rejects_duplicate_id(samples_file):
    register_sample("S-001", "A", 0.5, 0.9, file_path=samples_file)

    with pytest.raises(ValueError):
        register_sample("S-001", "B", 0.4, 0.8, file_path=samples_file)


@pytest.mark.parametrize("yield_rate", [0, -0.1, 1.1, 2])
def test_register_sample_rejects_invalid_yield_rate(samples_file, yield_rate):
    with pytest.raises(ValueError):
        register_sample("S-001", "A", 0.5, yield_rate, file_path=samples_file)


@pytest.mark.parametrize("avg_production_time", [0, -1])
def test_register_sample_rejects_non_positive_production_time(
    samples_file, avg_production_time
):
    with pytest.raises(ValueError):
        register_sample(
            "S-001", "A", avg_production_time, 0.9, file_path=samples_file
        )


def test_list_samples_returns_all_registered_samples(samples_file):
    register_sample("S-001", "A", 0.5, 0.9, file_path=samples_file)
    register_sample("S-002", "B", 0.3, 0.8, file_path=samples_file)

    samples = list_samples(file_path=samples_file)

    assert [s["id"] for s in samples] == ["S-001", "S-002"]


def test_search_samples_matches_partial_name_case_insensitively(samples_file):
    register_sample("S-001", "Silicon Wafer", 0.5, 0.9, file_path=samples_file)
    register_sample("S-002", "GaN Epitaxial", 0.3, 0.8, file_path=samples_file)

    results = search_samples("silicon", file_path=samples_file)

    assert [s["id"] for s in results] == ["S-001"]


def test_search_samples_returns_empty_when_no_match(samples_file):
    register_sample("S-001", "Silicon Wafer", 0.5, 0.9, file_path=samples_file)

    assert search_samples("없는이름", file_path=samples_file) == []


def test_get_sample_returns_none_when_missing(samples_file):
    assert get_sample("S-999", file_path=samples_file) is None
