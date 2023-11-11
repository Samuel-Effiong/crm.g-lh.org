
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponseRedirect

from users.serializers import (UserSerializer, ShepherdSerializer, SubShepherdSerializer,
                               PermissionSerializer, CatalogSerializer,
                               FamilyMemberWeeklyScheduleSerializer,
                               WeekOneSerializer, WeekTwoSerializer,
                               WeekThreeSerializer, WeekFourSerializer)

from users.models import (Shepherd, SubShepherd, Catalog, Permission,
                          WeekOne, WeekTwo, WeekThree, WeekFour,
                          FamilyMemberWeeklySchedule)

from pastoring.models import (Testimony, PropheticWord, Blog, Sermon)

from pastoring.serializers import (TestimonySerializer, PropheticWordSerializer,
                                   BlogSerializer, SermonSerializer)

from .paginator import PageNumberPaginator
from .miscellaneous import reroute_to_user


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPaginator
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]


class ShepherdViewSet(ModelViewSet):
    queryset = Shepherd.objects.select_related('name').all()
    serializer_class = ShepherdSerializer
    pagination_class = PageNumberPaginator
    throttle_classes = [AnonRateThrottle]

    @action(detail=True)
    def user(self, request, *args, **kwargs):
        return reroute_to_user(self)


class SubShepherdViewSet(ModelViewSet):
    queryset = SubShepherd.objects.select_related('name').all()
    serializer_class = SubShepherdSerializer
    pagination_class = PageNumberPaginator

    @action(detail=True)
    def user(self, request, *args, **kwargs):
        return reroute_to_user(self)


class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.select_related('name').all()
    serializer_class = PermissionSerializer
    pagination_class = PageNumberPaginator

    @action(detail=True)
    def user(self, request, *args, **kwargs):
        return reroute_to_user(self)


class WeekOneViewSet(ModelViewSet):
    http_method_names = ['get', 'delete', 'head', 'options']
    queryset = WeekOne.objects.all()
    serializer_class = WeekOneSerializer
    pagination_class = PageNumberPaginator


class WeekTwoViewSet(ModelViewSet):
    http_method_names = ['get', 'delete', 'head', 'options']
    queryset = WeekTwo.objects.all()
    serializer_class = WeekTwoSerializer
    pagination_class = PageNumberPaginator


class WeekThreeViewSet(ModelViewSet):
    http_method_names = ['get', 'delete', 'head', 'options']
    queryset = WeekThree.objects.all()
    serializer_class = WeekThreeSerializer
    pagination_class = PageNumberPaginator


class WeekFourViewSet(ModelViewSet):
    http_method_names = ['get', 'delete', 'head', 'options']
    queryset = WeekFour.objects.all()
    serializer_class = WeekFourSerializer
    pagination_class = PageNumberPaginator


class FamilyWeeklyScheduleViewSet(ModelViewSet):
    http_method_names = ['get', 'delete', 'head', 'options']
    queryset = FamilyMemberWeeklySchedule.objects.all()
    serializer_class = FamilyMemberWeeklyScheduleSerializer
    pagination_class = PageNumberPaginator

    @action(detail=True)
    def user(self, request, *args, **kwargs):
        user = self.get_object().username
        return HttpResponseRedirect(reverse('customuser-detail', args=[user.pk]))

    @action(detail=True)
    def week_one(self, request, *args, **kwargs):
        week_one = self.get_object().weekone
        return HttpResponseRedirect(reverse('weekone-detail', args=[week_one.pk]))

    @action(detail=True)
    def week_two(self, request, *args, **kwargs):
        week_two = self.get_object().weektwo
        return HttpResponseRedirect(reverse('weektwo-detail', args=[week_two.pk]))

    @action(detail=True)
    def week_three(self, request, *args, **kwargs):
        week_three = self.get_object().weekthree
        return HttpResponseRedirect(reverse('weekthree-detail', args=[week_three.pk]))

    @action(detail=True)
    def week_four(self, request, *args, **kwargs):
        week_four = self.get_object().weekfour
        return HttpResponseRedirect(reverse('weekfour-detail', args=[week_four.pk]))


class CatalogViewSet(ModelViewSet):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    pagination_class = PageNumberPaginator


class TestimonyViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    queryset = Testimony.objects.all()
    serializer_class = TestimonySerializer
    pagination_class = PageNumberPaginator


class PropheticWordViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    queryset = PropheticWord.objects.all()
    serializer_class = PropheticWordSerializer
    pagination_class = PageNumberPaginator


class BlogViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = PageNumberPaginator


class SermonViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    queryset = Sermon.objects.all()
    serializer_class = SermonSerializer
    pagination_class = PageNumberPaginator