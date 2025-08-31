from django.urls import path, include
from . import views


app_name = 'project_management'

partial_views = views.PartialsView()


partials_url_patterns = [
    path('get_department_overview_selection/', partial_views.get_departments, name='get_departments'),
    path('get_members/', partial_views.get_members, name='get_members'),
    path('get_department_overview_selection/<str:all_department_option>', partial_views.get_departments, name='get_departments_with_options'),
    path('get_department_overview_selection/<str:all_department_option>/<str:department_filter>', partial_views.get_departments, name='get_departments_with_options_and_filters'),
    path('change_target_status/', partial_views.change_target_status, name='change_target_status_post'),
    path('change_target_status/<int:target_id>', partial_views.change_target_status, name='change_target_status'),
    # path('project_target_filter/<int:project_id>', partial_views.get_project_targets_by_filter, name='get_project_targets_by_filter'),
]


project_settings_patterns = [

    path('admin', views.ProjectManagementAdminSettingView.as_view(), name='project-admin-settings'),
    path('admin/<str:department>/<int:pk>', views.ProjectManagementAdminSettingDepartmentDetailView.as_view(), name='project-admin-setting-department-detail'),
    path('', views.ProjectManagementSettingView.as_view(), name='project-settings'),
    path('<str:diakonate>/', views.ProjectManagementSettingView.as_view(), name='project-settings-diakonate'),
    path('<str:diakonate>/<str:department>', views.ProjectManagementSettingView.as_view(), name='project-settings-diakonate-department'),
    path('<str:diakonate>/<str:department>/<str:unit>', views.ProjectManagementSettingView.as_view(), name='project-settings-diakonate-department-unit'),
]

urlpatterns = [
    path('', views.ProjectManagementView.as_view(), name='dashboard'),

    path('dashboard/<str:department>/', views.ProjectManagementView.as_view(), name='department_dashboard'),

    path('project/', views.DepartmentProjectListView.as_view(), name='project'),
    path('project/<str:department>/<int:pk>/', views.DepartmentProjectDetailView.as_view(), name='project-detail'),
    path('project/<str:department>/table/<int:pk>/', views.DepartmentTableDetailView.as_view(), name='project-department-table-detail'),
    path('project/calender/<str:department>/', views.DepartmentProjectCalenderView.as_view(), name='project-calender'),
    path('project/members/', views.ProjectMemberView.as_view(), name='project-members'),
    path('<str:department_name>/members/<int:pk>/', views.DepartmentMemberDetailView.as_view(), name='department-member-detail'),
    path('project/settings/', include(project_settings_patterns)),
    path('partials/', include(partials_url_patterns))
]
