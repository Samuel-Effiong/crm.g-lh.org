from django.urls import path

from .views import Dashboard


app_name = 'hod_reports'
urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
]