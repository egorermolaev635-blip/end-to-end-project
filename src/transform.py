import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_ROOT / "notebooks" / "week3_eda.ipynb"
NORMALIZED_DIR = PROJECT_ROOT / "data" / "normalized" / "variant_03"
CONFIG_PATH = PROJECT_ROOT / "variant_03.yml"


def latest_csv(folder: Path) -> Path:
    files = list(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"Нет csv-файлов в {folder}")
    return max(files, key=lambda f: f.stat().st_mtime)


def main() -> None:
    print(f"config: {CONFIG_PATH.name}")

    if not NOTEBOOK.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK}")

    print(f"transform: executing {NOTEBOOK.relative_to(PROJECT_ROOT)}")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=600",
            str(NOTEBOOK),
        ],
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError("Ошибка при выполнении ноутбука transform")

    normalized_path = latest_csv(NORMALIZED_DIR)
    df = pd.read_csv(normalized_path)
    print(f"normalized rows: {len(df)}")
    print(f"normalized saved: {normalized_path}")

    mart_script = PROJECT_ROOT / "src" / "showcase_mart.py"
    print(f"transform: running {mart_script.relative_to(PROJECT_ROOT)}")
    mart_result = subprocess.run([sys.executable, str(mart_script)], cwd=PROJECT_ROOT)
    if mart_result.returncode != 0:
        raise RuntimeError("Ошибка при построении mart")


if __name__ == "__main__":
    main()
