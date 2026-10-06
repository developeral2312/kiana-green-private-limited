import os
import django
from django.utils import timezone
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

from users.models import CustomUser, Employee
from crm.models import Lead
from projects.models import Project, FeasibilityReport, InstallationTask
from finance.models import Invoice, PaymentMilestone, ProjectCosting, DesignCosting

def populate_completed():
    # 1. Create an Engineer User
    engineer_user, _ = CustomUser.objects.get_or_create(
        username='eng_test',
        defaults={'email': 'eng@example.com', 'role': 'engineer'}
    )
    engineer_user.set_password('eng123')
    engineer_user.save()

    eng_emp, _ = Employee.objects.get_or_create(
        user=engineer_user,
        defaults={'name': 'Test Engineer', 'designation': 'Senior Installer', 'is_active': True}
    )
    print("Created Engineer: eng_test / eng123")

    # 2. Create a Sales User
    sales_user, _ = CustomUser.objects.get_or_create(
        username='sales_test',
        defaults={'email': 'sales@example.com', 'role': 'sales'}
    )
    sales_user.set_password('sales123')
    sales_user.save()

    sales_emp, _ = Employee.objects.get_or_create(
        user=sales_user,
        defaults={'name': 'Test Sales', 'designation': 'Sales Exec', 'is_active': True}
    )
    print("Created Sales User: sales_test / sales123")

    # 3. Create a Lead
    lead, created = Lead.objects.get_or_create(
        name="Completed Project Lead",
        phone="8887776665",
        service="ongrid",
        defaults={'status': 'new', 'assigned_to': sales_user}
    )
    if created:
        lead.status = 'converted'
        lead.save()
        print("Created Lead and converted to Project")

    # 4. Get Project and mark as completed
    project = Project.objects.filter(lead=lead).first()
    if not project:
        project, _ = Project.objects.get_or_create(
            title="Completed Solar Project",
            project_type="ongrid",
            status="completed",
            engineer=eng_emp
        )
    else:
        project.status = "completed"
        project.engineer = eng_emp
        project.save()
    print(f"Project marked as completed, assigned to engineer ID: {eng_emp.id}")

    # 5. Add Installation Tasks for the Engineer and mark as completed
    tasks_to_add = ['site_inspection', 'structure_fixing', 'panel_mounting', 'wiring', 'testing']
    for step in tasks_to_add:
        task, _ = InstallationTask.objects.get_or_create(
            project=project,
            step=step,
            defaults={'assigned_to': engineer_user, 'status': 'new'}
        )
        task.mark_completed()

    # 6. Create Feasibility Report
    FeasibilityReport.objects.get_or_create(
        project=project,
        defaults={
            'site_type': 'residential',
            'roof_type': 'rcc',
            'roof_area': 2000,
            'shadow_analysis': 'none',
            'orientation': 'south',
            'connection_type': 'three_phase',
            'suggested_capacity': 10.0,
            'system_type': 'on_grid',
            'is_approved': True
        }
    )

    # 7. Create Costing Data
    dc, _ = DesignCosting.objects.get_or_create(
        project=project,
        defaults={'cost': Decimal('8000.00'), 'status': 'approved'}
    )
    ProjectCosting.objects.get_or_create(
        project=project,
        defaults={
            'design_costing': dc,
            'system_costing': Decimal('300000.00'),
            'kseb_cost': Decimal('15000.00'),
            'client_approved': True,
            'proposal_sent': True
        }
    )

    # 8. Create Payment Milestones (Showcase new feature)
    PaymentMilestone.objects.get_or_create(
        project=project,
        milestone_type='booking',
        defaults={'percentage': Decimal('20.00'), 'amount_due': Decimal('60000.00'), 'due_date': timezone.now().date() - datetime.timedelta(days=30), 'status': 'paid'}
    )
    PaymentMilestone.objects.get_or_create(
        project=project,
        milestone_type='final',
        defaults={'percentage': Decimal('10.00'), 'amount_due': Decimal('30000.00'), 'due_date': timezone.now().date(), 'status': 'pending'}
    )

    print("Completed project and payment milestones added successfully!")

if __name__ == "__main__":
    populate_completed()
