from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

import secrets
import string




def create_notification(recipient, title, message, sender=None, link=None, category="system"):
    msg = message or title or ""
    cat = category or "system"

    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        title=title,
        message=msg,
        link=link,
        category=cat
    )
    
    # Check if this is an important notification that warrants an email
    important_categories = [
        'task', 'assignment', 'alert', 'escalation', 'approval', 'important',
        'employee', 'crm', 'lead', 'finance', 'payment', 'invoice',
        'procurement', 'project', 'service', 'partner', 'system'
    ]
    important_keywords = ['assigned', 'escalation', 'urgent', 'approved', 'rejected', 'payment', 'created', 'new', 'welcome', 'status']
    
    is_important = cat in important_categories
    if not is_important:
        text_to_check = f"{title} {msg}".lower()
        if any(keyword in text_to_check for keyword in important_keywords):
            is_important = True
            
    if is_important and recipient and recipient.email:
        try:
            full_name = recipient.get_full_name() or recipient.username
            email_body = f"Hello {full_name},\n\n{msg}\n\n"
            if link:
                full_url = f"http://127.0.0.1:8000{link}" if link.startswith('/') else link
                email_body += f"View Details in ERP: {full_url}\n\n"
            email_body += "Regards,\nKiana Green Private Limited ERP Team"
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'sajmiya@gmail.com')
            send_mail(
                subject=f"Kiana Green Alert: {title}",
                message=email_body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {recipient.email}: {str(e)}")




def generate_temp_password():
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))