CREATE OR REPLACE TABLE {layer}_{table} AS
SELECT * FROM read_json_auto('{data_dir}/{table}.json')
