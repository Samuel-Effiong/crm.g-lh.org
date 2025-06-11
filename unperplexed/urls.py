from django.urls import path, include
from . import views

app_name = 'unperplexed'


worker = [
    path("", views.WorkerView.as_view(), name='worker'),
    path('<str:worker>/', views.WorkerDetail.as_view(), name='worker-detail'),
    # path('<str:worker>/contracts', name="worker-contracts ),
    # path("<str:worker>/contracts/<pk:contract_id>/", name="worker-contracts-detail"),
]

contract = [
    path("", views.ContractView.as_view(), name="contract"),
    # path("<pk:contract_id>/", name="contract-detail"),
]

admin = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('worker/', include(worker)),
    path('contract/', include(contract)),
    path('organization/', views.OrganizationView.as_view(), name='organization'),
]


urlpatterns = [
    path("admin/", include(admin)),
    path("", views.Homepage.as_view(), name="homepage"),
]
