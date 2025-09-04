from django.urls import include, path, re_path
from topbar.debug.awsS3.views import AwsS3

urlpatterns = [
    re_path(r'^$', AwsS3.as_view(), name='AwsS3')
]
