from django.http import HttpResponseRedirect
from rest_framework.reverse import reverse


def reroute_to_user(obj):
    user = obj.get_object().name
    return HttpResponseRedirect(reverse('customuser-detail', args=[user.pk]))