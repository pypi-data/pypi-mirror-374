from django.urls import include, path, re_path
from topbar.settings.userGroup.views import UserGroup


urlpatterns = [
    re_path('^$', UserGroup.as_view(), name='userGroupMgmt'),
]

