from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

# Create your models here.


class PropheticVision(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='username')
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=1000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    body = models.TextField()

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse("prophetic_vision:detail", args=[self.username.username, self.date.month,
                       self.date.year, self.id])

    class Meta:
        ordering = ('-date', )
