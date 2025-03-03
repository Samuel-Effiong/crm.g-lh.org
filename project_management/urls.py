from django.urls import path

from . import views


app_name = 'project_management'

urlpatterns = [
    path('', views.ProjectManagementView.as_view(), name='dashboard'),
    path('dashboard/<str:department>/', views.ProjectManagementView.as_view(), name='department_dashboard'),

    path('project/<str:department>/', views.DepartmentProjectListView.as_view(), name='project'),
    path('project/<str:department>/<int:pk>/', views.DepartmentProjectDetailView.as_view(), name='project-detail'),
    path('project/<str:department>/table/<int:pk>/', views.DepartmentTableDetailView.as_view(), name='project-department-table-detail'),

    path('project/calender/<str:department>/', views.DepartmentProjectCalenderView.as_view(), name='project-calender'),

    path('project/settings/admin', views.ProjectManagementAdminSettingView.as_view(), name='project-admin-settings'),
    path('project/settings/admin/<str:department>/<int:pk>', views.ProjectManagementAdminSettingDepartmentDetailView.as_view(), name='project-admin-setting-department-detail'),
    
    path('project/settings/<str:department>/', views.ProjectManagementSettingView.as_view(), name='project-settings'),
]
