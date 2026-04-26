from pathlib import Path
import json
import pandas as pd


MART_DIR = Path("data/mart/variant_03")
REPORT_PATH = Path("data/dq_report.json")


def latest_csv(folder: Path) -> Path:
    files = sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"CSV files not found in {folder}")
    return files[0]


def result(name, status, reason, details=None):
    return {
        "check": name,
        "status": status,
        "reason": reason,
        "details": details or {}
    }


def check_non_empty(df):
    if df.empty:
        return result("table_non_empty", "FAIL", "Table is empty")
    return result("table_non_empty", "PASS", "Table is not empty", {"rows": len(df)})


def check_not_null(df, columns):
    bad = {}
    for col in columns:
        bad[col] = int(df[col].isna().sum())

    total_bad = sum(bad.values())

    if total_bad > 0:
        return result("not_null_critical_fields", "FAIL", "Critical fields contain NULL", bad)

    return result("not_null_critical_fields", "PASS", "Critical fields do not contain NULL", bad)


def check_unique_key(df, columns):
    duplicates = int(df.duplicated(subset=columns).sum())

    if duplicates > 0:
        return result("unique_business_key", "FAIL", "Business key has duplicates", {
            "key": columns,
            "duplicates": duplicates
        })

    return result("unique_business_key", "PASS", "Business key is unique", {
        "key": columns
    })


def check_temperature_range(df):
    columns = [
        "temperature_mean",
        "temperature_min",
        "temperature_max"
    ]

    problems = {}

    for col in columns:
        bad_count = int(((df[col] < -90) | (df[col] > 60)).sum())
        problems[col] = bad_count

    if sum(problems.values()) > 0:
        return result("temperature_range", "FAIL", "Temperature is outside realistic range", problems)

    return result("temperature_range", "PASS", "Temperature values are realistic", problems)


def check_temperature_logic(df):
    bad_rows = int((df["temperature_min"] > df["temperature_max"]).sum())

    if bad_rows > 0:
        return result("temperature_min_max_logic", "FAIL", "temperature_min is greater than temperature_max", {
            "bad_rows": bad_rows
        })

    return result("temperature_min_max_logic", "PASS", "temperature_min <= temperature_max")


def check_country_code(df):
    allowed = {"RU"}
    bad_rows = int(~df["country_code"].isin(allowed).sum())

    if bad_rows > 0:
        return result("country_code_enum", "WARNING", "Unexpected country_code values found", {
            "allowed": list(allowed),
            "bad_rows": bad_rows
        })

    return result("country_code_enum", "PASS", "country_code values are valid")


def run_dq():
    csv_path = latest_csv(MART_DIR)
    df = pd.read_csv(csv_path)

    checks = [
        check_non_empty(df),
        check_not_null(df, ["date", "city_id", "city_name", "country_code"]),
        check_unique_key(df, ["date", "city_id"]),
        check_temperature_range(df),
        check_temperature_logic(df),
        check_country_code(df)
    ]

    report = {
        "source_file": str(csv_path),
        "rows": len(df),
        "checks": checks
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    print(json.dumps(report, ensure_ascii=False, indent=4))

    has_fail = any(check["status"] == "FAIL" for check in checks)

    if has_fail:
        raise ValueError("DQ checks failed")

    return report


if __name__ == "__main__":
    run_dq()
