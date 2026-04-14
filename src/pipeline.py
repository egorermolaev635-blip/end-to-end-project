import json
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd


STATE_PATH = Path("data/state/state.json")
RAW_DIR = Path("data/raw/variant_03")
MART_DIR = Path("data/mart/variant_03")


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


def run_step(script_name: str) -> None:
    script_path = Path(__file__).parent / script_name
    print(f"[pipeline] Запускаю шаг: {script_name}")

    result = subprocess.run([sys.executable, str(script_path)])
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


def extract_watermark_from_mart() -> str:
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
    return parser.parse_args()


def main():
    args = parse_args()
    mode = args.mode

    print(f"[pipeline] старт | mode={mode}")

    state = load_state()
    print("[pipeline] Текущее состояние:")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    run_step("extract.py")
    run_notebook("notebooks/week3_eda.ipynb")
    run_step("showcase_mart.py")
    run_step("load.py")

    last_raw_path = str(get_latest_file(RAW_DIR, "*.json"))
    watermark = extract_watermark_from_mart()

    state["last_successful_run_at"] = datetime.now().isoformat()
    state["last_mode"] = mode
    state["watermark"] = watermark
    state["last_raw_path"] = last_raw_path

    save_state(state)

    print("[pipeline] Пайплайн завершился успешно")
    print("[pipeline] Обновлённый state:")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
