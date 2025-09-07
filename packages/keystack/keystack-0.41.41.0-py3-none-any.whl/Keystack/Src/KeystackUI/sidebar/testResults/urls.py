from django.urls import include, path, re_path
from sidebar.testResults.views import TestResults

urlpatterns = [
    re_path(r'^$', TestResults.as_view(), name='testResults'),
]
