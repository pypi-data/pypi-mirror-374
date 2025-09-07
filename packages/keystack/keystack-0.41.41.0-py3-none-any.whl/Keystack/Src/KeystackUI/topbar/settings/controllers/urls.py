from django.urls import include, path, re_path
from topbar.settings.controllers.views import Controllers

urlpatterns = [
    re_path('^$', Controllers.as_view(), name='controllers')
]

