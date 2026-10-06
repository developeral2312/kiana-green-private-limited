import os

# 1. Update users/models.py with EmployeeKPI
users_models_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\users\models.py"
kpi_code = """
# -------------------------------
# Employee Performance / KPI
# -------------------------------
class EmployeeKPI(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='kpis')
    month = models.DateField()
    target_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    achieved_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leads_assigned = models.IntegerField(default=0)
    leads_converted = models.IntegerField(default=0)
    projects_completed_on_time = models.IntegerField(default=0)
    projects_delayed = models.IntegerField(default=0)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.user.username} - KPI {self.month.strftime('%b %Y')}"
"""
with open(users_models_path, "a", encoding="utf-8") as f:
    f.write(kpi_code)


# 2. Update users/utils.py to add Email capability
utils_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\users\utils.py"
with open(utils_path, "r", encoding="utf-8") as f:
    utils_content = f.read()

email_import = "from django.core.mail import send_mail\nfrom django.conf import settings\n"
if "send_mail" not in utils_content:
    utils_content = email_import + utils_content

# We'll just replace the Notification.objects.create logic
if "Notification.objects.create(" in utils_content:
    new_logic = """
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        title=title,
        message=message,
        link=link,
        category=category
    )
    # Trigger Email hook
    if recipient and recipient.email:
        try:
            send_mail(
                subject=f"Zyphora ERP: {title}",
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@kianagreen.com'),
                recipient_list=[recipient.email],
                fail_silently=True,
            )
        except Exception as e:
            pass # Ignore email failure in dev
    return notification
"""
    # Replace the return Notification.objects.create block
    import re
    utils_content = re.sub(r'return Notification\.objects\.create\([^)]+\)', new_logic.strip(), utils_content, flags=re.DOTALL)

with open(utils_path, "w", encoding="utf-8") as f:
    f.write(utils_content)


# 3. Create Escalation Matrix Tasks in projects/tasks.py
tasks_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\projects\tasks.py"
tasks_code = """
from celery import shared_task
from django.utils import timezone
from .models import Project
from users.utils import create_notification
from users.models import CustomUser

@shared_task
def check_sla_and_escalate():
    \"\"\" Escalation Matrix Engine (SLA/TAT) \"\"\"
    delayed_projects = Project.objects.filter(end_date__lt=timezone.now().date()).exclude(status='completed')
    
    for project in delayed_projects:
        days_delayed = (timezone.now().date() - project.end_date).days
        
        # Escalate if delayed by more than 3 days
        if days_delayed >= 3:
            admins = CustomUser.objects.filter(role='admin')
            for admin in admins:
                create_notification(
                    recipient=admin,
                    title="🚨 SLA ESCALATION",
                    message=f"Project {project.project_id or project.title} is delayed by {days_delayed} days! Current Status: {project.get_status_display()}.",
                    category="system"
                )
"""
with open(tasks_path, "w", encoding="utf-8") as f:
    f.write(tasks_code.strip())


# 4. Universal Search and Customer 360 in public/views.py (or crm/views)
crm_views_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\crm\views.py"
search_code = """
from django.http import JsonResponse
from django.db.models import Q
from projects.models import Project
from finance.models import Invoice

def universal_search(request):
    \"\"\" Enterprise Universal Search \"\"\"
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({"results": []})
        
    results = []
    
    # 1. Search Leads
    leads = Lead.objects.filter(Q(phone__icontains=q) | Q(name__icontains=q) | Q(email__icontains=q))[:5]
    for l in leads:
        results.append({"type": "Lead", "title": l.name, "subtitle": l.phone, "url": f"/crm/lead/{l.id}/"})
        
    # 2. Search Projects
    projects = Project.objects.filter(Q(project_id__icontains=q) | Q(title__icontains=q))[:5]
    for p in projects:
        results.append({"type": "Project", "title": p.project_id or p.title, "subtitle": p.get_status_display(), "url": f"/projects/{p.id}/"})
        
    # 3. Search Invoices
    invoices = Invoice.objects.filter(invoice_number__icontains=q)[:5]
    for i in invoices:
        results.append({"type": "Invoice", "title": i.invoice_number, "subtitle": f"₹{i.total_amount}", "url": f"/finance/invoice/{i.id}/"})
        
    return JsonResponse({"results": results})

def customer_360(request, phone):
    \"\"\" Customer 360 Degree View \"\"\"
    leads = Lead.objects.filter(phone=phone)
    projects = Project.objects.filter(lead__phone=phone)
    invoices = Invoice.objects.filter(project__in=projects)
    
    data = {
        "customer": phone,
        "total_leads": leads.count(),
        "total_projects": projects.count(),
        "total_invoices": invoices.count(),
        "revenue_value": sum(i.total_amount for i in invoices if i.status == 'paid')
    }
    return JsonResponse(data)
"""
with open(crm_views_path, "a", encoding="utf-8") as f:
    f.write("\n" + search_code)

print("Enterprise features added.")
