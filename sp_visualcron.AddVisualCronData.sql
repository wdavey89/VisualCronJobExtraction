USE [VisualCronJobInformation]
GO
/****** Object:  StoredProcedure [visualcron].[AddVisualCronInfo]    Script Date: 12/05/2023 15:30:03 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


ALTER PROCEDURE [visualcron].[AddVisualCronInfo]
(
@computerName VARCHAR(15),
@jobId VARCHAR(36),
@jobName VARCHAR(100),
@jobDescription VARCHAR(255),
@groupName VARCHAR(50),
@isJobActive BIT,
@lastExecutionTime DATETIME2,
@numberOfExecutes INT,
@dateModified DATETIME2
)
AS
BEGIN
	SET NOCOUNT ON;
		DECLARE @CurrentJobDescription VARCHAR(255)
		DECLARE @CurrentGroupName VARCHAR(50)
		DECLARE @CurrentJobName VARCHAR(100)
		DECLARE @CurrentIsJobActive BIT
		DECLARE @CurrentLastExecutionTime DATETIME2
		DECLARE @CurrentNumberOfExecutes INT
		SET @CurrentJobDescription = (SELECT [JobDescription] FROM [visualcron].[VisualCronData] WHERE [ComputerName] = @computerName AND [JobId] = @jobId)
		SET @CurrentGroupName = (SELECT [GroupName] FROM [visualcron].[VisualCronData] WHERE ComputerName = @computerName AND JobId = @jobId)
		SET @CurrentJobName = (SELECT [JobName] FROM [visualcron].[VisualCronData] WHERE ComputerName = @computerName AND JobId = @jobId)
		SET @CurrentIsJobActive = (SELECT [IsJobActive] FROM [visualcron].[VisualCronData] WHERE ComputerName = @computerName AND JobId = @jobId)
		SET @CurrentLastExecutionTime = (SELECT [LastExecutionTime] FROM [visualcron].[VisualCronData] WHERE ComputerName = @computerName AND JobId = @jobId)
		SET @CurrentNumberOfExecutes = (SELECT [NumberOfExecutes] FROM [visualcron].[VisualCronData] WHERE ComputerName = @computerName AND JobId = @jobId)
		IF EXISTS (SELECT 1 FROM [visualcron].[VisualCronData] where ComputerName = @computerName AND JobId = @jobId)
		BEGIN
			IF @CurrentJobDescription <> @jobDescription OR @CurrentJobDescription IS NULL OR @CurrentJobDescription IS NOT NULL AND @jobDescription IS NULL OR @CurrentGroupName <> @groupName OR @CurrentJobName <> @jobName OR @CurrentIsJobActive <> @isJobActive 
				UPDATE [visualcron].[VisualCronData]
				SET JobDescription = @jobDescription, JobName = @jobName, GroupName = @groupName, IsJobActive = @isJobActive, DateEntryUpdatedInDatabase = @dateModified
				WHERE ComputerName = @computerName AND JobId = @jobId
			ELSE IF @CurrentLastExecutionTime <> @lastExecutionTime OR @CurrentNumberOfExecutes <> @numberOfExecutes
				UPDATE [visualcron].[VisualCronData]
				SET LastExecutionTime = @lastExecutionTime, NumberOfExecutes = @numberOfExecutes
				WHERE ComputerName = @computerName AND JobId = @jobId
		END
		ELSE
			INSERT INTO [visualcron].[VisualCronData](ComputerName, JobId, JobName, JobDescription, GroupName, IsJobActive, LastExecutionTime, NumberOfExecutes, DateAddedToDatabase, DateEntryUpdatedInDatabase)
			VALUES (@computerName, @jobId, @jobName, @jobDescription, @groupName, @isJobActive, @lastExecutionTime, @numberOfExecutes, GETDATE(), @dateModified)

END
