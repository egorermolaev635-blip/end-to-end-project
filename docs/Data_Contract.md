# Data Contract: Open-Meteo Archive API (variant_03)

## Источник
- **API**: Open-Meteo Historical Weather API  
- **Endpoint**: `https://archive-api.open-meteo.com/v1/archive`
- **Метод**: GET
- **Аутентификация**: Не требуется

## Параметры запроса
| Параметр | Значение | Описание |
|----------|----------|----------|
| latitude | 55.75 | Москва |
| longitude | 37.62 | Москва |
| past_days | 1 | За вчера |
| hourly | temperature_2m | Температура по часам |

## raw json
```json
{
  "hourly": {
    "time": ["2026-03-08T00:00", "2026-03-08T01:00", ...],
    "temperature_2m": [-5.2, -6.1, ...]
  }
}


Ограничения
Архив: до 70 лет назад

Лимит: 10,000 запросов/день бесплатно
```

## Normalized dataset

**Описание:**
Одна строка = одно почасовое наблюдение температуры.

Источник данных: Open-Meteo API (raw JSON из data/raw/...).

---

### Схема таблицы

| поле        | тип       | nullable | описание |
|------------|----------|----------|----------|
| time       | datetime | no       | дата и время наблюдения |
| temperature| float    | no       | температура воздуха на высоте 2м (°C) |
| latitude   | float    | no       | широта точки наблюдения |
| longitude  | float    | no       | долгота точки наблюдения |
| date       | date     | no       | дата (выделена из time) |
| hour       | int      | no       | час (0–23) |

## Mart dataset

**Описание:**  
Одна строка = один день наблюдения температуры по Новосибирску.

Источник данных: normalized CSV из `data/normalized/variant_03/...`, дополнительно обогащённый справочником города.

---

### Схема таблицы mart

| поле               | тип       | nullable | описание |
|-------------------|-----------|----------|----------|
| date              | date      | no       | дата агрегирования |
| city_id           | string    | no       | идентификатор города |
| city_name         | string    | no       | название города |
| country_code      | string    | no       | код страны |
| temperature_mean  | float     | no       | средняя температура за день |
| temperature_min   | float     | no       | минимальная температура за день |
| temperature_max   | float     | no       | максимальная температура за день |
| temperature_range | float     | no       | суточный диапазон температуры (`max - min`) |

---

### Логика расчёта

- `temperature_mean` = среднее значение `temperature` за день
- `temperature_min` = минимальное значение `temperature` за день
- `temperature_max` = максимальное значение `temperature` за день
- `temperature_range` = `temperature_max - temperature_min`
