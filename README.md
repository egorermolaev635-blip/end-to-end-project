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
