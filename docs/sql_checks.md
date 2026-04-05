# SQL checks for mart_weather

## 1. Table is not empty
```sql
SELECT COUNT(*) AS row_count
FROM mart_weather;
```

## 2. Date range
```sql
SELECT MIN(date) AS min_date,
       MAX(date) AS max_date
FROM mart_weather;
```

## 3. NULL in key columns
```sql
SELECT COUNT(*) AS null_count
FROM mart_weather
WHERE date IS NULL OR city_id IS NULL;
```

## 4. Duplicates by business key (date + city_id)
```sql
SELECT date,
       city_id,
       COUNT(*) AS cnt
FROM mart_weather
GROUP BY date, city_id
HAVING COUNT(*) > 1;
```

## 5. Temperature sanity check
```sql
SELECT AVG(temperature_mean) AS avg_temp,
       MIN(temperature_min) AS min_temp,
       MAX(temperature_max) AS max_temp
FROM mart_weather;
```
