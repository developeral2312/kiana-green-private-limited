
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from projects.models import Project, InstallationTask
from crm.models import Lead
from .serializers import LeadSerializer, ProjectSerializer, InstallationTaskSerializer

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    # permission_classes = [IsAuthenticated] # Commented for easy dev testing

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class InstallationTaskViewSet(viewsets.ModelViewSet):
    queryset = InstallationTask.objects.all()
    serializer_class = InstallationTaskSerializer
