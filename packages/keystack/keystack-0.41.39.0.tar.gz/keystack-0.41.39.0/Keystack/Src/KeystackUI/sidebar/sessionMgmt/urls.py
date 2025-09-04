from django.urls import include, path, re_path
from sidebar.sessionMgmt.views import SessionMgmt, SessionDetails
#from sidebar.sessionMgmt.views import  WebsocketDemo

# DeletePipelines, GetSessions, GetTestReport, GetTestLogs, GetCronScheduler, JobScheduler, GetJobSchedulerCount, TerminateProcessId, ArchiveResults, ResumePausedOnError, ShowGroups, GetSessionGroups, GetPipelinesDropdown, GetPipelinesForJobScheduler, SavePipeline, GetPipelineTableData, GetServerTime,

urlpatterns = [
    #re_path(r'(?P<module>(.*))/(?P<testResultFolder>(.*))', TestResults.as_view(), name='testResults'),
    path(r'sessionDetails', SessionDetails.as_view(), name='sessionDetails'),
    re_path(r'^$', SessionMgmt.as_view(), name='sessionMgmt')
]
