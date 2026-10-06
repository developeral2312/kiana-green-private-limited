import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

from users.models import CustomUser, Employee
from crm.models import Lead
from projects.models import Project, InstallationTask

def populate_ongoing():
    sales_user = CustomUser.objects.filter(role='sales').first()
    engineer_emp = Employee.objects.filter(designation='Senior Installer').first()

    # Create an ongoing Lead
    lead, created = Lead.objects.get_or_create(
        name="Ongoing Installation Lead",
        phone="9988776655",
        service="offgrid",
        defaults={'status': 'converted', 'assigned_to': sales_user}
    )

    # Create Project in 'structure' status
    project, _ = Project.objects.get_or_create(
        title="Ongoing Offgrid Installation",
        project_type="offgrid",
        status="structure",
        engineer=engineer_emp
    )
    project.lead = lead
    project.save()

    # Add Installation Tasks for the Engineer, some pending, some complete
    tasks_to_add = [
        ('site_inspection', 'completed'), 
        ('structure_fixing', 'in_progress'), 
        ('panel_mounting', 'new'), 
        ('wiring', 'new')
    ]

    for step, status in tasks_to_add:
        InstallationTask.objects.get_or_create(
            project=project,
            step=step,
            defaults={'assigned_to': engineer_emp.user if engineer_emp else None, 'status': status}
        )

    print("Ongoing project in 'structure' status added successfully!")

if __name__ == "__main__":
    populate_ongoing()
