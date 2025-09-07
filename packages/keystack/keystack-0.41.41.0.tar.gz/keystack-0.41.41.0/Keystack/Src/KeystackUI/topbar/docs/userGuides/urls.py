from django.urls import include, path, re_path
from topbar.docs.userGuides.views import UserGuides

# REST APIs
urlpatterns = [
    re_path('^$', UserGuides.as_view(), name='userGuides'),
]
