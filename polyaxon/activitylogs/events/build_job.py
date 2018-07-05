import activitylogs

from event_manager.events import build_job

activitylogs.subscribe(build_job.BuildJobStartedTriggeredEvent)
activitylogs.subscribe(build_job.BuildJobSoppedTriggeredEvent)
activitylogs.subscribe(build_job.BuildJobDeletedTriggeredEvent)
activitylogs.subscribe(build_job.BuildJobCreatedEvent)
activitylogs.subscribe(build_job.BuildJobUpdatedEvent)
activitylogs.subscribe(build_job.BuildJobViewedEvent)
activitylogs.subscribe(build_job.BuildJobLogsViewedEvent)
activitylogs.subscribe(build_job.BuildJobStatusesViewedEvent)