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

## Ответ
```json
{
  "hourly": {
    "time": ["2026-03-08T00:00", "2026-03-08T01:00", ...],
    "temperature_2m": [-5.2, -6.1, ...]
  }
}

