
from django.urls import path
from .views import (PropheticVisionListView, PropheticVisionDetailView)

app_name = 'prophetic_vision'
urlpatterns = [
    path('', PropheticVisionListView.as_view(), name='list'),
    path('<str:name>/<str:month>/<str:year>/<int:pk>/', PropheticVisionDetailView.as_view(), name='detail'),
]
