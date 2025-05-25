from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ads/', include('ads.urls')),
    # ... other URL patterns ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 