from django.urls import include, path, re_path
#from sidebar.portMgmt.views import PortMgmt, ShowProfile, PortGroup
from sidebar.portMgmt.views import ShowProfile

urlpatterns = [
    #re_path(r'^$', PortMgmt.as_view(), name='portMgmt'),
    re_path(r'showProfile/(?P<profileName>(.*))', ShowProfile.as_view(), name='showProfile'),
    #re_path(r'portGroup', PortGroup.as_view(), name='portGroup')
]
