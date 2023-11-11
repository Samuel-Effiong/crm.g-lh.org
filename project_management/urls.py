from django.urls import path, include

from . import views


app_name = 'project_management'

urlpatterns = [
    path('', views.ProjectManagementView.as_view(), name='dashboard'),
    path('project/<str:department>/', views.DepartmentProjectListView.as_view(), name='project'),
    path('project/<str:department>/<int:pk>/', views.DepartmentProjectDetailView.as_view(), name='project-detail'),

    path('project/settings/<str:department>/', views.ProjectManagementSettingView.as_view(), name='project-settings'),
]
