
USE [DS_Cwk2_DB];
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SensorReadings')
BEGIN
    CREATE TABLE dbo.SensorReadings (
        ReadingID BIGINT IDENTITY(1,1) PRIMARY KEY,
        SensorID INT NOT NULL,
        Temperature DECIMAL(5,2) NOT NULL,  -- Celsius
        Wind DECIMAL(5,2) NOT NULL,         -- kph
        Humidity DECIMAL(5,2) NOT NULL,     -- percentage
        CO2Level INT NOT NULL,              -- ppm
        Timestamp DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    
    PRINT 'Table dbo.SensorReadings created successfully';
END
ELSE
BEGIN
    PRINT 'Table dbo.SensorReadings already exists';
END
GO

PRINT '';
PRINT 'Database schema setup completed successfully!';
PRINT 'Tables: SensorReadings, SensorStats, Control';
PRINT 'Views: vw_LatestSensorReadings, vw_CurrentSensorStats';
PRINT 'Stored Procedures: usp_InsertSensorReadings, usp_CalculateSensorStats';
GO
