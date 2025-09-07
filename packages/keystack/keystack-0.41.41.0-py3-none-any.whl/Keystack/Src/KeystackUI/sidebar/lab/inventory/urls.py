from django.urls import include, path, re_path
from sidebar.lab.inventory.views import Inventory

urlpatterns = [
    re_path(r'^$', Inventory.as_view(), name='inventory'),
    #re_path(r'exportCSV/(?P<domain>.*)', ExportCSV.as_view(), name="exportCSV")
]
