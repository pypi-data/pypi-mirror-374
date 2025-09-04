from django.urls import include, path, re_path
from topbar.debug.systemLogs.views import SystemLogs

urlpatterns = [
    re_path(r'^$', SystemLogs.as_view(), name='systemLogs'),
    # path(r'getLogMessages', GetLogMessages.as_view(), name='getLogMessages'),
    # path(r'deleteLogs', DeleteLogs.as_view(), name='deleteLogs'),
]
