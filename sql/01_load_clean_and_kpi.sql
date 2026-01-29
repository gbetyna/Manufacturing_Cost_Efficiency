USE ManufacturingCostEfficiency;
GO

/* =========================================================
   01) CLEAN LAYER: DROP + CREATE + LOAD (idempotent)
   ========================================================= */

IF OBJECT_ID('dbo.cost_efficiency_clean', 'U') IS NOT NULL
    DROP TABLE dbo.cost_efficiency_clean;
GO

CREATE TABLE dbo.cost_efficiency_clean (
    [timestamp] datetime2(0),
    plant nvarchar(50),
    line nvarchar(50),
    shift nvarchar(50),
    product_family nvarchar(50),
    cycle_time_sec float,
    cavity float,
    efficiency_pct float,
    downtime_rate float,
    scrap_rate float,
    units_per_hour float,
    effective_units_per_hour float,
    good_units_per_hour float,
    material_cost_per_unit float,
    labor_cost_per_hour float,
    energy_cost_per_hour float,
    overhead_cost_per_hour float,
    total_cost_per_hour float,
    cost_per_unit float,
    cost_per_good_unit float,
    scrap_cost_per_unit_proxy float
);
GO

INSERT INTO dbo.cost_efficiency_clean
SELECT
    TRY_CONVERT(datetime2(0), [timestamp], 126),
    plant,
    line,
    shift,
    product_family,
    TRY_CONVERT(float, cycle_time_sec),
    TRY_CONVERT(float, cavity),
    TRY_CONVERT(float, efficiency_pct),
    TRY_CONVERT(float, downtime_rate),
    TRY_CONVERT(float, scrap_rate),
    TRY_CONVERT(float, units_per_hour),
    TRY_CONVERT(float, effective_units_per_hour),
    TRY_CONVERT(float, good_units_per_hour),
    TRY_CONVERT(float, material_cost_per_unit),
    TRY_CONVERT(float, labor_cost_per_hour),
    TRY_CONVERT(float, energy_cost_per_hour),
    TRY_CONVERT(float, overhead_cost_per_hour),
    TRY_CONVERT(float, total_cost_per_hour),
    TRY_CONVERT(float, cost_per_unit),
    TRY_CONVERT(float, cost_per_good_unit),
    TRY_CONVERT(float, scrap_cost_per_unit_proxy)
FROM dbo.cost_efficiency_data;
GO

/* =========================================================
   02) DATA QUALITY CHECKS
   ========================================================= */

SELECT COUNT(*) AS clean_rows
FROM dbo.cost_efficiency_clean;
GO

SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN [timestamp] IS NULL THEN 1 ELSE 0 END) AS null_timestamps,
    SUM(CASE WHEN cost_per_good_unit IS NULL THEN 1 ELSE 0 END) AS null_cost_per_good_unit
FROM dbo.cost_efficiency_clean;
GO

/* =========================================================
   03) INDEXES (idempotent)
   ========================================================= */

IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_cost_eff_timestamp' AND object_id = OBJECT_ID('dbo.cost_efficiency_clean'))
    DROP INDEX ix_cost_eff_timestamp ON dbo.cost_efficiency_clean;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_cost_eff_plant_line' AND object_id = OBJECT_ID('dbo.cost_efficiency_clean'))
    DROP INDEX ix_cost_eff_plant_line ON dbo.cost_efficiency_clean;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_cost_eff_product' AND object_id = OBJECT_ID('dbo.cost_efficiency_clean'))
    DROP INDEX ix_cost_eff_product ON dbo.cost_efficiency_clean;
GO

CREATE INDEX ix_cost_eff_timestamp ON dbo.cost_efficiency_clean ([timestamp]);
CREATE INDEX ix_cost_eff_plant_line ON dbo.cost_efficiency_clean (plant, line);
CREATE INDEX ix_cost_eff_product ON dbo.cost_efficiency_clean (product_family);
GO

/* =========================================================
   04) KPI QUERIES
   ========================================================= */

SELECT
    ROUND(AVG(cost_per_good_unit), 4) AS avg_cost_per_good_unit
FROM dbo.cost_efficiency_clean;
GO

SELECT TOP (5)
    plant,
    line,
    ROUND(AVG(cost_per_good_unit), 4) AS avg_cost
FROM dbo.cost_efficiency_clean
GROUP BY plant, line
ORDER BY AVG(cost_per_good_unit) DESC;
GO

SELECT
    product_family,
    ROUND(AVG(scrap_rate), 4) AS avg_scrap,
    ROUND(AVG(cost_per_good_unit), 4) AS avg_cost
FROM dbo.cost_efficiency_clean
GROUP BY product_family
ORDER BY AVG(scrap_rate) DESC;
GO
