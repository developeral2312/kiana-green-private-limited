from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, ProjectViewSet, InstallationTaskViewSet, SiteVisitViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', InstallationTaskViewSet)
router.register(r'visits', SiteVisitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
