from django.urls import include, path, re_path
from topbar.settings.domains.views import Domains

urlpatterns = [
    re_path('^$', Domains.as_view(), name='domains'),
]

