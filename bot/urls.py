from django.urls import path, include

from .views import telegram_webhook

app_name = 'bot'

urlpatterns = [
    path('webhook/', telegram_webhook)
]