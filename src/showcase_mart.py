import pandas as pd
import argparse
from pathlib import Path

NORMALIZED_DIR = Path("data/normalized/variant_03")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    target_date = args.date

    normalized_path = NORMALIZED_DIR / f"normalized_{target_date}.csv"
    if not normalized_path.exists():
        raise FileNotFoundError(f"Missing file: {normalized_path}")
        
    df = pd.read_csv(normalized_path)

    df["city_id"] = "RU_NSK"
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = pd.to_datetime(df["date"])

    ref = pd.read_csv("reference/cities.csv")

    df_joined = df.merge(
        ref[["city_id", "city_name", "country_code"]],
        on="city_id",
        how="left",
        validate="many_to_one"
    )

    mart = (
        df_joined
        .groupby(["date", "city_id", "city_name", "country_code"], as_index=False)
        .agg(
            temperature_mean=("temperature", "mean"),
            temperature_min=("temperature", "min"),
            temperature_max=("temperature", "max"),
        )
    )

    mart["temperature_range"] = mart["temperature_max"] - mart["temperature_min"]
    numeric_cols = ["temperature_mean", "temperature_min", "temperature_max", "temperature_range"]
    mart[numeric_cols] = mart[numeric_cols].round(2)

    out_dir = Path("data/mart/variant_03")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"mart_daily_{target_date}.csv"
    mart.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()
