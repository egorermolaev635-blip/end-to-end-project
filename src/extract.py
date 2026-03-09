import yaml
import requests
import json
from datetime import datetime
from pathlib import Path
import os


def main():
    config_path = Path(__file__).parent / r"variant_03.yml"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("YAML not found.")
        return
    print(f"Variant: {config['variant_id']} - {config['theme']}")

    url = config["api"]["base_url"]
    entity = config["entity"]
    params = {
        "latitude": entity["latitude"],
        "longitude": entity["longitude"],
        "timezone": entity["timezone"],
        "past_days": 1,
        "hourly": "temperature_2m"
    }

    print(f"URL: {url}")
    print(f"Params: {params}")

    try:
        respone = requests.get(url, params=params, timeout=10)
        print(f"Status: {respone.status_code}")

        if respone.status_code != 200:
            print("error status")
            return
        data = respone.json()
        print(f"Data: {len(data)}")

    except Exception as e:
        print(f"Error respone: {e}")
        return

    folder = "data/raw/variant_03"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{folder}/{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved: {filename}")

if __name__ == "__main__":
    main()
