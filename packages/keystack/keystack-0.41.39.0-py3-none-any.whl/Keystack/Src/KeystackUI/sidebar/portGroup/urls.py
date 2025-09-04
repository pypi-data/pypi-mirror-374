from django.urls import include, path, re_path
from sidebar.portGroup.views import PortGroup

urlpatterns = [
    path(r'', PortGroup.as_view(), name='portGroup'),

]
