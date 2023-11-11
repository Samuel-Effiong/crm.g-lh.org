from django.contrib import admin

from .models import Evangelism


# Register your models here.
@admin.register(Evangelism)
class EvangelismAdmin(admin.ModelAdmin):
    list_display = ('username', 'no_led_to_christ', 'holy_spirit_baptism')
    list_filter = ('username',)

