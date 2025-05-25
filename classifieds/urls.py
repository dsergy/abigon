"""
URL configuration for Abigon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include  
from django.conf import settings  
from django.conf.urls.static import static  
from .views import home, register, services, events  # импортируем конкретные функции  
from django.views.generic import TemplateView

# Error handlers
handler404 = 'classifieds.views.handler404'
handler500 = 'classifieds.views.handler500'

urlpatterns = [  
    path('', home, name='home'),  # Главная страница
    path('admin/', admin.site.urls),  
    path('accounts/', include('accounts.urls')),  
    path('accounts/', include('allauth.urls')),  # allauth URLs  
    path('ads/', include('ads.urls')),  # Изменено с '' на 'ads/'
    path('services/', services, name='services'),
    path('events/', events, name='events'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)