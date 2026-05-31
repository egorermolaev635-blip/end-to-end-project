# LLM Context

Dataset identity: Open-Meteo archive, variant_03, city=Новосибирск.

Schema hints: one mart row = one day for one city. Temperature fields are in Celsius.

Mart file: data/mart/variant_03/mart_daily_2026-03-08.csv

Period: 2026-03-08 to 2026-03-08

Rows: 1

Cities count: 1; cities: Новосибирск

Computed metrics:

- temperature_mean_min=-0.50
- temperature_mean_max=-0.50
- temperature_mean_avg=-0.50
- temperature_min_abs=-1.50
- temperature_max_abs=0.40
- temperature_range_avg=1.90
- top_temperature_range_date=2026-03-08
- top_temperature_range_value=1.90
- last_date=2026-03-08
- last_temperature_mean=-0.50
- previous_date=not_available
- last_vs_previous_delta=not_available

Quality status: dq=PASS

Constraints:

- use only provided metrics;
- do not invent numbers;
- do not calculate new metrics;
- if data is insufficient, say that data is insufficient.
