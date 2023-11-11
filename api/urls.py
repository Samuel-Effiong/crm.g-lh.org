
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet


router = routers.DefaultRouter()
wagtail_api_router = WagtailAPIRouter('wagtailapi')

wagtail_api_router.register_endpoint('pages', PagesAPIViewSet)
wagtail_api_router.register_endpoint('images', ImagesAPIViewSet)
wagtail_api_router.register_endpoint('document', DocumentsAPIViewSet)


router.register(r'users', views.UserViewSet, basename='customuser')
router.register(r'shepherds', views.ShepherdViewSet, basename='shepherd')
router.register(r'sub-shepherds', views.SubShepherdViewSet, basename='subshepherd')
router.register(r'permissions', views.PermissionViewSet, basename='permission')

router.register(r'family-schedule', views.FamilyWeeklyScheduleViewSet, basename='familymemberweeklyschedule')
router.register(r'week-one', views.WeekOneViewSet, basename='weekone')
router.register(r'week-two', views.WeekTwoViewSet, basename='weektwo')
router.register(r'week-three', views.WeekThreeViewSet, basename='weekthree')
router.register(r'week-four', views.WeekFourViewSet, basename='weekfour')

##################  WORKSPACE API URL  ########################
router.register(r'catalogs', views.CatalogViewSet, basename='catalog')
router.register(r'testimony', views.TestimonyViewSet, basename='testimony')
router.register(r'prophetic-word', views.PropheticWordViewSet, basename='propheticwords')
router.register(r'blog', views.BlogViewSet, basename='blog')
router.register(r'sermon', views.SermonViewSet, basename='sermon')


urlpatterns = [
    path('v2/', wagtail_api_router.urls),
    path('api-token-auth/', obtain_auth_token),
    path('', include(router.urls)),
]