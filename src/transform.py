import subprocess
import sys
import argparse
from pathlib import Path
import os
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_ROOT / "notebooks" / "week3_eda.ipynb"
NORMALIZED_DIR = PROJECT_ROOT / "data" / "normalized" / "variant_03"
CONFIG_PATH = PROJECT_ROOT / "variant_03.yml"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    target_date = args.date

    if not NOTEBOOK.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK}")

    env = os.environ.copy()
    env["TARGET_DATE"] = target_date

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
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError("Ошибка при выполнении ноутбука transform")

    normalized_path = NORMALIZED_DIR / f"normalized_{target_date}.csv"
    if not normalized_path.exists():
        raise FileNotFoundError(f"Missing file: {normalized_path}")

    df = pd.read_csv(normalized_path)

    mart_script = PROJECT_ROOT / "src" / "showcase_mart.py"
    mart_result = subprocess.run([sys.executable, str(mart_script), "--date", target_date], cwd=PROJECT_ROOT)
    if mart_result.returncode != 0:
        raise RuntimeError("Ошибка при построении mart")


if __name__ == "__main__":
    main()
