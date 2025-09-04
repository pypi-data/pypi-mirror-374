from django.urls import include, path, re_path
from topbar.settings.accountMgmt.views import AccountMgmt

urlpatterns = [
    re_path('^$', AccountMgmt.as_view(), name='accountMgmt'),
]

