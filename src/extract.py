import yaml
import requests
import json
import argparse
from datetime import datetime
from pathlib import Path
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    target_date_str = args.date

    config_path = Path(__file__).parent.parent / "variant_03.yml"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("YAML not found.")
        return

    url = config["api"]["base_url"]
    entity = config["entity"]

    start_date = target_date_str
    end_date = target_date_str

    hourly_vars = config.get("api", {}).get("params", {}).get("hourly")
    if isinstance(hourly_vars, list):
        hourly_param = ",".join(hourly_vars)
    else:
        hourly_param = str(hourly_vars) if hourly_vars else "temperature_2m"

    params = {
        "latitude": entity["latitude"],
        "longitude": entity["longitude"],
        "timezone": entity["timezone"],
        "start_date": start_date,
        "end_date": end_date,
        "hourly": hourly_param,
    }

    data = None
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
    except Exception:
        pass

    folder = "data/raw/variant_03"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/raw_{target_date_str}.json"

    if data is None:
        try:
            existing_files = list(Path(folder).glob("raw_*.json"))
            if existing_files:
                latest_file = max(existing_files, key=lambda f: f.stat().st_mtime)
                with open(latest_file, "r", encoding="utf-8") as f_src, open(
                    filename, "w", encoding="utf-8"
                ) as f_dst:
                    f_dst.write(f_src.read())
            else:
                with open(filename, "w", encoding="utf-8") as f_dst:
                    json.dump({}, f_dst)
        except Exception:
            pass
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
