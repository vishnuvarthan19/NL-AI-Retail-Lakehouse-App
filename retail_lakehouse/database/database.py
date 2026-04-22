import logging
import duckdb
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parents[1] / "config.yaml"
DATA_DIR = Path(__file__).parents[1] / "data"


class DuckDB:
    def __init__(self):
        self.db_path = DATA_DIR / "duckdb/lakehouse.duckdb"

    def apply_column_comments(self, target_table: str, source_table: str) -> None:
        con = duckdb.connect(str(self.db_path))
        rows = con.execute(
            f"SELECT Key, Description FROM {source_table} WHERE Key != '' AND Description != ''"
        ).fetchall()
        comments = {key: desc for key, desc in rows}
        columns = con.execute(f"DESCRIBE {target_table}").fetchdf()["column_name"].tolist()
        for col in columns:
            if col in comments:
                desc = comments[col].replace("'", "''").replace("\r\n", " ").strip()
                con.execute(f"COMMENT ON COLUMN {target_table}.{col} IS '{desc}'")
                logger.info("Comment set on %s.%s", target_table, col)
        con.close()

    def load_layer(self, table: str, layer: str, query: str) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        sql = query.format(table=table, layer=layer, data_dir=DATA_DIR)
        con = duckdb.connect(str(self.db_path))
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                con.execute(stmt)
        con.close()
        logger.info("[%s_%s] saved -> %s", layer, table, self.db_path)


def _load_tables() -> list[str]:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)["cbs"]["endpoint"]


def _load_query(layer: str) -> str:
    query_path = DATA_DIR / f"duckdb/queries/{layer}.sql"
    return query_path.read_text()


def run_duckdb_bronze() -> None:
    tables = _load_tables()
    query = _load_query("bronze")
    db = DuckDB()
    logger.info("Building bronze Retail Layer")
    for table in tables:
        logger.info("Loading %s", table)
        db.load_layer(table, "bronze", query)
        logger.info("[%s] done", table)
    logger.info("Building bronze Retail Layer Completed")


def run_duckdb_silver() -> None:
    query = _load_query("silver")
    db = DuckDB()
    logger.info("Building Silver Retail Layer")
    db.load_layer("retail", "silver", query)
    db.apply_column_comments("silver_retail", "bronze_DataProperties")
    logger.info("Building Silver Retail Layer Completed")


def run_duckdb_gold() -> None:
    query = _load_query("gold")
    db = DuckDB()
    logger.info("Building Gold Retail Layer")
    db.load_layer("retail", "gold", query)
    logger.info("Building Gold Retail Layer Completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_duckdb_bronze()
    run_duckdb_silver()
    run_duckdb_gold()
