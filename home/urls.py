from django.urls import path, include, re_path
from .views import (Home, Profile, Registration, Login, logout_user, CounterUpdate,
                    ChartBibleReading, CatalogView, TaskView, ComingSoonView,
                    SuggestionComplaintView, RecoverPasswordView, short_links)


urlpatterns = [
    path('', Home.as_view(), name='home'),

    # This URL is reserved only for dialog-boxes that will be use on the home page
    # for fetech request
    path('fetch/<str:mode>/dialog-box/', Home.as_view(), name='fetch'),

    # This URL is reserved only for the deactivation of notifications on the home page
    path('deactivate/<str:mode>/<int:notification_id>/', Home.as_view(), name='deactivate-notification'),

    path('users-profile/<str:username>/', Profile.as_view(), name='users-profiles'),
    path('users-registration/', Registration.as_view(), name='users-registration'),
    path('users-login/', Login.as_view(), name='users-login'),
    path('users-logout/', logout_user, name='users-logout'),
    path('users-recover-password/', RecoverPasswordView.as_view(), name='users-recover-password'),

    path('users-tasks/', TaskView.as_view(), name='users-task'),
    path('coming-soon/<str:category>/', ComingSoonView.as_view(), name='coming-soon'),

    path('personal-development/', include('personal_development.urls')),
    path('church-work/', include('church_work.urls')),
    path('evangelism/', include('evangelism.urls')),
    path('prophetic-vision/', include('prophetic_vision.urls')),

    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('suggestion-complaints/<str:mode>/', SuggestionComplaintView.as_view(), name='suggestion-complaint'),

    path('update-counter/', CounterUpdate.as_view(), name='update-counter'),
    path('update-counter/<str:category>/<str:mode>/', ChartBibleReading.as_view(), name='update-charts'),

    path('pastoring/', include('pastoring.urls')),
    path('project-management/', include('project_management.urls')),
    path('site_admin/', include('site_admin.urls')),
]