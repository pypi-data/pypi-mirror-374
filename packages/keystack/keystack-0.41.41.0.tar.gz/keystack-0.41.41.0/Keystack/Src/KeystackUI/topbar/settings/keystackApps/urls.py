from django.urls import include, path, re_path
from topbar.settings.keystackApps.views import Apps

urlpatterns = [
    re_path(r'^$', Apps.as_view(), name='apps'),
]
