import argparse
import json
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "variant_03"
NORMALIZED_DIR = PROJECT_ROOT / "data" / "normalized" / "variant_03"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    target_date = args.date

    raw_path = RAW_DIR / f"raw_{target_date}.json"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing file: {raw_path}")

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hourly = data.get("hourly", {})
    if "time" not in hourly or "temperature_2m" not in hourly:
        raise ValueError("Raw file does not contain hourly.time or hourly.temperature_2m")

    df = pd.DataFrame(
        {
            "time": hourly["time"],
            "temperature": hourly["temperature_2m"],
        }
    )
    df["time"] = pd.to_datetime(df["time"])
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df = df.dropna(subset=["time", "temperature"])
    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour
    df["latitude"] = data.get("latitude")
    df["longitude"] = data.get("longitude")

    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    normalized_path = NORMALIZED_DIR / f"normalized_{target_date}.csv"
    df.to_csv(normalized_path, index=False)

    print(f"normalized rows: {len(df)}")
    print(f"normalized saved: {normalized_path}")

    mart_script = PROJECT_ROOT / "src" / "showcase_mart.py"
    import subprocess
    import sys

    mart_result = subprocess.run(
        [sys.executable, str(mart_script), "--date", target_date],
        cwd=PROJECT_ROOT,
    )
    if mart_result.returncode != 0:
        raise RuntimeError("Ошибка при построении mart")


if __name__ == "__main__":
    main()
