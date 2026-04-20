CREATE OR REPLACE TABLE {layer}_{table} AS
SELECT
    period_title                             AS period_label,
    CASE
        WHEN Periods LIKE '%MM%' THEN strptime(Periods, '%YMM%m')
        WHEN Periods LIKE '%JJ%' THEN strptime(REPLACE(Periods, 'JJ00', ''), '%Y')
    END                                      AS observation_date,
    branch_title                             AS industry_name,
    branch_description                       AS industry_details,
    UncorrectedProductionTurnover_1          AS turnover_value_index_raw,
    CalendarAdjustedProductionTurnover_2     AS turnover_value_index_calendar_adj,
    SeasonallyAdjustedProductionTurnover_3   AS turnover_value_index_seasonal_adj,
    UncorrectedProductionTurnover_4          AS turnover_growth_yoy_percentage,
    CalendarAdjustedProductionTurnover_5     AS volume_index_calendar_adj,
    UncorrectedProductionTurnover_6          AS volume_index_raw,
    period_status                            AS data_reliability_status
FROM silver_retail
WHERE UncorrectedProductionTurnover_1 IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_gold_date ON {layer}_{table} (observation_date);
CREATE INDEX IF NOT EXISTS idx_gold_industry ON {layer}_{table} (industry_name)
