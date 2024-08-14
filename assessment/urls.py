"""assessment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from home.views import short_links


# Send signal every 12 hours

# hours = 60 * 60 * 24
# system_wide_tasks(verbose_name="Execute Daily Tasks", repeat=hours, repeat_until=None)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin', RedirectView.as_view(url='/admin/', permanent=True)),

    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('pages/', include(wagtail_urls)),

    path('bot/', include('bot.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')),

    re_path(r'^(?!admin|api|auth|media|cms|documents|pages|bot|accounts|fetch|deactivate|users-profile|users-registration|users-login|users-logout|users-recover-password|users-tasks|coming-soon|personal-development|church-work|evangelism|prophetic-vision|catalog|suggestion-complaints|update-counter|pastoring|project-management|site_admin).*$', short_links, name='short-links')
]

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

