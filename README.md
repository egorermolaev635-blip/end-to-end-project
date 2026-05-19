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

Params: {'latitude': 55.0084, 'longitude': 82.9357, 'timezone': 'Asia/Novosibirsk', ...}

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

## Week 7 — Data Visualization (matplotlib + storytelling)

### Что сделано

- построены визуализации на основе mart-данных  
- используется самый свежий mart CSV из `data/mart/variant_03/`  
- реализован анализ в Jupyter Notebook  
- применены базовые типы графиков:
  - временной ряд (line plot)  
  - распределение (histogram)  
  - ranking (bar chart)  
- обеспечена корректная работа с датой (`datetime + сортировка`)  
- добавлены текстовые выводы по графикам  

---

### Ноутбук

Файл:
notebooks/week7_viz.ipynb

---

### Загрузка данных

- автоматически выбирается последний файл из:
data/mart/variant_03/*.csv

---

### Построенные графики

1. Временной ряд  
   - динамика средней температуры по датам  

2. Распределение  
   - распределение значений температуры  

3. Ranking  
   - агрегирование по диапазонам temperature_range  

---

### Оформление

- заголовки графиков  
- подписи осей  
- единицы измерения (°C)  
- корректная временная ось  

---

### Выводы

- данные проанализированы через визуализацию  
- выявлены колебания температуры во времени  
- оценено распределение значений  
- показана вариативность через агрегирование  

---

### Результат

- построены 3 графика  
- выполнен базовый визуальный анализ  
- ноутбук воспроизводим  
- данные корректно интерпретированы  

---
## Week 8 — Data Quality (DQ + тесты)

### Что сделано

- реализованы проверки качества данных для слоя mart  
- написан отдельный скрипт `dq.py`  
- реализован автоматический отчёт в JSON  
- добавлены unit-тесты через pytest  
- проверена корректность всех функций  

---

### Проверки DQ

Реализованы следующие проверки:

1. table_non_empty  
   - проверка, что таблица не пустая  

2. not_null_critical_fields  
   - проверка NULL в полях:  
     date, city_id, city_name, country_code  

3. unique_business_key  
   - проверка уникальности ключа:  
     date + city_id  

4. temperature_range  
   - проверка диапазона температур:  
     от -90 до +60  

5. temperature_min_max_logic  
   - проверка условия:  
     temperature_min ≤ temperature_max  

6. country_code_enum  
   - проверка допустимых значений country_code  

---

### Запуск DQ

python src/dq.py

---

### Что происходит

- берётся последний mart CSV  
- выполняются все проверки  
- формируется отчёт  

---

### Результат

Отчёт сохраняется в:

data/dq_report.json  

Содержит:
- источник данных  
- количество строк  
- список проверок  
- статус (PASS / FAIL / WARNING)  

---

### Тесты

Файл:
tests/test_dq.py  

Проверяется:
- корректность работы всех функций  
- обработка ошибок (NULL, дубли, диапазоны)  

---

### Запуск тестов

python3 -m pytest tests  

---

### Итог

- реализован контроль качества данных  
- проверки применяются к реальным данным  
- логика проверок покрыта тестами  
- результаты сохраняются в отчёт  

DQ слой добавлен в pipeline и завершает цепочку обработки данных.

### Итог

Добавлен этап анализа данных через визуализацию:

mart → matplotlib → выводы

## Week 9 — Data Governance (Data Contract + Data Dictionary)

### Что сделано

- оформлен полный Data Contract (`docs/Data_Contract.md`)
- добавлены:
  - версия контракта (version)
  - changelog изменений
  - единицы измерения (units)
  - часовой пояс (timezone)
  - правила именования (naming conventions)
  - ограничения (constraints)
  - гранулярность данных
- создан словарь данных (`docs/data_dictionary.md`)
- согласована логика данных между кодом и документацией

---

### Data Contract

Файл:
docs/Data_Contract.md

Содержит:

- описание источника данных (Open-Meteo API)
- схемы слоёв:
  - normalized
  - mart
- типы данных и nullable
- единицы измерения (°C, degrees)
- часовой пояс: `Asia/Novosibirsk`
- гранулярность:
  - normalized → 1 строка = 1 час
  - mart → 1 строка = 1 день × 1 город
- ключи и ограничения:
  - `date + city_id`
- правила именования колонок
- changelog версий

---

### Data Dictionary

Файл:
docs/data_dictionary.md

Содержит:

- человеко-ориентированное описание колонок mart
- бизнес-смысл каждой метрики
- единицы измерения
- пояснения к интерпретации данных

---

### Основная идея

Данные не просто существуют, а:

- имеют зафиксированный смысл  
- имеют единые единицы измерения  
- имеют согласованную структуру  
- не ломают downstream при изменениях  

---

### Итог

Pipeline приведён к уровню Data Governance:

API → raw → normalized → mart → PostgreSQL → DQ → visualization → **contract + dictionary**

Обеспечено:

- понимание данных  
- воспроизводимость  
- согласованность  
- прозрачность изменений  

## Неделя 10 — Docker: PostgreSQL, Metabase и BI-дашборд

**Статус:** 🟢 Готово

### Цель недели

На неделе 10 был собран воспроизводимый локальный стенд для работы с витриной данных.

В рамках задания были выполнены следующие действия:

- PostgreSQL поднимается через `docker compose`;
- данные PostgreSQL сохраняются в отдельном volume;
- Metabase поднимается как BI-инструмент;
- Metabase подключается к PostgreSQL внутри Docker Compose-сети;
- дашборд строится по таблице `mart_weather` из PostgreSQL, а не по CSV-файлу.

---

### Состав Docker Compose-стенда

В проект добавлен файл:

```text
docker-compose.yml
```

В нём описаны два сервиса:

| Сервис | Назначение |
|---|---|
| `postgres` | база данных PostgreSQL для хранения витрины |
| `metabase` | BI-инструмент для построения дашборда |

Также используются два volume:

| Volume | Назначение |
|---|---|
| `pgdata` | хранит данные PostgreSQL |
| `metabase_data` | хранит настройки Metabase и созданные дашборды |

---

### Запуск сервисов

Для запуска PostgreSQL и Metabase используется команда:

```bash
docker compose up -d
```

Проверка запущенных контейнеров:

```bash
docker compose ps
```

После запуска сервисов доступны:

```text
PostgreSQL: localhost:5432
Metabase:   http://localhost:3000
```

---

### Загрузка витрины в PostgreSQL

Витрина загружается в PostgreSQL через существующий скрипт:

```bash
python src/load.py
```

Скрипт автоматически берёт последний CSV-файл из папки:

```text
data/mart/variant_03/
```

и загружает его в таблицу:

```text
mart_weather
```

Используемое подключение:

```text
database: analytics_db
user: analytics
password: analytics_pass
host: localhost
port: 5432
```

---

### Проверка таблицы в PostgreSQL

Для ручной проверки можно зайти в PostgreSQL:

```bash
docker compose exec postgres psql -U analytics -d analytics_db
```

Проверочные SQL-команды:

```sql
\dt
SELECT COUNT(*) FROM mart_weather;
SELECT * FROM mart_weather LIMIT 5;
```

---

### Подключение Metabase к PostgreSQL

В Metabase используется подключение:

```text
Database type: PostgreSQL
Host: postgres
Port: 5432
Database name: analytics_db
Username: analytics
Password: analytics_pass
```

Важно: в Metabase используется `Host = postgres`, потому что Metabase работает внутри Docker Compose-сети и обращается к PostgreSQL по имени сервиса.

При этом `src/load.py` подключается к `localhost:5432`, потому что запускается с локальной машины, а порт PostgreSQL проброшен наружу.

---

### BI-дашборд

В Metabase создан дашборд:

```text
Weather Analytics Dashboard
```

Дашборд построен по таблице:

```text
mart_weather
```

В него входят три визуализации:

| № | Название | Тип | Поля |
|---|---|---|---|
| 1 | Средняя температура по дням | line chart | `date`, `temperature_mean` |
| 2 | Максимальная температура по дням | bar chart | `date`, `temperature_max` |
| 3 | Сводка температурной витрины | table | `date`, `city_name`, `temperature_mean`, `temperature_min`, `temperature_max`, `temperature_range` |

Так как текущая mart-витрина содержит небольшой набор данных, третья визуализация сделана в виде таблицы. Это позволяет явно показать итоговую витрину, из которой строятся графики.

---

### BI-артефакты

Скриншоты BI-дашборда сохранены в папке:

```text
docs/bi/
```

Файлы:

```text
docs/bi/dashboard_overview.png
docs/bi/chart_timeseries.png
docs/bi/chart_summary.png
```

---

### Разница между Docker-командами

`docker compose stop` останавливает контейнеры, но не удаляет их.

`docker compose down` удаляет контейнеры, но сохраняет volumes.

`docker compose down -v` удаляет контейнеры и volumes. В этом случае данные PostgreSQL и настройки Metabase будут удалены.

---

## Неделя 11 — Airflow: оркестрация ETL-процесса

**Статус:** 🟢 Готово

### Цель недели

На неделе 11 был добавлен Apache Airflow для автоматического запуска ETL-процесса.

Ранее этапы проекта запускались отдельными командами:

```text
extract → transform → load → dq
```

Теперь эти этапы объединены в один Airflow DAG.  
Это позволяет запускать весь pipeline через веб-интерфейс, видеть историю запусков, отслеживать статусы задач и проверять логи выполнения.

---

### Что сделано

- добавлен запуск Airflow через Docker Compose;
- создан DAG `etl_variant_03`;
- настроена цепочка задач `extract → transform → load → dq`;
- добавлено расписание запуска;
- настроены зависимости между задачами;
- обновлены ETL-скрипты для корректной работы внутри Airflow;
- добавлены логи для проверки выполнения каждого этапа;
- сделаны скриншоты успешного запуска DAG.

---

### Основной DAG

Файл DAG находится по пути:

```text
airflow/dags/etl_variant_03.py
```

Название DAG в интерфейсе Airflow:

```text
etl_variant_03
```

Цепочка задач:

```text
extract → transform → load → dq
```

---

### Задачи DAG

| Task | Назначение |
|---|---|
| `extract` | получение raw JSON |
| `transform` | нормализация данных и построение mart |
| `load` | загрузка mart в PostgreSQL |
| `dq` | проверка качества данных |

---

### Расписание

Для учебной проверки используется расписание:

```text
*/5 * * * *
```

DAG может запускаться автоматически каждые 5 минут.

Также его можно запустить вручную через кнопку **Trigger DAG** в интерфейсе Airflow.

---

### Настройки DAG

В DAG используются следующие настройки:

```text
start_date = 2026-03-01
catchup = False
schedule = */5 * * * *
```

Параметр `catchup=False` нужен, чтобы Airflow не запускал все пропущенные интервалы с момента `start_date`.

---

### Запуск Airflow

Сначала запускается основной Docker Compose с PostgreSQL:

```bash
docker compose up -d
```

После этого запускается Airflow:

```bash
docker compose -f docker-compose.yml -f docker-compose.airflow.yml up -d
```

Проверка контейнеров:

```bash
docker compose ps
```

---

### Airflow UI

После запуска Airflow доступен в браузере:

```text
http://localhost:8080
```

Логин и пароль:

```text
airflow / airflow
```

В интерфейсе Airflow нужно:

1. открыть список DAGs;
2. включить DAG `etl_variant_03`;
3. запустить DAG вручную через Trigger DAG;
4. дождаться статуса `success`;
5. проверить Graph View и логи задач.

---

### Подключение к PostgreSQL

При локальном запуске `src/load.py` использует подключение:

```text
localhost:5432
```

Но внутри контейнера Airflow `localhost` указывает на сам контейнер Airflow.

Поэтому для DAG используется подключение к PostgreSQL по имени Docker Compose-сервиса:

```text
postgres:5432
```

Строка подключения внутри Airflow:

```text
postgresql+psycopg2://analytics:analytics_pass@postgres:5432/analytics_db
```

---

### Изменения в ETL-скриптах

Для корректной работы Airflow были обновлены основные скрипты проекта.

В `src/extract.py`:

- исправлен запрос к Open-Meteo Archive API;
- вместо `past_days` используются `start_date` и `end_date`;
- добавлен fallback на последний локальный raw-файл;
- добавлен вывод логов для Airflow.

В `src/transform.py`:

- добавлен отдельный transform-этап для Airflow;
- выполняется notebook `notebooks/week3_eda.ipynb`;
- после normalized-слоя запускается построение mart;
- в лог выводится количество строк.

В `src/load.py`:

- добавлена поддержка переменной окружения `DB_URL`;
- загрузка выполняется в таблицу `mart_weather`;
- добавлен вывод количества загруженных строк;
- сохранена идемпотентность через `if_exists="replace"`.

В `src/dq.py`:

- выполняются проверки качества mart-слоя;
- в лог выводится итоговый статус проверок;
- при наличии FAIL задача завершается с ошибкой.

---

### Ожидаемые строки в логах

В логах Airflow должны быть видны основные этапы выполнения:

```text
config: variant_03.yml
raw saved: data/raw/variant_03/....json
normalized rows: ...
mart rows: ...
loaded rows to postgres: ...
dq checks: PASS=6 WARNING=0 FAIL=0
```

Эти строки подтверждают, что DAG не просто запустился, а реально выполнил весь ETL-процесс.

---

### Скриншоты

Скриншоты для подтверждения выполнения сохранены в папке:

```text
docs/airflow/
```

Файлы:

```text
docs/airflow/successful_run.png
docs/airflow/graph_view.png
docs/airflow/task_log.png
```

---

### Что показывают скриншоты

| Файл | Что показывает |
|---|---|
| `successful_run.png` | успешные DAG Run со статусом `success` |
| `graph_view.png` | цепочку задач `extract → transform → load → dq` |
| `task_log.png` | лог задачи `dq` с итогом проверок |

---

### Результат

DAG `etl_variant_03` успешно выполняет полный ETL-процесс:

```text
raw → normalized → mart → PostgreSQL → DQ
```

Все задачи выполняются последовательно:

```text
extract → transform → load → dq
```

После запуска DAG завершается со статусом `success`.

---

### Итог

Pipeline расширен до оркестрации через Apache Airflow.

Теперь проект можно запускать не только отдельными Python-скриптами, но и через Airflow DAG.

Добавлены:

- автоматический запуск по расписанию;
- ручной запуск через Airflow UI;
- зависимости между задачами;
- история запусков;
- логи выполнения;
- скриншоты успешного запуска.

Airflow-часть проекта работает корректно и подтверждена результатами выполнения DAG.
