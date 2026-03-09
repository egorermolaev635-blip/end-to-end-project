# end-to-end-project
Запуск проекта (Windows)

### Вариант 1. Через Git.
1. git clone https://github.com/egorermolaev635-blip/end-to-end-project.git
2. cd project
3. scripts\setup_env.bat

### Вариант 2: ZIP + двойной клик
1. Скачайте ZIP с GitHub
2. Распакуйте в любую папку
3. Двойной клик на scripts\setup_env.bat

### Проверка (smoke test)
conda run -n data-project python broken_env.py

Ожидаемый результат:
python: C:\...\envs\data-project\python.exe
pandas: 2.1.4

### Week 2: API Extract (variant_03)

### Вариант 1.
conda run -n data-project python src/extract.py
### Вариант 2:
python src/extract.py  (если активирована среда)

Ожидаемый результат:
Variant: 3 - Погода (архив) - Новосибирск
URL: https://archive-api.open-meteo.com/v1/archive
Params: {'latitude': 55.75, 'longitude': 37.62, ...}
Status: 200
Data: 1234
Saved: data/raw/variant_03/2026-03-09_18-39-XX.json

Файлы создаются:
data/raw/variant_03/YYYY-MM-DD_HH-MM-SS.json  <- raw API ответ
docs/Data_Contract.md                         <- документация API

### Требования
- Windows 10/11
- Anaconda/Miniconda (устанавливается автоматически)


