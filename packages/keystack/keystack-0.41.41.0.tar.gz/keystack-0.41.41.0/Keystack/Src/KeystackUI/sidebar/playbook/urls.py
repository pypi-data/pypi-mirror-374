from django.urls import include, path, re_path

from sidebar.playbook.views import Playbook

urlpatterns = [
    #re_path(r'(?P<module>(.*))/(?P<testResultFolder>(.*))', TestResults.as_view(), name='testResults'),
    path(r'',                  Playbook.as_view(),                        name='playbooksView'),
]
