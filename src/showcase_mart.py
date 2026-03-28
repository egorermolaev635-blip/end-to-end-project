import pandas as pd
from pathlib import Path
from datetime import datetime

df = pd.read_csv("data/normalized/variant_03/2026-03-08_21-33-20.csv")

print("Размер:", df.shape)
print("Колонки:", df.columns.tolist())
print(df.head())

df["city_id"] = "RU_NSK"

df["time"] = pd.to_datetime(df["time"])
df["date"] = pd.to_datetime(df["date"])

ref = pd.read_csv("reference/cities.csv")

print("Размер справочника:", ref.shape)
print("Колонки справочника:", ref.columns.tolist())
print("NULL в city_id:", ref["city_id"].isna().sum())
print("Дубликаты city_id:", ref["city_id"].duplicated().sum())

rows_before = len(df)

df_joined = df.merge(
    ref[["city_id", "city_name", "country_code"]],
    on="city_id",
    how="left",
    validate="many_to_one"
)

rows_after = len(df_joined)

print("Строк до merge:", rows_before)
print("Строк после merge:", rows_after)
print("NULL в city_name после merge:", df_joined["city_name"].isna().sum())

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
mart = mart.round(2)

print(mart.head())
print("Размер mart:", mart.shape)

out_dir = Path("data/mart/variant_03")
out_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
out_path = out_dir / f"mart_daily_{timestamp}.csv"

mart.to_csv(out_path, index=False)
print("Витрина сохранена:", out_path)
