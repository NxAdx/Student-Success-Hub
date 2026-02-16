from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('alumni/', include('alumni.urls')),
    path('resources/', include('resources.urls')),
    path('guidance/', include('guidance.urls')),
    path('hackathons/', include('hackathons.urls')),
    path('doubts/', include('doubts.urls')),
    path('chat/', include('chat.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('roadmaps/', include('roadmaps.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
