from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

MART_PATH = Path("data/mart/variant_03/mart_daily_2026-03-28_22-41-14.csv")
TABLE_NAME = "mart_weather"

DB_URL = "postgresql+psycopg2://analytics:analytics_pass@localhost:5432/analytics_db"

def main():
    if not MART_PATH.exists():
        raise FileNotFoundError(f"Mart file not found:{MART_PATH}")
    df = pd.read_csv(MART_PATH)

    print("Loaded mart file:", MART_PATH)
    print("Shape", df.shape)
    print("Colums:", list(df.columns))
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
    print(f"Table '{TABLE_NAME}' loaded successfully.")

if __name__ == "__main__":
    main()
