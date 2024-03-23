from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from telegram.ext import (Updater, CommandHandler, MessageHandler)
from telegram import Update


token = "5928323972:AAFIokvKAKsQpXQaw6t8oFfUKPlDixc8AGw"

# Create your views here.
def telegram_webhook(request):
    if request.method == 'POST':
        if 'application/json' in request.content_type:
            data = JSONParser().parse(request)
        else:
            data = request.POST.dict()
        update = Update.de_json(data, bot)
    else:
        return HttpResponse(status=404)
    

