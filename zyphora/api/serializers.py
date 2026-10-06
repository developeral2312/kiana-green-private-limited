
from rest_framework import serializers
from projects.models import Project, InstallationTask
from crm.models import Lead

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
