# Data Contract: Open-Meteo Archive API (variant_03)

## Источник

- **API**: Open-Meteo Historical Weather API  
- **Endpoint**: https://archive-api.open-meteo.com/v1/archive  
- **Метод**: GET  
- **Аутентификация**: Не требуется  

---

## Параметры запроса

| Параметр | Значение | Описание |
|----------|----------|----------|
| latitude | 55.0084 | Новосибирск |
| longitude | 82.9357 | Новосибирск |
| timezone | Asia/Novosibirsk | Часовой пояс Новосибирска |
| hourly | temperature_2m | Температура воздуха на высоте 2 м |

---

## Raw JSON

    {
      "hourly": {
        "time": ["2026-03-08T00:00", "2026-03-08T01:00"],
        "temperature_2m": [-5.2, -6.1]
      }
    }

---

## Ограничения источника

- Архивные данные доступны до 70 лет назад  
- API-ключ не требуется  
- Бесплатный лимит: ~10 000 запросов в день  

---

## Normalized dataset

**Описание:**  
Одна строка = одно почасовое наблюдение температуры по Новосибирску.  

**Источник:**  
Raw JSON из `data/raw/variant_03/`

---

### Схема normalized

| поле | тип | nullable | единица | описание |
|------|-----|----------|---------|----------|
| time | datetime | no | local time | дата и время наблюдения |
| temperature | float | no | °C | температура воздуха на высоте 2 м |
| latitude | float | no | degrees | широта |
| longitude | float | no | degrees | долгота |
| date | date | no | calendar date | дата |
| hour | int | no | hour | час (0–23) |

---

## Mart dataset

**Описание:**  
Одна строка = один день по одному городу (Новосибирск)

**Источник:**  
data/normalized/variant_03/ + справочник городов  

---

### Схема mart

| поле | тип | nullable | единица | описание |
|------|-----|----------|---------|----------|
| date | date | no | calendar date | дата |
| city_id | string | no | identifier | идентификатор |
| city_name | string | no | text | название города |
| country_code | string | no | country code | код страны |
| temperature_mean | float | no | °C | средняя температура |
| temperature_min | float | no | °C | минимум |
| temperature_max | float | no | °C | максимум |
| temperature_range | float | no | °C | диапазон |

---

## Логика расчёта

- temperature_mean = avg(temperature)  
- temperature_min = min(temperature)  
- temperature_max = max(temperature)  
- temperature_range = temperature_max - temperature_min  

---

## Версия контракта

version: 0.1  
last_updated: 2026-04-29  

---

## Время и часовой пояс

- Используется Asia/Novosibirsk  
- Все даты считаются в локальном времени  
- Агрегации выполняются по календарному дню  

---

## Гранулярность

- Normalized: 1 строка = 1 час  
- Mart: 1 строка = 1 день × 1 город  

---

## Единицы измерения

| поле | единица |
|------|---------|
| temperature | °C |
| temperature_mean | °C |
| temperature_min | °C |
| temperature_max | °C |
| temperature_range | °C |
| latitude | degrees |
| longitude | degrees |

---

## Naming rules

- snake_case  
- без кириллицы  
- *_id для идентификаторов  
- date для дат  
- запрещены: value, metric, data1  

---

## Ключ

date + city_id  

---

## Ограничения

- нет NULL  
- нет дублей по ключу  
- temperature_min ≤ temperature_mean ≤ temperature_max  
- temperature_range = max - min  
- temperature_range ≥ 0  

---

## Data Quality assumptions

- температура в диапазоне [-80; +60]  
- значения числовые  
- пропуски искажают агрегаты  

---

## Проверка контракта

- наличие колонок  
- отсутствие NULL  
- уникальность ключа  
- проверка формулы  
- проверка порядка температур  

---

## Changelog

| version | date | change |
|--------|------|--------|
| 0.1 | 2026-04-29 | Добавлен Data Governance (units, TZ, version, rules) |
