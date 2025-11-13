-- =============================================
-- Useful Queries for Testing and Monitoring
-- =============================================

USE [DS_Cwk2_DB];
GO

-- =============================================
-- 1. Check table row counts
-- =============================================
SELECT 
    'SensorReadings' AS TableName,
    COUNT(*) AS RowCount
FROM dbo.SensorReadings
UNION ALL
SELECT 
    'SensorStats' AS TableName,
    COUNT(*) AS RowCount
FROM dbo.SensorStats
UNION ALL
SELECT 
    'Control' AS TableName,
    COUNT(*) AS RowCount
FROM dbo.Control;
GO

-- =============================================
-- 2. View latest readings per sensor
-- =============================================
SELECT * FROM dbo.vw_LatestSensorReadings
ORDER BY SensorID;
GO

-- =============================================
-- 3. View current statistics per sensor
-- =============================================
SELECT * FROM dbo.vw_CurrentSensorStats
ORDER BY SensorID;
GO

-- =============================================
-- 4. Readings by time range
-- =============================================
DECLARE @MinutesAgo INT = 5;

SELECT 
    SensorID,
    COUNT(*) AS ReadingCount,
    AVG(Temperature) AS AvgTemp,
    AVG(Wind) AS AvgWind,
    AVG(Humidity) AS AvgHumidity,
    AVG(CAST(CO2Level AS FLOAT)) AS AvgCO2
FROM dbo.SensorReadings
WHERE Timestamp >= DATEADD(MINUTE, -@MinutesAgo, GETUTCDATE())
GROUP BY SensorID
ORDER BY SensorID;
GO

-- =============================================
-- 5. Batch insert performance
-- =============================================
SELECT 
    BatchID,
    COUNT(*) AS RecordsInBatch,
    MIN(Timestamp) AS BatchStartTime,
    MAX(Timestamp) AS BatchEndTime,
    DATEDIFF(MILLISECOND, MIN(Timestamp), MAX(Timestamp)) AS DurationMs
FROM dbo.SensorReadings
WHERE BatchID IS NOT NULL
GROUP BY BatchID
ORDER BY BatchStartTime DESC;
GO

-- =============================================
-- 6. Check change tracking status
-- =============================================
SELECT 
    DB_NAME() AS DatabaseName,
    is_auto_cleanup_on,
    retention_period,
    retention_period_units_desc
FROM sys.change_tracking_databases
WHERE database_id = DB_ID();

SELECT 
    OBJECT_NAME(object_id) AS TableName,
    is_track_columns_updated_on,
    min_valid_version
FROM sys.change_tracking_tables
WHERE object_id = OBJECT_ID('dbo.SensorReadings');
GO

-- =============================================
-- 7. Get change tracking version
-- =============================================
SELECT CHANGE_TRACKING_CURRENT_VERSION() AS CurrentVersion;

SELECT * FROM dbo.Control;
GO

-- =============================================
-- 8. View changes since last watermark
-- =============================================
DECLARE @LastVersion BIGINT;
SELECT @LastVersion = LastChangeVersion FROM dbo.Control WHERE ControlID = 1;

SELECT 
    CT.SYS_CHANGE_VERSION,
    CT.SYS_CHANGE_OPERATION,
    SR.*
FROM dbo.SensorReadings SR
RIGHT JOIN CHANGETABLE(CHANGES dbo.SensorReadings, @LastVersion) CT
    ON SR.ReadingID = CT.ReadingID
ORDER BY CT.SYS_CHANGE_VERSION;
GO

-- =============================================
-- 9. Sensor reading distribution
-- =============================================
SELECT 
    SensorID,
    COUNT(*) AS TotalReadings,
    MIN(Timestamp) AS FirstReading,
    MAX(Timestamp) AS LastReading,
    DATEDIFF(SECOND, MIN(Timestamp), MAX(Timestamp)) AS TimeSpanSeconds
FROM dbo.SensorReadings
GROUP BY SensorID
ORDER BY SensorID;
GO

-- =============================================
-- 10. Recent inserts timeline (last 100)
-- =============================================
SELECT TOP 100
    ReadingID,
    SensorID,
    Temperature,
    Wind,
    Humidity,
    CO2Level,
    Timestamp,
    BatchID
FROM dbo.SensorReadings
ORDER BY Timestamp DESC;
GO

-- =============================================
-- 11. Performance: Index usage statistics
-- =============================================
SELECT 
    OBJECT_NAME(s.object_id) AS TableName,
    i.name AS IndexName,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates,
    s.last_user_seek,
    s.last_user_scan
FROM sys.dm_db_index_usage_stats s
INNER JOIN sys.indexes i ON s.object_id = i.object_id AND s.index_id = i.index_id
WHERE database_id = DB_ID()
    AND OBJECT_NAME(s.object_id) IN ('SensorReadings', 'SensorStats')
ORDER BY TableName, IndexName;
GO

-- =============================================
-- 12. Clear all data (keep schema)
-- =============================================
-- TRUNCATE TABLE dbo.SensorStats;
-- TRUNCATE TABLE dbo.SensorReadings;
-- UPDATE dbo.Control SET LastChangeVersion = 0, LastProcessedAt = NULL WHERE ControlID = 1;
-- GO
