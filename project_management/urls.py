from django.urls import path, include

from . import views


app_name = 'project_management'

partial_views = views.PartialsView()


partials_url_patterns = [
    path('get_department_overview_selection/', partial_views.get_departments, name='get_departments'),
    path('get_department_overview_selection/<str:all_department_option>', partial_views.get_departments, name='get_departments_with_options')
]

urlpatterns = [
    path('', views.ProjectManagementView.as_view(), name='dashboard'),

    path('dashboard/<str:department>/', views.ProjectManagementView.as_view(), name='department_dashboard'),

    path('project/', views.DepartmentProjectListView.as_view(), name='project'),
    path('project/<str:department>/<int:pk>/', views.DepartmentProjectDetailView.as_view(), name='project-detail'),
    path('project/<str:department>/table/<int:pk>/', views.DepartmentTableDetailView.as_view(), name='project-department-table-detail'),

    path('project/calender/<str:department>/', views.DepartmentProjectCalenderView.as_view(), name='project-calender'),

    path('project/settings/admin', views.ProjectManagementAdminSettingView.as_view(), name='project-admin-settings'),
    path('project/settings/admin/<str:department>/<int:pk>', views.ProjectManagementAdminSettingDepartmentDetailView.as_view(), name='project-admin-setting-department-detail'),

    path('project/settings/', views.ProjectManagementSettingView.as_view(), name='project-settings'),
    path('project/settings/<str:diakonate>/', views.ProjectManagementSettingView.as_view(), name='project-settings-diakonate'),
    path('project/settings/<str:diakonate>/<str:department>', views.ProjectManagementSettingView.as_view(), name='project-settings-diakonate-department'),


    path('partials/', include(partials_url_patterns))
]
