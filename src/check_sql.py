import os

from sqlalchemy import create_engine, text


DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://analytics:analytics_pass@localhost:5432/analytics_db",
)

engine = create_engine(DB_URL)

queries = [
    "SELECT COUNT(*) FROM mart_weather",
    "SELECT MIN(date), MAX(date) FROM mart_weather",
    """
    SELECT date, city_id, COUNT(*)
    FROM mart_weather
    GROUP BY date, city_id
    HAVING COUNT(*) > 1
    """,
]

with engine.connect() as conn:
    for query in queries:
        print("\n--- QUERY ---")
        print(query)

        result = conn.execute(text(query))

        for row in result:
            print("RESULT:", row)
