
from django.urls import path, include

from . import views


app_name = 'site_admin'


urlpatterns = [
    path('', views.SiteAdminView.as_view(), name='homepage'),
    path('<str:category>/<str:sub_category>/', views.SiteAdminListView.as_view(), name='admin-category'),
    path('<str:category>/<str:sub_category>/<int:pk>/', views.SiteAdminDetailView.as_view(), name='admin-category-detail'),
    path('<str:category>/<str:sub_category>/<str:pk>/', views.SiteAdminDetailView.as_view(), name='admin-category-detail-str'),
]
