"""
URL configuration for attuned_energy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core_api.ai_views import ai_agent_query

urlpatterns = [
    path('login/', RedirectView.as_view(url='/users/login/', permanent=False), name='login_redirect'),
    path('admin/', admin.site.urls),
    path('users/',include('users.urls')),
    path('projects/',include('projects.urls')),
    path('procurement/',include('procurement.urls')),
    path('finance/',include('finance.urls')),
    path('',include('public.urls')),
    path('crm/',include('crm.urls')),
    path('partners/',include('partners.urls')),
    path('api/ai/query/', ai_agent_query, name='ai_agent_query'),
    path('api/mobile/', include('api.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)