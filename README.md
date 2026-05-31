# end-to-end-project

Учебный end-to-end проект по обработке погодных данных: получение данных из API, нормализация, сборка витрины, проверка качества, загрузка в PostgreSQL, визуализация, Airflow-оркестрация и краткая LLM-сводка.

## Что делает проект

Проект работает с архивными погодными данными Open-Meteo по городу Новосибирск.

Основная цепочка:

```text
Extract -> Transform -> Mart -> DQ -> Load -> LLM Summary
```

Слои данных:

```text
data/raw/variant_03/          raw JSON из API
data/normalized/variant_03/   очищенные CSV
data/mart/variant_03/         дневная витрина
docs/dq_report.json           отчет качества данных
docs/llm/summary.md           краткая аналитическая сводка
```

## Требования

- Windows 10/11
- Anaconda или Miniconda
- Docker Desktop, если нужен PostgreSQL, Metabase и Airflow
- Python 3.11

## Быстрый запуск на Windows

### Вариант 1. Через Git

```bash
git clone https://github.com/egorermolaev635-blip/end-to-end-project.git
cd end-to-end-project
scripts\setup_env.bat
```

### Вариант 2. Через ZIP

1. Скачайте ZIP с GitHub.
2. Распакуйте проект в любую папку.
3. Откройте папку проекта.
4. Запустите:

```bash
scripts\setup_env.bat
```

Скрипт создает conda-окружение:

```text
ds_project
```

## Проверка окружения

```bash
conda run -n ds_project python broken_env.py
```

Ожидаемый результат:

```text
python: C:\...\envs\ds_project\python.exe
pandas: ...
```

## Основной запуск pipeline

Локальный запуск без загрузки в PostgreSQL:

```bash
conda run -n ds_project python src/pipeline.py --mode full --date 2026-03-08 --skip-load
```

Запуск с загрузкой в PostgreSQL:

```bash
conda run -n ds_project python src/pipeline.py --mode full --date 2026-03-08
```

Параметры:

- `--mode full` — полный запуск;
- `--mode incremental` — инкрементальный режим;
- `--date YYYY-MM-DD` — дата периода;
- `--skip-load` — пропустить загрузку в PostgreSQL.

## Отдельные шаги

### Extract

Получает данные из Open-Meteo Archive API и сохраняет raw JSON.

```bash
conda run -n ds_project python src/extract.py --date 2026-03-08
```

Результат:

```text
data/raw/variant_03/raw_2026-03-08.json
```

### Transform

Читает raw JSON, очищает данные и создает normalized CSV. После этого запускается сборка mart.

```bash
conda run -n ds_project python src/transform.py --date 2026-03-08
```

Результаты:

```text
data/normalized/variant_03/normalized_2026-03-08.csv
data/mart/variant_03/mart_daily_2026-03-08.csv
```

### Mart

Собирает дневную витрину по температуре.

```bash
conda run -n ds_project python src/showcase_mart.py --date 2026-03-08
```

Гранулярность витрины:

```text
1 строка = 1 день по 1 городу
```

Основные поля:

- `date`
- `city_id`
- `city_name`
- `country_code`
- `temperature_mean`
- `temperature_min`
- `temperature_max`
- `temperature_range`

### DQ

Проверяет качество mart-слоя.

```bash
conda run -n ds_project python src/dq.py --date 2026-03-08
```

Проверки:

- таблица не пустая;
- критичные поля не содержат NULL;
- ключ `date + city_id` уникален;
- температуры находятся в реалистичном диапазоне;
- `temperature_min <= temperature_max`;
- `country_code` входит в допустимый список.

Результат:

```text
docs/dq_report.json
```

### Load

Загружает mart-витрину в PostgreSQL.

```bash
conda run -n ds_project python src/load.py --date 2026-03-08
```

Таблица:

```text
mart_weather
```

Загрузка идемпотентная: перед вставкой удаляются строки за выбранную дату, затем данные вставляются заново.

### SQL-проверки

```bash
conda run -n ds_project python src/check_sql.py
```

Скрипт проверяет:

- количество строк;
- минимальную и максимальную дату;
- дубли по `date + city_id`.

## PostgreSQL и Metabase

Запуск сервисов:

```bash
docker compose up -d
```

После запуска доступны:

```text
PostgreSQL: localhost:5432
Metabase:   http://localhost:3000
```

Подключение PostgreSQL:

```text
database: analytics_db
user: analytics
password: analytics_pass
host: localhost
port: 5432
```

Для подключения Metabase к PostgreSQL внутри Docker Compose используйте:

```text
Host: postgres
Port: 5432
Database name: analytics_db
Username: analytics
Password: analytics_pass
```

## Airflow

Airflow запускает ETL-процесс по расписанию.

Запуск:

```bash
docker compose -f docker-compose.yml -f docker-compose.airflow.yml up -d
```

Airflow UI:

```text
http://localhost:8080
```

Логин и пароль:

```text
airflow / airflow
```

DAG:

```text
etl_variant_03
```

Цепочка задач:

```text
extract -> transform -> dq -> load
```

DQ стоит перед загрузкой в базу. Если проверки качества падают, данные в PostgreSQL не загружаются.

## Визуализация

Ноутбук:

```text
notebooks/week7_viz.ipynb
```

Построенные графики:

```text
notebooks/week7_timeseries.png
notebooks/week7_distribution.png
notebooks/week7_ranking.png
```

## ML-блок

Ноутбук:

```text
notebooks/week13_ml.ipynb
```

В проекте используется простой поиск аномалий по температурному ряду через IQR-метод. Это выбранный учебный сценарий, потому что в данных нет готовой целевой переменной для supervised-модели.

Артефакты:

```text
docs/ml/week13_summary.md
docs/ml/metrics.png
docs/ml/anomalies_top.csv
```

## LLM Summary

Скрипт:

```text
src/llm_summary.py
```

Запуск:

```bash
conda run -n ds_project python src/llm_summary.py --date 2026-03-08
```

Результаты:

```text
docs/llm/context.md
docs/llm/prompt.md
docs/llm/summary.md
docs/LLM_Usage_Log.md
```

LLM не считает метрики. Все числа считаются кодом из mart-витрины, а LLM получает только готовый агрегированный контекст и помогает сформулировать краткую интерпретацию.

Если переменная `OPENAI_API_KEY` не задана, используется локальный безопасный шаблон.

## Основные файлы проекта

```text
src/extract.py          получение raw-данных
src/transform.py        нормализация данных
src/showcase_mart.py    сборка mart-витрины
src/dq.py               проверки качества данных
src/load.py             загрузка в PostgreSQL
src/check_sql.py        SQL-проверки
src/pipeline.py         единая точка запуска pipeline
src/llm_summary.py      LLM-сводка
airflow/dags/etl_variant_03.py
docker-compose.yml
docker-compose.airflow.yml
```

## Как проверить проект перед сдачей

1. Проверить окружение:

```bash
conda run -n ds_project python broken_env.py
```

2. Запустить тесты:

```bash
conda run -n ds_project python -m pytest tests
```

3. Запустить pipeline без базы:

```bash
conda run -n ds_project python src/pipeline.py --mode full --date 2026-03-08 --skip-load
```

4. Если нужен PostgreSQL, поднять Docker:

```bash
docker compose up -d
```

5. Запустить pipeline с загрузкой:

```bash
conda run -n ds_project python src/pipeline.py --mode full --date 2026-03-08
```

6. Проверить SQL:

```bash
conda run -n ds_project python src/check_sql.py
```

## Итог

Проект показывает полный путь данных:

```text
API -> raw -> normalized -> mart -> DQ -> PostgreSQL -> BI / LLM summary
```

Главные свойства проекта:

- воспроизводимый запуск;
- разделение на слои данных;
- проверки качества;
- идемпотентная загрузка;
- Docker-инфраструктура;
- Airflow-оркестрация;
- понятные артефакты для проверки.
