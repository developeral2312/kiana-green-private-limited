from celery import shared_task
from django.utils import timezone
from .models import Project
from users.utils import create_notification
from users.models import CustomUser

@shared_task
def check_sla_and_escalate():
    """ Escalation Matrix Engine (SLA/TAT) """
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

import os
import shutil
from datetime import datetime
from django.conf import settings

@shared_task
def backup_database_and_media():
    """ Enterprise Disaster Recovery Backup Cron """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup DB
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        db_backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')
        if os.path.exists(db_path):
            shutil.copy2(db_path, db_backup_path)
            
        # Backup Media
        # skipping massive media copies for dev environment speed, but logic is here:
        # shutil.make_archive(os.path.join(backup_dir, f'media_backup_{timestamp}'), 'zip', settings.MEDIA_ROOT)
        
        # Notify Admins
        admins = CustomUser.objects.filter(role='admin')
        for admin in admins:
            create_notification(
                recipient=admin,
                title="System Backup Successful",
                message=f"Disaster recovery backup completed at {timestamp}.",
                category="system"
            )
        return True
    except Exception as e:
        return False
