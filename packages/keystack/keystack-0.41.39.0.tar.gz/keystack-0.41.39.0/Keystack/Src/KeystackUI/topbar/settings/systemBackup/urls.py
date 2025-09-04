from django.urls import include, path, re_path
from topbar.settings.systemBackup.views import SystemBackup

urlpatterns = [
    re_path('^$', SystemBackup.as_view(), name='system_backup'),
]

