# NL-AI Retail Lakehouse App

## Project Structure

```
NL-AI-Retail-Lakehouse-App/
├── retail_lakehouse/
│   ├── __init__.py
│   ├── cbs_to_lakehouse.py   # Orchestrator: ingestion -> bronze -> silver -> gold
│   ├── config.yaml           # CBS table_id and endpoint config
│   ├── app/
│   │   └── app.py            # Streamlit UI: chat interface + pipeline trigger
│   ├── core/
│   │   ├── __init__.py
│   │   └── agent.py          # RetailAgent: NL query -> DuckDB via Ollama
│   ├── data/
│   │   ├── Branches.json
│   │   ├── DataProperties.json
│   │   ├── Periods.json
│   │   ├── TypedDataSet.json
│   │   └── duckdb/
│   │       ├── lakehouse.duckdb  # Single DuckDB file for all layers
│   │       └── queries/
│   │           ├── bronze.sql       # Loads JSON -> bronze_{table} tables
│   │           ├── silver.sql    # Joins bronze tables -> silver_retail
│   │           └── gold.sql      # Aggregates silver -> gold layer
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py       # DuckDB: load_layer, run_duckdb_bronze, run_duckdb_silver, run_duckdb_gold
│   └── ingestion/
│       ├── __init__.py
│       └── cbs_api_extract.py # OData API fetch + save JSON (Table 85828ENG)
├── setup.sh                       # First-time setup: installs Poetry, pulls Ollama model, launches app
├── CLAUDE.md
├── poetry.lock
└── pyproject.toml                 # Poetry (duckdb, pyyaml, requests, streamlit, ollama)
```

## Architecture

- All layers (bronze, silver, gold) live in a single `lakehouse.duckdb` file.
- Table naming convention: `{layer}_{table}` (e.g. `bronze_TypedDataSet`, `silver_retail`, `gold_retail`).
- SQL for each layer lives in `data/duckdb/queries/{layer}.sql`.
- `load_layer(table, layer, query)` in `database.py` is the single entry point for writing any layer.
- `run_duckdb_bronze()` — loads all CBS JSON files into bronze layer tables.
- `run_duckdb_silver()` — joins bronze tables into `silver_retail`.
- `run_duckdb_gold()` — aggregates silver into `gold_retail`.
- `RetailAgent` in `core/agent.py` — translates natural language queries to DuckDB SQL via Ollama.
- `app/app.py` — Streamlit UI with chat interface and pipeline trigger.

## pythonfilecheckout

when run cleancode for python file run isort, black and flake8 on it

## sqlfile fluff

when run cleancode for sql files run sqlfluff and fix all fixable errors

## logging

Never use print statements. Always use logger.info (or logger.warning/logger.error as appropriate).
Use `logger = logging.getLogger(__name__)` at the module level.
Only call `logging.basicConfig` in `if __name__ == "__main__"` blocks.

## Exit

when I run exit always store the resume checkpoint in the file .clauderesume.txt and replace it everytime so that i can always hold the last checkpoint
