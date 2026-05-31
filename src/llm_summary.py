import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MART_DIR = PROJECT_ROOT / "data" / "mart" / "variant_03"
DQ_REPORT_PATH = PROJECT_ROOT / "docs" / "dq_report.json"
LLM_DIR = PROJECT_ROOT / "docs" / "llm"
SUMMARY_PATH = LLM_DIR / "summary.md"
CONTEXT_PATH = LLM_DIR / "context.md"
PROMPT_PATH = LLM_DIR / "prompt.md"
LOG_PATH = PROJECT_ROOT / "docs" / "LLM_Usage_Log.md"


def find_mart(date: Optional[str]) -> Path:
    if date:
        path = MART_DIR / f"mart_daily_{date}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing mart file: {path}")
        return path

    files = list(MART_DIR.glob("mart_daily_*.csv"))
    if not files:
        raise FileNotFoundError(f"No mart files found in {MART_DIR}")
    return max(files, key=lambda path: path.stat().st_mtime)


def fmt_num(value: float) -> str:
    return f"{value:.2f}"


def load_dq_status() -> tuple[str, dict]:
    if not DQ_REPORT_PATH.exists():
        return "UNKNOWN", {}

    with open(DQ_REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)

    statuses = [check.get("status", "UNKNOWN") for check in report.get("checks", [])]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "WARNING" in statuses or "WARN" in statuses:
        overall = "WARN"
    elif statuses:
        overall = "PASS"
    else:
        overall = "UNKNOWN"
    return overall, report


def compute_metrics(df: pd.DataFrame, mart_path: Path) -> dict:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
    df = df.sort_values("date")

    top_range = df.loc[df["temperature_range"].idxmax()]
    last = df.iloc[-1]
    previous = df.iloc[-2] if len(df) >= 2 else None

    metrics = {
        "mart_file": str(mart_path.relative_to(PROJECT_ROOT)),
        "rows": int(len(df)),
        "period_start": str(df["date"].min()),
        "period_end": str(df["date"].max()),
        "city_count": int(df["city_id"].nunique()),
        "cities": ", ".join(sorted(df["city_name"].dropna().astype(str).unique())),
        "temperature_mean_min": float(df["temperature_mean"].min()),
        "temperature_mean_max": float(df["temperature_mean"].max()),
        "temperature_mean_avg": float(df["temperature_mean"].mean()),
        "temperature_min_abs": float(df["temperature_min"].min()),
        "temperature_max_abs": float(df["temperature_max"].max()),
        "temperature_range_avg": float(df["temperature_range"].mean()),
        "top_range_date": str(top_range["date"]),
        "top_range_value": float(top_range["temperature_range"]),
        "last_date": str(last["date"]),
        "last_temperature_mean": float(last["temperature_mean"]),
    }

    if previous is not None:
        metrics["previous_date"] = str(previous["date"])
        metrics["previous_temperature_mean"] = float(previous["temperature_mean"])
        metrics["last_vs_previous_delta"] = (
            metrics["last_temperature_mean"] - metrics["previous_temperature_mean"]
        )
    else:
        metrics["previous_date"] = "not_available"
        metrics["previous_temperature_mean"] = None
        metrics["last_vs_previous_delta"] = None

    return metrics


def build_context(metrics: dict, dq_status: str) -> str:
    delta = metrics["last_vs_previous_delta"]
    delta_text = "not_available" if delta is None else fmt_num(delta)

    return "\n".join(
        [
            "Dataset identity: Open-Meteo archive, variant_03, city=Новосибирск.",
            "Schema hints: one mart row = one day for one city; temperature fields are in Celsius.",
            f"Mart file: {metrics['mart_file']}",
            f"Period: {metrics['period_start']} to {metrics['period_end']}",
            f"Rows: {metrics['rows']}",
            f"Cities count: {metrics['city_count']}; cities: {metrics['cities']}",
            "Computed metrics:",
            f"- temperature_mean_min={fmt_num(metrics['temperature_mean_min'])}",
            f"- temperature_mean_max={fmt_num(metrics['temperature_mean_max'])}",
            f"- temperature_mean_avg={fmt_num(metrics['temperature_mean_avg'])}",
            f"- temperature_min_abs={fmt_num(metrics['temperature_min_abs'])}",
            f"- temperature_max_abs={fmt_num(metrics['temperature_max_abs'])}",
            f"- temperature_range_avg={fmt_num(metrics['temperature_range_avg'])}",
            f"- top_temperature_range_date={metrics['top_range_date']}",
            f"- top_temperature_range_value={fmt_num(metrics['top_range_value'])}",
            f"- last_date={metrics['last_date']}",
            f"- last_temperature_mean={fmt_num(metrics['last_temperature_mean'])}",
            f"- previous_date={metrics['previous_date']}",
            f"- last_vs_previous_delta={delta_text}",
            f"Quality status: dq={dq_status}",
            "Constraints: use only provided metrics; do not invent numbers; if data is insufficient, say so.",
        ]
    )


def build_prompt(context: str) -> str:
    return f"""Ты аналитик данных. Ниже дан только агрегированный контекст.

Задача:
1. Напиши краткую LLM-сводку на русском языке.
2. Интерпретируй только уже рассчитанные метрики.
3. Не добавляй новые числа и не пересчитывай показатели.
4. Если данных мало для вывода, прямо напиши, что данных недостаточно.
5. Дай 2-3 практических следующих шага для проверки.

Контекст:
{context}
"""


def call_openai(prompt: str) -> tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return local_interpretation(), "local_safe_template"

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
    response = requests.post(
        base_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You write concise analytical summaries and never invent numbers.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip(), model


def local_interpretation() -> str:
    return "\n".join(
        [
            "Температурная витрина выглядит пригодной для короткого аналитического вывода: DQ-статус нужно читать вместе с отчетом качества.",
            "По такому объему данных нельзя делать устойчивые выводы о сезонности или долгом тренде, поэтому сводка подходит только для проверки пайплайна и демонстрации подхода.",
            "Следующие шаги: расширить период наблюдений, сравнить динамику с соседними датами и проверить, совпадают ли BI-графики с mart-витриной.",
        ]
    )


def extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"(?<![\w])-?\d+(?:[.,]\d+)?", text))


def verify_model_text(model_text: str) -> tuple[str, list[str]]:
    numbers = sorted(extract_numbers(model_text))
    if numbers:
        return "WARN", numbers
    return "PASS", []


def write_summary(metrics: dict, context: str, model_text: str, provider: str, verification: str) -> None:
    delta = metrics["last_vs_previous_delta"]
    delta_text = "недостаточно данных" if delta is None else fmt_num(delta)

    summary = f"""# LLM Summary

## Проверяемые цифры

- Источник витрины: `{metrics['mart_file']}`
- Период: {metrics['period_start']} — {metrics['period_end']}
- Строк в mart: {metrics['rows']}
- Городов: {metrics['city_count']} ({metrics['cities']})
- Средняя дневная температура: min={fmt_num(metrics['temperature_mean_min'])}, max={fmt_num(metrics['temperature_mean_max'])}, mean={fmt_num(metrics['temperature_mean_avg'])}
- Абсолютный минимум температуры: {fmt_num(metrics['temperature_min_abs'])}
- Абсолютный максимум температуры: {fmt_num(metrics['temperature_max_abs'])}
- Средний дневной диапазон температуры: {fmt_num(metrics['temperature_range_avg'])}
- Максимальный дневной диапазон: {fmt_num(metrics['top_range_value'])} на дату {metrics['top_range_date']}
- Последняя дата в витрине: {metrics['last_date']}, средняя температура={fmt_num(metrics['last_temperature_mean'])}
- Изменение к предыдущей дате: {delta_text}

## LLM-интерпретация

{model_text}

## Anti-hallucination check

- Числовой блок выше сформирован кодом из mart/DQ, а не посчитан LLM.
- LLM получил только агрегированный контекст: `docs/llm/context.md`.
- Проверка интерпретационного блока: {verification}.
- Provider/model: {provider}.
"""

    LLM_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(summary, encoding="utf-8")
    CONTEXT_PATH.write_text(context + "\n", encoding="utf-8")


def append_log(context: str, prompt: str, model_text: str, provider: str, verification: str, unexpected_numbers: list[str]) -> None:
    now = datetime.now().strftime("%Y-%m-%d")
    numbers_text = ", ".join(unexpected_numbers) if unexpected_numbers else "нет"
    log_entry = f"""

## {now} - Week 14 LLM Summary

- Цель запроса: подготовить краткую аналитическую сводку по mart-витрине без расчета чисел внутри LLM.
- Инструмент: {provider}.
- Контекст: переданы только агрегаты, период, статус DQ и ограничения. Полный контекст сохранен в `docs/llm/context.md`.
- Промпт: попросили интерпретировать только предоставленные метрики, не придумывать числа и явно писать о недостатке данных.
- Краткий ответ LLM: {model_text[:500]}
- Проверка: числовой блок summary вставлен кодом из mart; новые числа в LLM-интерпретации: {numbers_text}.
- Итог: {verification}.
"""
    LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8") + log_entry, encoding="utf-8")
    PROMPT_PATH.write_text(prompt + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a checked LLM summary from mart aggregates")
    parser.add_argument("--date", help="Дата mart-файла в формате YYYY-MM-DD")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mart_path = find_mart(args.date)
    df = pd.read_csv(mart_path)
    dq_status, _ = load_dq_status()
    metrics = compute_metrics(df, mart_path)
    context = build_context(metrics, dq_status)
    prompt = build_prompt(context)
    model_text, provider = call_openai(prompt)
    verification, unexpected_numbers = verify_model_text(model_text)

    write_summary(metrics, context, model_text, provider, verification)
    append_log(context, prompt, model_text, provider, verification, unexpected_numbers)

    if verification == "WARN":
        print(f"LLM summary saved with WARN: unexpected numbers={unexpected_numbers}")
    else:
        print(f"LLM summary saved: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
