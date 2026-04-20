import json
import logging
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)


class Cbs:
    def __init__(self):
        self.base_url = "https://opendata.cbs.nl/ODataFeed/odata"
        self.all_records = []

    def _build_url(self, table_id, endpoint):
        return f"{self.base_url}/{table_id}/{endpoint}"

    def _get_headers(self):
        return {"Accept": "application/json"}

    def api_extract(self, table_id, endpoint, page_size=1000, skip=0):
        self.all_records = []
        while True:
            params = {"$top": page_size, "$skip": skip}
            response = requests.get(
                self._build_url(table_id, endpoint),
                params=params,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            payload = response.json()

            batch = payload.get("value", [])
            self.all_records.extend(batch)

            if len(batch) < page_size:
                break
            skip += page_size
        return self.all_records


def load_config() -> dict:
    config_path = Path(__file__).parents[1] / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)["cbs"]


def save_json(data: list[dict], endpoint: str) -> Path:
    output_dir = Path(__file__).parents[1] / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{endpoint}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    return output_path


def fetch_cbs_data() -> dict[str, list[dict]]:
    config = load_config()
    table_id = config["table_id"]
    endpoints = config["endpoint"]
    cbs = Cbs()
    results = {}
    for endpoint in endpoints:
        records = cbs.api_extract(table_id=table_id, endpoint=endpoint)
        path = save_json(records, endpoint)
        results[endpoint] = records
        logger.info("[%s] %d records -> %s", endpoint, len(records), path)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Fetching NL Retail data from CBS data ")
    fetch_cbs_data()
    logger.info("Done.")
