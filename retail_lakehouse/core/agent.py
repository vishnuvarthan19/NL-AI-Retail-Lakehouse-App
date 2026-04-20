import logging

import duckdb
import ollama
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

_TABLE = "gold_retail"
_SYSTEM_PROMPT_TEMPLATE = """You are a Senior SQL Developer for a Dutch Retail firm writing DuckDB SQL.
SCHEMA:
{schema}
KEY RULES:
1. Use double quotes for column names with spaces.
2. Industry filters: Use ILIKE with wildcards (e.g., `industry_name ILIKE '%Hotel%'` or `ILIKE '%47%'` for SBI codes).
3. Exclude NULLs: `WHERE column IS NOT NULL` for the metric being queried.
4. Year filtering: `EXTRACT(YEAR FROM observation_date) = YYYY`.
5. Trends: Include both `observation_date` and metric. Default: AVG for percentages, SUM for volumes.
6. Latest data: CBS has 2-month lag. Use subquery to find max(observation_date), not CURRENT_DATE.
7. Return ONLY raw SQL. No markdown, no explanations."""

DATA_DIR = Path(__file__).parents[1] / "data"
_CONFIG_PATH = Path(__file__).parents[1] / "config.yaml"


class RetailAgent:
    def __init__(self):
        cfg = _load_agent_config()
        self.model = cfg["model"]
        self.max_retries = cfg["max_retries"]
        db_path= DATA_DIR / "duckdb/lakehouse.duckdb"
        self._conn = duckdb.connect(db_path)
        self._system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(schema=self._load_schema())

    def _load_schema(self):
        rows = self._conn.execute(f"DESCRIBE {_TABLE}").fetchall()
        lines = [f"Table: {_TABLE}", "Columns:"]
        lines += [f"- {r[0]}: {r[1]}" for r in rows]
        return "\n".join(lines)

    def _execute_sql(self, sql):
        try:
            return self._conn.execute(sql).df(), None
        except Exception as e:
            return None, str(e)

    def query(self, user_question):
        current_prompt = f"User Question: {user_question}"
        sql_query = ""

        for attempt in range(self.max_retries):
            response = ollama.generate(
                model=self.model,
                system=self._system_prompt,
                prompt=current_prompt,
            )
            sql_query = (
                response["response"].strip().replace("```sql", "").replace("```", "")
            )

            result, error = self._execute_sql(sql_query)

            if error is None:
                return {
                    "success": True,
                    "data": result,
                    "sql": sql_query,
                    "attempts": attempt + 1,
                }

            logger.warning("Attempt %d/%d failed: %s", attempt + 1, self.max_retries, error)

            if attempt < self.max_retries - 1:
                current_prompt = (
                    f"The previous SQL query was:\n{sql_query}\n\n"
                    f"It failed with this error:\n{error}\n\n"
                    "Please fix the error and provide the corrected SQL."
                )

        return {
            "success": False,
            "data": None,
            "sql": sql_query,
            "error": error,
            "attempts": self.max_retries,
        }


def _load_agent_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)["agent"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = RetailAgent()
    result = agent.query("Which 5 industries had the highest turnover growth in the most recent month available?")

    if result["success"]:
        logger.info(
            "Success in %d attempt(s)!\nSQL:\n%s\n%s",
            result["attempts"],
            result["sql"],
            result["data"].head(),
        )
    else:
        logger.error(
            "Failed after %d attempts\nError: %s\nSQL: %s",
            result["attempts"],
            result["error"],
            result["sql"],
        )
