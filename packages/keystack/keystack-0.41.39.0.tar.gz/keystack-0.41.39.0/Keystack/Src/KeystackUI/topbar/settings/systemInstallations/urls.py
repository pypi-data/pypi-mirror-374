from django.urls import include, path, re_path

from topbar.settings.systemInstallations.views import SystemInstallations

urlpatterns = [
    path('systemInstallations', SystemInstallations.as_view(), name='systemInstallations')
]

