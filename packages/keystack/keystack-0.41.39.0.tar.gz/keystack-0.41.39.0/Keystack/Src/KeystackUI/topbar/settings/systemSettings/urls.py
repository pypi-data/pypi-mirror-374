from django.urls import include, path, re_path

from topbar.settings.systemSettings.views import Settings

urlpatterns = [
    path('settings', Settings.as_view(), name='systemSettings')
]

