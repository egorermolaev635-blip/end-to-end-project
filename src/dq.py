import argparse
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MART_DIR = PROJECT_ROOT / "data" / "mart" / "variant_03"
REPORT_PATH = PROJECT_ROOT / "docs" / "dq_report.json"


def result(name, status, reason, details=None):
    return {
        "check": name,
        "status": status,
        "reason": reason,
        "details": details or {},
    }


def check_columns_exist(df, columns):
    missing = [col for col in columns if col not in df.columns]

    if missing:
        return result(
            "required_columns_exist",
            "FAIL",
            "Required columns are missing",
            {"missing_columns": missing},
        )

    return result(
        "required_columns_exist",
        "PASS",
        "All required columns exist",
        {"columns": columns},
    )


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
        return result(
            "unique_business_key",
            "FAIL",
            "Business key has duplicates",
            {
                "key": columns,
                "duplicates": duplicates,
            },
        )

    return result(
        "unique_business_key",
        "PASS",
        "Business key is unique",
        {"key": columns},
    )


def check_temperature_range(df):
    columns = ["temperature_mean", "temperature_min", "temperature_max"]
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
        return result(
            "temperature_min_max_logic",
            "FAIL",
            "temperature_min is greater than temperature_max",
            {"bad_rows": bad_rows},
        )

    return result("temperature_min_max_logic", "PASS", "temperature_min <= temperature_max")


def check_country_code(df):
    allowed = {"RU"}
    bad_rows = int((~df["country_code"].isin(allowed)).sum())

    if bad_rows > 0:
        return result(
            "country_code_enum",
            "WARNING",
            "Unexpected country_code values found",
            {
                "allowed": list(allowed),
                "bad_rows": bad_rows,
            },
        )

    return result("country_code_enum", "PASS", "country_code values are valid")


def run_dq():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    target_date = args.date

    csv_path = MART_DIR / f"mart_daily_{target_date}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}")

    df = pd.read_csv(csv_path)

    required_columns = [
        "date",
        "city_id",
        "city_name",
        "country_code",
        "temperature_mean",
        "temperature_min",
        "temperature_max",
        "temperature_range",
    ]

    checks = [
        check_columns_exist(df, required_columns),
    ]

    if checks[0]["status"] == "PASS":
        checks.extend(
            [
                check_non_empty(df),
                check_not_null(df, ["date", "city_id", "city_name", "country_code"]),
                check_unique_key(df, ["date", "city_id"]),
                check_temperature_range(df),
                check_temperature_logic(df),
                check_country_code(df),
            ]
        )

    report = {
        "source_file": str(csv_path),
        "rows": len(df),
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    pass_n = sum(1 for check in checks if check["status"] == "PASS")
    warning_n = sum(1 for check in checks if check["status"] == "WARNING")
    fail_n = sum(1 for check in checks if check["status"] == "FAIL")

    print(f"dq checks: PASS={pass_n} WARNING={warning_n} FAIL={fail_n}")
    print(f"dq report saved: {REPORT_PATH}")

    if fail_n > 0:
        raise ValueError(f"CRITICAL: DQ checks failed for period {target_date}. Load aborted.")

    return report


if __name__ == "__main__":
    run_dq()
