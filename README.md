# end-to-end-project
##  Запуск проекта (Windows)

### Вариант 1: Через Git (рекомендуется)
```cmd
git clone https://github.com/ВАШ_НИК/project.git
cd project
scripts\setup_env.bat

### Вариант 2: ZIP + двойной клик
## 1. Скачайте ZIP с GitHub
## 2. Распакуйте в любую папку
## 3. Двойной клик на scripts\setup_env.bat

### Проверка (smoke test)
conda run -n data-project python broken_env.py

## Ождидаемый результат:
python: C:\...\envs\data-project\python.exe
pandas: 2.1.4



