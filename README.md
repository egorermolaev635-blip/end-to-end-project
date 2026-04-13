# end-to-end-project

## Запуск проекта (Windows)

### Вариант 1. Через Git
1. git clone https://github.com/egorermolaev635-blip/end-to-end-project.git
2. cd project
3. scripts\setup_env.bat

### Вариант 2: ZIP + двойной клик
1. Скачайте ZIP с GitHub
2. Распакуйте в любую папку
3. Двойной клик на scripts\setup_env.bat

---

## Проверка (smoke test)

conda run -n data-project python broken_env.py

### Ожидаемый результат:

python: C:\...\envs\data-project\python.exe  
pandas: 2.1.4

---

## Week 2 — API Extract (variant_03)

### Вариант 1
conda run -n data-project python src/extract.py  

### Вариант 2
python src/extract.py (если активирована среда)

---

### Ожидаемый результат

Variant: 3 - Погода (архив) - Новосибирск  

URL: https://archive-api.open-meteo.com/v1/archive  

Params: {'latitude': 55.75, 'longitude': 37.62, ...}  

Status: 200  

Data: 1234  

Saved: data/raw/variant_03/YYYY-MM-DD_HH-MM-SS.json  

---

### Файлы создаются

data/raw/variant_03/YYYY-MM-DD_HH-MM-SS.json  ← raw API ответ  
docs/Data_Contract.md                         ← документация API  

---

### Требования

- Windows 10/11  
- Anaconda/Miniconda  

---

## Week 3 — Data Normalization (Pandas)

### Что сделано

- raw JSON преобразован в DataFrame  
- определено зерно: 1 строка = 1 час наблюдения  
- выполнена базовая очистка данных  

---

### Очистка

- `time` → datetime  
- `temperature` → float  
- проверка и удаление пропусков  
- добавлены признаки: `date`, `hour`  

---

### Результат

Данные сохранены в:
data/normalized/variant_03/.csv

Параметр: `index=False`

---

### Data Contract

Добавлена схема normalized-слоя:

- поля  
- типы данных  
- nullable  
- описание колонок  

---

### Итог

Собран pipeline:
raw JSON → DataFrame → очистка → CSV

---

## Week 4 — Mart (Группировки и агрегаты)

### Что сделано

- normalized-данные агрегированы в дневную витрину  
- добавлен `city_id` из config  
- создан справочник `reference/cities.csv`  
- выполнен join по `city_id`  
- проверено отсутствие many-to-many  
- рассчитаны KPI  

---

### Гранулярность

Одна строка = один день по одному городу  

---

### KPI витрины

- средняя температура за день  
- минимальная температура  
- максимальная температура  
- диапазон температуры  

---

### Результат

Витрина сохраняется в:
data/mart/variant_03/mart_daily_.csv

---

### Итог

Собран полный pipeline:
raw JSON → normalized CSV → mart CSV

---

## Week 5 — PostgreSQL (Загрузка и SQL-проверки)

### Что сделано
1.mart-данные загружены в PostgreSQL
2.реализован скрипт загрузки load.py
3.использована транзакция через engine.begin()
4.обеспечена идемпотентность загрузки (if_exists="replace")
5.выполнены SQL-проверки качества данных

### Подключение
- host: localhost
- port: 5432
- database: analytics_db
- user: analytics
- password: analytics_pass

### Загрузка
Запуск:

```bash
python src/load.py
```

### Что происходит
- чтение mart CSV
- проверка структуры DataFrame (shape, columns, dtypes)
- подключение к базе
- загрузка в таблицу mart_weather

### Идемпотентность
Повторный запуск не создаёт дубли
таблица пересоздаётся при каждой загрузке

### SQL-проверки
Проверки описаны в: docs/sql_checks.md

### Выполнены проверки:
таблица не пустая (COUNT)
диапазон дат (MIN/MAX)
NULL в ключевых колонках
дубли по (date, city_id)
проверка температурных метрик

### Результат
Данные загружены в PostgreSQL
таблица: mart_weather
SQL-запросы успешно выполняются
данные прошли базовые проверки качества

## Week 6 — ETL Pipeline (Слои, state, incremental)

### Что сделано

- объединены все этапы в единый pipeline (pipeline.py)  
- реализована единая команда запуска  
- добавлены режимы:
  - full
  - incremental  
- устранён хардкод путей во всех слоях  
- реализовано автоматическое связывание слоёв (raw → normalized → mart)  
- добавлен state.json для хранения состояния пайплайна  
- реализован watermark (по максимальной дате)  
- обеспечена идемпотентность пайплайна  

---

### Запуск pipeline

Full режим:
python src/pipeline.py --mode full

Incremental режим:
python src/pipeline.py --mode incremental

---

### Что происходит

Pipeline выполняет шаги:

1. Extract
   - получение данных из API  
   - сохранение в data/raw/variant_03/

2. Transform (notebook)
   - берётся последний raw-файл  
   - выполняется очистка и преобразование  
   - сохраняется новый файл в data/normalized/variant_03/

3. Mart
   - берётся последний normalized  
   - строится дневная витрина  
   - сохраняется в data/mart/variant_03/

4. Load
   - берётся последний mart  
   - загрузка в PostgreSQL  

---

### State пайплайна

Файл:
data/state.json

Содержит:
- variant
- source_type
- last_successful_run_at
- last_mode
- watermark
- last_raw_path

---

### Watermark

- используется поле: date  
- определяется как максимальная дата из mart  
- обновляется только после успешного завершения pipeline  

Пример:
watermark = 2026-04-14

---

### Business key

Одна строка витрины = один день по одному городу  

Business key:
date + city_id

---

### Идемпотентность

- повторный запуск pipeline не создаёт дубликатов  
- загрузка в PostgreSQL выполняется через replace  
- результат одинаков при повторных запусках на тех же данных  

---

### Режимы работы

Full:
- пересоздаются все слои  
- витрина полностью пересобирается  
- таблица в БД заменяется  

Incremental:
- используется state.json  
- сохраняется watermark  
- pipeline запускается безопасно повторно  
- дубли не накапливаются  

---

### Итог

Собран полноценный ETL pipeline:

API → raw → normalized → mart → PostgreSQL

Свойства:
- единая точка входа  
- повторяемость  
- идемпотентность  
- поддержка incremental  
- хранение состояния (state + watermark)
