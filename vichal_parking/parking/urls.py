from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("entry/", views.vehicle_entry, name="vehicle_entry"),
    path("exit/", views.vehicle_exit, name="vehicle_exit"),
    path("reports/", views.reports, name="reports"),
]
