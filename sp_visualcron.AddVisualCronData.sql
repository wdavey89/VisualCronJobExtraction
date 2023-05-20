USE [VisualCronInfo]
GO
/****** Object:  StoredProcedure [visualcron].[AddVisualCronInfo]    Script Date: 11/11/2022 11:44:38 ******/
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
@numberOfExecutes INT
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
			IF @CurrentJobDescription <> @jobDescription OR @CurrentGroupName <> @groupName OR @CurrentJobName <> @jobName OR @CurrentIsJobActive <> @isJobActive OR @CurrentLastExecutionTime <> @lastExecutionTime OR @CurrentNumberOfExecutes <> @numberOfExecutes
			IF @CurrentJobDescription <> @jobDescription OR @CurrentGroupName <> @groupName OR @CurrentJobName <> @jobName OR @CurrentIsJobActive <> @isJobActive 
				UPDATE [visualcron].[VisualCronData]
				SET JobDescription = @jobDescription, JobName = @jobName, GroupName = @groupName, IsJobActive = @isJobActive, LastExecutionTime = @lastExecutionTime, 
				NumberOfExecutes = @numberOfExecutes, DateEntryUpdatedInDatabase = GETDATE()
				SET JobDescription = @jobDescription, JobName = @jobName, GroupName = @groupName, IsJobActive = @isJobActive, DateEntryUpdatedInDatabase = GETDATE()
				WHERE ComputerName = @computerName AND JobId = @jobId
			ELSE IF @CurrentLastExecutionTime <> @lastExecutionTime OR @CurrentNumberOfExecutes <> @numberOfExecutes
				UPDATE [visualcron].[VisualCronData]
				SET LastExecutionTime = @lastExecutionTime, NumberOfExecutes = @numberOfExecutes
				WHERE ComputerName = @computerName AND JobId = @jobId
		END
		ELSE
			INSERT INTO [visualcron].[VisualCronData](ComputerName, JobId, JobName, JobDescription, GroupName, IsJobActive, LastExecutionTime, NumberOfExecutes, DateAddedToDatabase)
			VALUES (@computerName, @jobId, @jobName, @jobDescription, @groupName, @isJobActive, @lastExecutionTime, @numberOfExecutes, GETDATE())

END