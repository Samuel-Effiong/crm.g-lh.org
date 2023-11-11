
from django.urls import path

from .views import (EvangelismListView, EvangelismDetailView)

app_name = 'evangelism'
urlpatterns = [
    path('', EvangelismListView.as_view(), name='list'),
    path('<int:pk>/', EvangelismDetailView.as_view(), name='detail'),

]

