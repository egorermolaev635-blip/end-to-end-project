import yaml
import requests
import json
from datetime import datetime
from pathlib import Path
import os


def main():
    config_path = Path(__file__).parent.parent / r"variant_03.yml"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("YAML not found.")
        return
    print(f"Variant: {config['variant_id']} - {config['theme']}")

    url = config["api"]["base_url"]
    entity = config["entity"]

    try:
        import pytz  
        tz = pytz.timezone(entity.get("timezone", "UTC"))
        today = datetime.now(tz)
    except Exception:
        tz = None
        today = datetime.now()

    from datetime import timedelta
    target_date = today.date() - timedelta(days=7)
    start_date = target_date.strftime("%Y-%m-%d")
    end_date = target_date.strftime("%Y-%m-%d")

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

    print(f"URL: {url}")
    print(f"Params: {params}")

    data = None
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                print(f"Data keys: {list(data.keys())}")
            else:
                print(f"Data length: {len(data)}")
        else:
            print("Warning: non-200 status received, falling back to local raw data")
    except Exception as e:
        print(f"Warning: error during API call ({e}); falling back to local raw data")

    folder = "data/raw/variant_03"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{folder}/{timestamp}.json"

    if data is None:
        try:
            existing_files = list(Path(folder).glob("*.json"))
            if existing_files:
                latest_file = max(existing_files, key=lambda f: f.stat().st_mtime)
                with open(latest_file, "r", encoding="utf-8") as f_src, open(
                    filename, "w", encoding="utf-8"
                ) as f_dst:
                    f_dst.write(f_src.read())
                file_size = Path(filename).stat().st_size
                print(f"Used fallback raw file: {latest_file}")
                print(f"raw saved: {filename} ({file_size} bytes)")
            else:
                with open(filename, "w", encoding="utf-8") as f_dst:
                    json.dump({}, f_dst)
                print("No existing raw files found; wrote empty JSON")
        except Exception as e:
            print(f"Error during fallback copy: {e}")
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        file_size = Path(filename).stat().st_size
        print(f"raw saved: {filename} ({file_size} bytes)")
    print(f"config: {config_path.name}")

if __name__ == "__main__":
    main()
