from django.urls import include, path, re_path
from topbar.utilizations.views import Utilizations

urlpatterns = [
    re_path(r'^$', Utilizations.as_view(), name='utilizations')
]
