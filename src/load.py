from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import os

MART_DIR = Path(os.getenv("MART_DIR", "data/mart/variant_03"))
TABLE_NAME = os.getenv("TABLE_NAME", "mart_weather")

DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://analytics:analytics_pass@localhost:5432/analytics_db"
)

def get_latest_mart_file(mart_dir: Path) -> Path:
    files = list(mart_dir.glob("*.csv"))

    if not files:
        raise FileNotFoundError(f"В папке нет mart-файлов: {mart_dir}")

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    return latest_file

def main():
    if not MART_DIR.exists():
        raise FileNotFoundError(f"Folder with mart not found: {MART_DIR}")
    mart_path = get_latest_mart_file(MART_DIR)
    df = pd.read_csv(mart_path)
    print("Loaded mart file:", mart_path)
    print("Shape", df.shape)
    print("Columns:", list(df.columns))
    print("Dtypes:")
    print(df.dtypes)

    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        df.to_sql(
            TABLE_NAME,
            con = conn,
            if_exists="replace",
            index=False
        )
    print(f"loaded rows to postgres: {len(df)}")
    print(f"table: {TABLE_NAME}")
    print(f"Table '{TABLE_NAME}' loaded successfully.")

if __name__ == "__main__":
    main()
