-- =============================================
-- Database Cleanup Script
-- WARNING: This will delete all data!
-- =============================================

USE [DS_Cwk2_DB];
GO

PRINT 'Starting cleanup...';
GO

-- Disable change tracking
IF EXISTS (
    SELECT * FROM sys.change_tracking_tables 
    WHERE object_id = OBJECT_ID('dbo.SensorReadings')
)
BEGIN
    ALTER TABLE dbo.SensorReadings DISABLE CHANGE_TRACKING;
    PRINT 'Change tracking disabled on dbo.SensorReadings';
END
GO

-- Drop views
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_CurrentSensorStats')
BEGIN
    DROP VIEW dbo.vw_CurrentSensorStats;
    PRINT 'View vw_CurrentSensorStats dropped';
END
GO

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_LatestSensorReadings')
BEGIN
    DROP VIEW dbo.vw_LatestSensorReadings;
    PRINT 'View vw_LatestSensorReadings dropped';
END
GO

-- Drop procedures
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_CalculateSensorStats')
BEGIN
    DROP PROCEDURE dbo.usp_CalculateSensorStats;
    PRINT 'Procedure usp_CalculateSensorStats dropped';
END
GO

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_InsertSensorReadings')
BEGIN
    DROP PROCEDURE dbo.usp_InsertSensorReadings;
    PRINT 'Procedure usp_InsertSensorReadings dropped';
END
GO

-- Drop tables
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'SensorStats')
BEGIN
    DROP TABLE dbo.SensorStats;
    PRINT 'Table dbo.SensorStats dropped';
END
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Control')
BEGIN
    DROP TABLE dbo.Control;
    PRINT 'Table dbo.Control dropped';
END
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'SensorReadings')
BEGIN
    DROP TABLE dbo.SensorReadings;
    PRINT 'Table dbo.SensorReadings dropped';
END
GO

PRINT 'Cleanup completed successfully!';
GO
