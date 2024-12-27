from django.urls import path, include
from . import views 

app_name = 'diaconate'

treasury_urls = [
    path('dashboard/', views.TreasuryDashboardView.as_view(), name='treasury-dashboard'),
    path('pending-request/', views.TreasuryPendingRequestView.as_view(), name='treasury-pending-request'),
    path('inventory/', views.TreasuryInventoryView.as_view(), name='treasury-inventory'),
    path('maintenance/', views.TreasuryMaintenanceView.as_view(), name='treasury-maintenance')
]

urlpatterns = [
    path('treasury/', include(treasury_urls))
    # path('', views.TreasuryDashboardView.as_view(), name='treasury-dashboard'),
]