
from rest_framework import serializers
from projects.models import Project, InstallationTask
from crm.models import Lead, SiteVisit

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class InstallationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallationTask
        fields = '__all__'

class SiteVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteVisit
        fields = '__all__'
