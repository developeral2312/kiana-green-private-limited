import os
import django
from django.utils import timezone
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

from users.models import CustomUser
from crm.models import Lead
from projects.models import Project, FeasibilityReport
from finance.models import Invoice, ExpenseReport, ExpenseItem, ProjectCosting, DesignCosting

def populate():
    # 1. Create a dummy admin if none exists
    admin, created = CustomUser.objects.get_or_create(
        username='admin_test',
        defaults={'is_superuser': True, 'is_staff': True, 'email': 'admin_test@example.com'}
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("Created admin_test user (password: admin123)")

    # 2. Create a Lead
    lead, created = Lead.objects.get_or_create(
        name="PDF Tester Lead",
        phone="9998887776",
        service="ongrid",
        defaults={'status': 'new'}
    )
    if created:
        lead.status = 'converted'
        lead.save() # This triggers Project creation in Lead.save()
        print("Created Lead and converted to Project")

    # 3. Get or Create Project
    project = Project.objects.filter(lead=lead).first()
    if not project:
        project, _ = Project.objects.get_or_create(
            title="PDF Tester Solar Project",
            project_type="ongrid",
            status="costing_approval"
        )
    print("Project ID:", project.id)

    # 4. Create Feasibility Report
    FeasibilityReport.objects.get_or_create(
        project=project,
        defaults={
            'site_type': 'residential',
            'roof_type': 'rcc',
            'roof_area': 1500,
            'shadow_analysis': 'none',
            'orientation': 'south',
            'connection_type': 'three_phase',
            'suggested_capacity': 5.0,
            'system_type': 'on_grid',
            'is_approved': True
        }
    )
    print("Added Feasibility Report")

    # 5. Create Costing Data
    dc, _ = DesignCosting.objects.get_or_create(
        project=project,
        defaults={'cost': Decimal('5000.00'), 'status': 'approved'}
    )
    ProjectCosting.objects.get_or_create(
        project=project,
        defaults={
            'design_costing': dc,
            'system_costing': Decimal('150000.00'),
            'kseb_cost': Decimal('10000.00'),
            'client_approved': True,
            'proposal_sent': True
        }
    )
    print("Added Costing Data")

    # 6. Create Invoice
    Invoice.objects.get_or_create(
        project=project,
        invoice_number=f"INV-TEST-{project.id}",
        defaults={
            'issue_date': timezone.now().date(),
            'due_date': timezone.now().date() + datetime.timedelta(days=15),
            'total_amount': Decimal('165000.00'),
            'status': 'sent'
        }
    )
    print("Added Invoice")
    
    # 7. Create Expense Report for testing
    expense, ex_created = ExpenseReport.objects.get_or_create(
        project=project,
        category='materials',
        defaults={
            'expense_date': timezone.now().date(),
            'status': 'approved'
        }
    )
    if ex_created:
        ExpenseItem.objects.create(report=expense, description="Solar Panels 5kW", amount=Decimal("75000.00"))
        ExpenseItem.objects.create(report=expense, description="Inverter", amount=Decimal("40000.00"))
        print("Added Expenses")
        
    print("Database populated successfully! You can now test PDF generation for Invoices, Costings, etc.")

if __name__ == "__main__":
    populate()
