from django.urls import include, path, re_path

from topbar.settings.loginCredentials.views import LoginCredentials

urlpatterns = [
    path('settings', LoginCredentials.as_view(), name='loginCredentials')
]

