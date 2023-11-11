
from django.urls import path, include


from .views import (ChurchWorkListView, ChurchWorkDetailView)

app_name = 'church_work'
urlpatterns = [
    path('', ChurchWorkListView.as_view(), name='list'),
    path('<int:pk>/', ChurchWorkDetailView.as_view(), name='detail'),
]
