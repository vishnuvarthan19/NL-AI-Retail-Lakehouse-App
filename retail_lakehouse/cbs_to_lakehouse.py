import logging

from retail_lakehouse.database.database import run_duckdb_bronze, run_duckdb_silver, run_duckdb_gold
from retail_lakehouse.ingestion.cbs_api_extract import fetch_cbs_data

logger = logging.getLogger(__name__)


def load_from_cbs_to_lakehouse() -> None:
    logger.info("Fetching CBS data from API")
    fetch_cbs_data()

    logger.info("Loading into DuckDB bronze Layer")
    run_duckdb_bronze()
    logger.info("Done Loading DuckDB bronze Layer")

    logger.info("Loading into DuckDB Silver Layer")
    run_duckdb_silver()
    logger.info("Done Loading DuckDB Silver Layer")

    logger.info("Loading into DuckDB Gold Layer")
    run_duckdb_gold()
    logger.info("Done Loading DuckDB Gold Layer")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_from_cbs_to_lakehouse()
