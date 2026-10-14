from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from crm.models import Lead
from users.models import CustomUser, Notification
import logging

logger = logging.getLogger(__name__)

@shared_task
def auto_escalate_leads():
    """
    Escalation Matrix (Auto-TAT):
    - Escalate to L1 (Manager) if a lead hasn't been followed up in 3 days.
    - Escalate to L2 (Director/Admin) if a lead hasn't been followed up in 5 days.
    """
    today = now()
    three_days_ago = today - timedelta(days=3)
    five_days_ago = today - timedelta(days=5)

    # Get active leads that are not rejected or converted
    active_leads = Lead.objects.exclude(status__in=['converted', 'rejected'])

    escalated_count = 0

    for lead in active_leads:
        last_followup = lead.followups.order_by('-created_at').first()
        last_action_date = last_followup.created_at if last_followup else lead.created_at
        
        days_inactive = (today - last_action_date).days

        # Level 2 Escalation (5+ Days Inactive)
        if days_inactive >= 5 and lead.escalation_level < 2:
            lead.escalation_level = 2
            lead.escalated_at = today
            lead.save()
            escalated_count += 1
            
            # Notify Directors
            directors = CustomUser.objects.filter(role='admin')
            for director in directors:
                Notification.objects.create(
                    recipient=director,
                    title="L2 Escalation: Lead Overdue",
                    message=f"Lead '{lead.name}' has been inactive for {days_inactive} days. Immediate attention required.",
                    category="escalation",
                    link=f"/crm/leads/{lead.id}/"
                )
            logger.info(f"Escalated Lead {lead.id} to L2 (Director).")

        # Level 1 Escalation (3+ Days Inactive)
        elif days_inactive >= 3 and days_inactive < 5 and lead.escalation_level < 1:
            lead.escalation_level = 1
            lead.escalated_at = today
            lead.save()
            escalated_count += 1

            # Notify Managers
            managers = CustomUser.objects.filter(role='manager')
            for manager in managers:
                Notification.objects.create(
                    recipient=manager,
                    title="L1 Escalation: Lead Pending",
                    message=f"Lead '{lead.name}' assigned to {lead.assigned_to.username if lead.assigned_to else 'None'} has no follow-up for {days_inactive} days.",
                    category="escalation",
                    link=f"/crm/leads/{lead.id}/"
                )
            logger.info(f"Escalated Lead {lead.id} to L1 (Manager).")

    return f"Escalation task completed. {escalated_count} leads escalated."
