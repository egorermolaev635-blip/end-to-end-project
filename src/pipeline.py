import json
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = PROJECT_ROOT / "data" / "state" / "state.json"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "variant_03"
MART_DIR = PROJECT_ROOT / "data" / "mart" / "variant_03"
DQ_REPORT_PATH = PROJECT_ROOT / "docs" / "dq_report.json"


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {
            "variant": "variant_03",
            "source_type": "weather_archive_api",
            "last_successful_run_at": None,
            "last_mode": None,
            "watermark": None,
            "last_raw_path": None
        }

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_latest_file(folder: Path, pattern: str) -> Path:
    files = list(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Нет файлов {pattern} в {folder}")
    return max(files, key=lambda f: f.stat().st_mtime)


def run_step(script_name: str, *args: str) -> None:
    script_path = Path(__file__).parent / script_name
    print(f"[pipeline] Запускаю шаг: {script_name} {' '.join(args)}")

    result = subprocess.run([sys.executable, str(script_path), *args], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Ошибка на шаге: {script_name}")


def run_notebook(notebook_path: str) -> None:
    print(f"[pipeline] Запускаю ноутбук: {notebook_path}")

    result = subprocess.run([
        sys.executable,
        "-m",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        notebook_path
    ])
    if result.returncode != 0:
        raise RuntimeError(f"Ошибка при выполнении ноутбука: {notebook_path}")


def extract_watermark_from_mart(target_date: str) -> str:
    mart_path = MART_DIR / f"mart_daily_{target_date}.csv"
    if not mart_path.exists():
        mart_path = get_latest_file(MART_DIR, "*.csv")
    df = pd.read_csv(mart_path)

    if "date" not in df.columns:
        raise ValueError("В mart нет колонки date, не могу вычислить watermark")

    watermark = str(df["date"].max())
    print(f"[pipeline] watermark = {watermark}")
    return watermark


def parse_args():
    parser = argparse.ArgumentParser(description="Run ETL pipeline")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--date", required=True, help="Дата периода в формате YYYY-MM-DD")
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Пропустить загрузку в PostgreSQL, если нужна только локальная проверка CSV/DQ",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    mode = args.mode
    target_date = args.date

    print(f"[pipeline] старт | mode={mode} | date={target_date}")

    state = load_state()
    print("[pipeline] Текущее состояние:")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    run_step("extract.py", "--date", target_date)
    run_step("transform.py", "--date", target_date)
    run_step("dq.py", "--date", target_date)
    if args.skip_load:
        print("[pipeline] load пропущен по флагу --skip-load")
    else:
        run_step("load.py", "--date", target_date)

    last_raw_path = str(RAW_DIR / f"raw_{target_date}.json")
    watermark = extract_watermark_from_mart(target_date)

    state["last_successful_run_at"] = datetime.now().isoformat()
    state["last_mode"] = mode
    state["last_date"] = target_date
    state["watermark"] = watermark
    state["last_raw_path"] = last_raw_path
    state["last_mart_path"] = str(MART_DIR / f"mart_daily_{target_date}.csv")
    state["last_dq_report_path"] = str(DQ_REPORT_PATH)
    state["load_skipped"] = args.skip_load

    save_state(state)

    print("[pipeline] Пайплайн завершился успешно")
    print("[pipeline] Обновлённый state:")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
