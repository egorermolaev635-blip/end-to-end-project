import pandas as pd

from src.dq import (
    check_non_empty,
    check_not_null,
    check_unique_key,
    check_temperature_range,
    check_temperature_logic
)


def test_non_empty_pass():
    df = pd.DataFrame({"x": [1, 2, 3]})
    res = check_non_empty(df)
    assert res["status"] == "PASS"


def test_not_null_fail():
    df = pd.DataFrame({
        "date": ["2026-03-08", None],
        "city_id": ["RU_NSK", "RU_NSK"]
    })

    res = check_not_null(df, ["date", "city_id"])
    assert res["status"] == "FAIL"


def test_unique_key_fail():
    df = pd.DataFrame({
        "date": ["2026-03-08", "2026-03-08"],
        "city_id": ["RU_NSK", "RU_NSK"]
    })

    res = check_unique_key(df, ["date", "city_id"])
    assert res["status"] == "FAIL"


def test_temperature_range_fail():
    df = pd.DataFrame({
        "temperature_mean": [20, 100],
        "temperature_min": [10, 15],
        "temperature_max": [25, 30]
    })

    res = check_temperature_range(df)
    assert res["status"] == "FAIL"


def test_temperature_logic_fail():
    df = pd.DataFrame({
        "temperature_min": [10, 30],
        "temperature_max": [20, 15]
    })

    res = check_temperature_logic(df)
    assert res["status"] == "FAIL"
