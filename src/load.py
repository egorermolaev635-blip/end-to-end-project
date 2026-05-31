import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect, text


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MART_DIR = Path(os.getenv("MART_DIR", PROJECT_ROOT / "data" / "mart" / "variant_03"))
TABLE_NAME = os.getenv("TABLE_NAME", "mart_weather")
DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://analytics:analytics_pass@localhost:5432/analytics_db",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    target_date = args.date

    if not MART_DIR.exists():
        raise FileNotFoundError(f"Folder with mart not found: {MART_DIR}")

    mart_path = MART_DIR / f"mart_daily_{target_date}.csv"
    if not mart_path.exists():
        raise FileNotFoundError(f"Missing file: {mart_path}")

    df = pd.read_csv(mart_path)
    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        table_exists = inspect(conn).has_table(TABLE_NAME)

        if table_exists:
            delete_query = text(f"DELETE FROM {TABLE_NAME} WHERE date = :target_date")
            conn.execute(delete_query, {"target_date": target_date})

        df.to_sql(
            TABLE_NAME,
            con=conn,
            if_exists="append",
            index=False,
        )

    print(f"loaded rows to postgres: {len(df)}")
    print(f"table: {TABLE_NAME}")
    print(f"source: {mart_path}")


if __name__ == "__main__":
    main()
