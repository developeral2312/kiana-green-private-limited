from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from crm.models import Lead
from projects.models import Task
from users.models import CustomUser, Notification
from users.views import create_notification

class Command(BaseCommand):
    help = 'Check for SLA/TAT breaches and escalate tasks and leads'

    def handle(self, *args, **options):
        self.stdout.write("Starting Escalation Check...")
        now = timezone.now()
        today = now.date()
        
        # We need an admin user to send notifications to (or the L2/L3 managers)
        admins = CustomUser.objects.filter(role='admin')
        staff = CustomUser.objects.filter(role='staff')
        
        # ----------------------------------------------------
        # 1. ESCALATE TASKS
        # ----------------------------------------------------
        # Tasks overdue by 1 day -> L1 (Supervisor/Staff)
        # Tasks overdue by 3 days -> L2 (Admin)
        
        pending_tasks = Task.objects.exclude(status='completed')
        
        for task in pending_tasks:
            if task.due_date and task.due_date < today:
                days_overdue = (today - task.due_date).days
                
                # Check for L2 Escalation (3+ days)
                if days_overdue >= 3 and task.escalation_level < 2:
                    task.escalation_level = 2
                    task.escalated_at = now
                    task.status = 'overdue'
                    task.save()
                    
                    self.stdout.write(f"Task '{task.title}' escalated to L2 (Admin)")
                    for admin in admins:
                        create_notification(
                            recipient=admin,
                            sender=None,
                            title=f"L2 Escalation: Overdue Task",
                            message=f"Task '{task.title}' assigned to {task.assigned_to.name} is overdue by {days_overdue} days.",
                            category="escalation"
                        )
                        
                # Check for L1 Escalation (1-2 days)
                elif days_overdue >= 1 and task.escalation_level < 1:
                    task.escalation_level = 1
                    task.escalated_at = now
                    task.status = 'overdue'
                    task.save()
                    
                    self.stdout.write(f"Task '{task.title}' escalated to L1 (Staff)")
                    # Notify assigned by, or staff
                    supervisor = task.assigned_by
                    if supervisor:
                        create_notification(
                            recipient=supervisor,
                            sender=None,
                            title=f"L1 Escalation: Overdue Task",
                            message=f"Task '{task.title}' assigned to {task.assigned_to.name} is overdue by {days_overdue} days.",
                            category="escalation"
                        )
                        
        # ----------------------------------------------------
        # 2. ESCALATE LEADS
        # ----------------------------------------------------
        # Leads in 'new' status for > 2 days -> L1
        # Leads in 'new' status for > 5 days -> L2
        
        new_leads = Lead.objects.filter(status='new')
        
        for lead in new_leads:
            days_old = (now - lead.created_at).days
            
            # Check for L2 Escalation (5+ days)
            if days_old >= 5 and lead.escalation_level < 2:
                lead.escalation_level = 2
                lead.escalated_at = now
                lead.save()
                
                self.stdout.write(f"Lead '{lead.name}' escalated to L2 (Admin)")
                for admin in admins:
                    create_notification(
                        recipient=admin,
                        sender=None,
                        title=f"L2 Escalation: Unattended Lead",
                        message=f"Lead '{lead.name}' has been uncontacted for {days_old} days.",
                        category="escalation"
                    )
                    
            # Check for L1 Escalation (2-4 days)
            elif days_old >= 2 and lead.escalation_level < 1:
                lead.escalation_level = 1
                lead.escalated_at = now
                lead.save()
                
                self.stdout.write(f"Lead '{lead.name}' escalated to L1 (Staff)")
                for s in staff:
                    create_notification(
                        recipient=s,
                        sender=None,
                        title=f"L1 Escalation: Unattended Lead",
                        message=f"Lead '{lead.name}' has been uncontacted for {days_old} days. Please assign or follow up.",
                        category="escalation"
                    )

        self.stdout.write(self.style.SUCCESS('Successfully completed escalation check.'))
