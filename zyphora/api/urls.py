
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, ProjectViewSet, InstallationTaskViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', InstallationTaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
