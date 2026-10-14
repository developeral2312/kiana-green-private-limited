from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
from django.db import transaction
from datetime import date
from django.utils.http import urlencode

from users.utils import create_notification
from users.views import notify_admins_and_assigned
from users.models import Employee

from .models import *
from .forms import *


from projects.models import Task

def notify_lead_updates(lead, title, message, request):
    admins = CustomUser.objects.filter(role='admin')
    for admin in admins:
        if admin != request.user:
            create_notification(recipient=admin, title=title, message=message, link=reverse('view_lead', kwargs={'lid': lead.id}), category='crm', sender=request.user)
    
    if lead.assigned_to and lead.assigned_to != request.user:
        create_notification(recipient=lead.assigned_to, title=title, message=message, link=reverse('view_lead', kwargs={'lid': lead.id}), category='crm', sender=request.user)


@login_required(login_url='/users/login')
def review_list(request):
    review_list = Review.objects.all().order_by('-created_at')
    paginator = Paginator(review_list, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/admin/review_list.html', {'page_obj': page_obj})


@login_required(login_url='/users/login')
def delete_review(request, rid):
    review = Review.objects.get(id=rid)
    review.delete()

    admins = CustomUser.objects.filter(role='admin')

    for admin in admins:
        create_notification(
            recipient=admin,
            sender=request.user,
            title="Review Deleted",
            message=f"Review from {review.name} has been deleted",
            link=reverse('review'),
            category="crm"
        )

    return redirect(review_list)


@login_required(login_url='/users/login')
def reply_review(request, rid):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=rid)
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if review.email and subject and message:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [review.email],
                    fail_silently=False,
                )
                messages.success(request, f"Reply sent successfully to {review.email}")
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
        else:
            messages.error(request, "Missing required fields or reviewer email.")
            
    return redirect('review')



@login_required(login_url='/users/login')
def lead_list(request):
    status = request.GET.get('status')
    query = request.GET.get('q', '').strip()

    leads = Lead.objects.select_related(
        "assigned_to"
    ).prefetch_related(
        "followups",
        "site_visits"
    ).all()

    # Filter by user role
    if request.user.role != 'admin' and request.user.role == 'sales':
        leads = leads.filter(assigned_to=request.user)

    # Filter by status
    if status:
        leads = leads.filter(status=status)

    # Search query
    if query:
        leads = leads.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(assigned_to__username__icontains=query)
        )

    leads = leads.order_by('-created_at')

    # Pagination
    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preserve GET parameters for pagination links
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')
    querystring = params.urlencode()

    context = {
        'leads': page_obj,
        'page_obj': page_obj,
        'status_choices': Lead.STATUS_CHOICES,
        'status': status,
        'query': query,
        'querystring': querystring,  # pass to template
    }

    return render(request, 'dashboard/lead_list.html', context)


@login_required(login_url='/users/login')
def view_lead(request, lid):
    lead = get_object_or_404(Lead, id=lid)
    return render(request, 'dashboard/view_lead.html', {'lead': lead})


@login_required(login_url='/users/login')
def add_lead(request):
    if request.method == "POST":
        notes = request.POST.get('notes')
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.notes = notes

            if request.user.role != 'admin':
                lead.assigned_to = request.user

            lead.save()

            LeadActivity.objects.create(
                lead=lead,
                title="Lead Created",
                description=f"Lead added manually by {request.user.username}",
                created_by=request.user
            )
            notify_admins_and_assigned(
                sender=request.user,
                instance=lead,
                title="New Lead Added",
                message=f"{lead.name} has been added to CRM",
                link=reverse('view_lead', kwargs={'lid': lead.id}),
                admin_cat="crm",
                emp_cat="lead"
            )
            return redirect(lead_list)
    else: 
        form = LeadForm()
    return render(request,'dashboard/add_lead.html',{'form':form})


@login_required(login_url='/users/login')
def delete_lead(request, lid):
    lead = get_object_or_404(Lead, id=lid)
    lead.delete()

    create_notification(
        recipient=request.user,
        sender=request.user,
        title="Lead Deleted",
        message=f"{lead.name} has been removed from CRM",
        link=reverse('lead_list'),
        category="crm"
    )
    return redirect(lead_list)  

@login_required(login_url='/users/login')
def mark_followup_done(request, fid):

    followup = get_object_or_404(FollowUp, id=fid)
    lead = followup.lead

    followup.mark_done(user=request.user)

    # =====================================
    # ✅ AUTO COMPLETE TASK
    # =====================================
    task = Task.objects.filter(
        title=f"Follow-up - {lead.name} ({followup.scheduled_date})",
        assigned_to=lead.assigned_to,
        status__in=['new', 'in_progress']
    ).first()

    if task:
        task.status = 'completed'
        task.save()

        LeadActivity.objects.create(
            lead=lead,
            title="Task Auto Completed",
            description=f"Task '{task.title}' auto-completed after follow-up",
            created_by=request.user
        )

    # =====================================
    # ✅ ACTIVITY LOG
    # =====================================
    LeadActivity.objects.create(
        lead=lead,
        title="Follow-up Completed",
        description=f"Follow-up on {followup.scheduled_date} marked as done",
        created_by=request.user
    )

    return redirect(update_lead, lid=followup.lead.id)


@login_required(login_url='/users/login')
def mark_site_visit_done(request, vid):

    visit = get_object_or_404(SiteVisit, id=vid)
    lead = visit.lead
    
    visit.mark_done(user=request.user)

        # =====================================
    # ✅ AUTO COMPLETE RELATED TASK
    # =====================================
    task = Task.objects.filter(
        title=f"Site Visit - {lead.name} ({visit.scheduled_date})",
        assigned_to=visit.engineer,
        status__in=['new', 'in_progress']
    ).first()

    if task:
        task.status = 'completed'
        task.save()

        # 🟢 Activity log (task)
        LeadActivity.objects.create(
            lead=lead,
            title="Task Auto Completed",
            description=f"Task '{task.title}' auto-completed after site visit",
            created_by=request.user
        )

    # =====================================
    # ✅ ACTIVITY LOG (visit)
    # =====================================
    LeadActivity.objects.create(
        lead=lead,
        title="Site Visit Completed",
        description=f"Site visit on {visit.scheduled_date} marked as done",
        created_by=request.user
    )

    return redirect(update_lead, lid=visit.lead.id)



@login_required(login_url='/users/login')
def update_lead(request, lid):
    lead = Lead.objects.select_related(
        "assigned_to"
    ).prefetch_related(
        "followups",
        "site_visits",
        "activities"
    ).get(id=lid)

    activities = lead.activities.order_by('-created_at')

    lead_form = LeadUpdateForm(instance=lead)
    sitevisit_form = SiteVisitForm()
    followup_form = FollowUpForm()

    if request.method == "POST":

        form_type = request.POST.get("form_type")

        with transaction.atomic():

            # -------- LEAD UPDATE --------
            if form_type == "lead_update":

                old_status = lead.status
                old_priority = lead.priority
                old_assigned = lead.assigned_to

                lead_form = LeadUpdateForm(request.POST, instance=lead)

                if lead_form.is_valid():

                    lead = lead_form.save()

                    if old_status != lead.status:
                        LeadActivity.objects.create(
                            lead=lead,
                            title="Status Updated",
                            description=f"Status changed to {lead.get_status_display()}",
                            created_by=request.user
                        )
                        notify_lead_updates(lead, "Status Updated", f"{lead.name} status changed to {lead.get_status_display()}", request)

                    if old_priority != lead.priority:
                        LeadActivity.objects.create(
                            lead=lead,
                            title="Priority Updated",
                            description=f"Priority changed to {lead.get_priority_display()}",
                            created_by=request.user
                        )
                        notify_lead_updates(lead, "Priority Updated", f"{lead.name} priority changed to {lead.get_priority_display()}", request)

                    if old_assigned != lead.assigned_to:

                        assigned_name = lead.assigned_to.username if lead.assigned_to else "Unassigned"

                        LeadActivity.objects.create(
                            lead=lead,
                            title="Lead Assigned",
                            description=f"Assigned to {assigned_name}",
                            created_by=request.user
                        )
                        notify_lead_updates(lead, "Lead Assigned", f"{lead.name} assigned to {assigned_name}", request)

            # -------- SITE VISIT --------
            elif form_type == "site_visit":

                # 🚫 BLOCK if pending visit exists
                if lead.site_visits.filter(status__in=['scheduled', 'pending']).exists():
                    return redirect('update_lead', lid=lead.id)
                
                sitevisit_form = SiteVisitForm(request.POST)

                if sitevisit_form.is_valid():

                    visit = sitevisit_form.save(commit=False)
                    visit.lead = lead
                    visit.added_by = request.user
                    visit.save()

                    LeadActivity.objects.create(
                        lead=lead,
                        title="Site Visit Scheduled",
                        description=f"Site visit scheduled on {visit.scheduled_date}",
                        created_by=request.user
                    )


                    # CREATE TASK FOR ENGINEER
                    if visit.engineer:

                        if visit.engineer:

                            task, created = Task.objects.get_or_create(
                                title=f"Site Visit - {lead.name} ({visit.scheduled_date})",
                                assigned_to=visit.engineer,
                                due_date=visit.scheduled_date,
                                defaults={
                                    "description": f"Site visit for {lead.name} on {visit.scheduled_date}",
                                    "assigned_by": request.user
                                }
                            )

                    # NOTIFY ADMINS + ENGINEER
                    notify_admins_and_assigned(
                        sender=request.user,
                        instance=lead,
                        title="Site Visit Scheduled",
                        message=f"Site visit for {lead.name} scheduled on {visit.scheduled_date}",
                        link=reverse('update_lead', args=[lead.id]),
                        admin_cat="crm",
                        emp_cat="lead"
                    )

            # -------- FOLLOWUP --------
            elif form_type == "followup":

                # 🚫 BLOCK if pending follow-up exists
                if lead.followups.filter(status__in=['scheduled', 'pending']).exists():
                    return redirect('update_lead', lid=lead.id)
    
                followup_form = FollowUpForm(request.POST)

                if followup_form.is_valid():

                    followup = followup_form.save(commit=False)
                    followup.lead = lead
                    followup.added_by = request.user
                    followup.save()

                    LeadActivity.objects.create(
                        lead=lead,
                        title="Follow-up Scheduled",
                        description=f"Follow-up scheduled on {followup.scheduled_date}",
                        created_by=request.user
                    )

                    if lead.assigned_to:

                        task, created = Task.objects.get_or_create(
                            title=f"Follow-up - {lead.name} ({followup.scheduled_date})",
                            assigned_to=lead.assigned_to,
                            due_date=followup.scheduled_date,
                            defaults={
                                "description": f"Follow-up with {lead.name} on {followup.scheduled_date}",
                                "assigned_by": request.user
                            }
                        )

                    # NOTIFY ADMINS + ASSIGNED STAFF
                    notify_admins_and_assigned(
                        sender=request.user,
                        instance=lead,
                        title="Follow-up Scheduled",
                        message=f"Follow-up scheduled with {lead.name} on {followup.scheduled_date}",
                        link=reverse('update_lead', args=[lead.id]),
                        admin_cat="crm",
                        emp_cat="lead"
                    )

        return redirect('update_lead', lid=lead.id)

    pending_visit_exists = lead.site_visits.filter(status__in=['scheduled', 'pending']).exists()
    pending_followup_exists = lead.followups.filter(status__in=['scheduled', 'pending']).exists()

    context = {
        "lead": lead,
        "activities": activities,
        "lead_form": lead_form,
        "sitevisit_form": sitevisit_form,
        "followup_form": followup_form,
        "today": timezone.localdate(),
        "pending_visit_exists": pending_visit_exists,
        "pending_followup_exists": pending_followup_exists
    }

    return render(request, "dashboard/update_lead.html", context)



@login_required(login_url='/users/login')
def site_visits(request, filter=None):

    visits = SiteVisit.objects.filter(engineer=request.user)
    today = date.today()

    # Filters
    overdue = visits.filter(scheduled_date__lt=today, status='pending')
    todays = visits.filter(scheduled_date=today, status='pending')
    upcoming = visits.filter(scheduled_date__gt=today, status='pending')
    completed = visits.filter(status='done')

    # Flags
    show_overdue = False
    show_today = False
    show_upcoming = False
    show_completed = False

    # Manual filter
    if filter == 'overdue':
        show_overdue = True
    elif filter == 'today':
        show_today = True
    elif filter == 'upcoming':
        show_upcoming = True
    elif filter == 'completed':
        show_completed = True

    # Auto priority
    else:
        if overdue.exists():
            show_overdue = True
        elif todays.exists():
            show_today = True
        elif upcoming.exists():
            show_upcoming = True
        else:
            show_completed = True

    context = {
        'overdue': overdue,
        'todays': todays,
        'upcoming': upcoming,
        'completed': completed,
        'show_overdue': show_overdue,
        'show_today': show_today,
        'show_upcoming': show_upcoming,
        'show_completed': show_completed,
    }

    return render(request, 'dashboard/engineer/sitevisits.html', context)




@login_required(login_url='/users/login')
def edit_site_visit(request,vid):
    visit = SiteVisit.objects.get(id=vid)

    if request.method == 'POST':
        form = UpdateVisitForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()

            admins = CustomUser.objects.filter(role='admin')
            for admin in admins:
                create_notification(
                    recipient=admin,
                    title='Site Visit Updated',
                    message=f'Engineer {visit.engineer} updated the site visit for the lead {visit.lead}.\nScheduled Date : {visit.scheduled_date}\nStatus : {visit.status}',
                    sender=request.user,
                    link= reverse('lead_list'),
                    category='crm'
                )
            
            # Redirect to the appropriate tab (today/upcoming/completed)
            if visit.status == 'done':
                return redirect('site_visits', 'completed')
            elif visit.scheduled_date == timezone.localdate():
                return redirect('site_visits', 'today')
            else:
                return redirect('site_visits', 'upcoming')
    else:
        form = UpdateVisitForm(instance=visit)



    context = {
        'form': form,
        'visit': visit
    }
    return render(request, 'dashboard/engineer/edit_visit.html', context)



@login_required(login_url='/users/login')
def upload_site_photos_page(request):
    visits = SiteVisit.objects.filter(engineer=request.user)

    if request.method == 'POST':
        form = SitePhotoForm(request.POST, request.FILES)
        form.fields['visit'].queryset = visits  # limit to engineer’s visits
        if form.is_valid():
            form.save()  # ModelForm handles saving the single file
            return redirect('upload_site_photos')
    else:
        form = SitePhotoForm()
        form.fields['visit'].queryset = visits

    return render(request, 'dashboard/engineer/upload_photos_page.html', {'form': form, 'visits': visits})


@login_required(login_url='/users/login')
def follow_ups(request, filter=None):
    followups = FollowUp.objects.filter(lead__assigned_to=request.user)
    today = timezone.localdate()

    overdue = followups.filter(status='pending', scheduled_date__lt=today)
    todays = followups.filter(status='pending', scheduled_date=today)
    upcoming = followups.filter(status='pending', scheduled_date__gt=today)
    completed = followups.filter(status='done')

    # Tab logic
    show_today = filter in (None, 'today')
    show_upcoming = filter == 'upcoming'
    show_completed = filter == 'completed'
    show_overdue = filter == 'overdue'

    context = {
        'overdue': overdue,
        'todays': todays,
        'upcoming': upcoming,
        'completed': completed,
        'show_today': show_today,
        'show_upcoming': show_upcoming,
        'show_completed': show_completed,
        'show_overdue': show_overdue,
    }
    return render(request, 'dashboard/sales/followups.html', context)


@login_required(login_url='/users/login')
def edit_followup(request, fid):
    followup = get_object_or_404(FollowUp, id=fid)

    if request.method == "POST":
        form = FollowUpForm(request.POST, instance=followup)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.added_by = request.user  # track who edited
            followup.save()

            # Log activity
            LeadActivity.objects.create(
                lead=followup.lead,
                title="Follow-up Updated",
                description=f"Follow-up on {followup.scheduled_date} updated by {request.user.username}",
                created_by=request.user
            )

            messages.success(request, "Follow-up updated successfully.")
            return redirect('update_lead', lid=followup.lead.id)
    else:
        form = FollowUpForm(instance=followup)

    context = {
        'form': form,
        'followup': followup,
    }
    return render(request, 'dashboard/sales/edit_followup.html', context)




from django.http import JsonResponse
from django.db.models import Q
from projects.models import Project
from finance.models import Invoice

def universal_search(request):
    """ Enterprise Universal Search """
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({"results": []})
        
    results = []
    
    # 1. Search Leads
    leads = Lead.objects.filter(Q(phone__icontains=q) | Q(name__icontains=q) | Q(email__icontains=q))[:5]
    for l in leads:
        results.append({"type": "Lead (Customer 360)", "title": l.name, "subtitle": l.phone, "url": f"/crm/customer-360/{l.phone}/"})
        
    # 2. Search Projects
    projects = Project.objects.filter(Q(project_id__icontains=q) | Q(title__icontains=q))[:5]
    for p in projects:
        results.append({"type": "Project", "title": p.project_id or p.title, "subtitle": p.get_status_display(), "url": f"/projects/{p.id}/"})
        
    # 3. Search Invoices
    invoices = Invoice.objects.filter(invoice_number__icontains=q)[:5]
    for i in invoices:
        results.append({"type": "Invoice", "title": i.invoice_number, "subtitle": f"₹{i.total_amount}", "url": f"/finance/invoice/{i.id}/"})
        
    return JsonResponse({"results": results})

@login_required(login_url='/users/login')
def customer_360(request, phone):
    """ Customer 360 Degree View """
    if request.user.role not in ['admin', 'sales', 'manager']:
        messages.error(request, "You do not have permission to view Customer 360.")
        return redirect('dashboard')
        
    leads = Lead.objects.filter(phone=phone).prefetch_related('activities', 'followups')
    projects = Project.objects.filter(lead__phone=phone)
    invoices = Invoice.objects.filter(project__in=projects)
    
    main_lead = leads.first()
    
    context = {
        "phone": phone,
        "main_lead": main_lead,
        "leads": leads,
        "projects": projects,
        "invoices": invoices,
        "revenue_value": sum(i.total_amount for i in invoices if i.status == 'paid')
    }
    return render(request, 'crm/customer_360.html', context)


# ===============================
# FEATURE 20: REFERRAL ENGINE
# ===============================

@login_required(login_url='/users/login')
def referral_list(request):
    referrals = Referral.objects.all().order_by('-created_at')
    
    # Auto-update status based on Lead status
    for ref in referrals:
        if ref.status == 'pending' and ref.referred_lead and ref.referred_lead.status == 'converted':
            ref.status = 'converted'
            ref.save()
            
    context = {
        'referrals': referrals
    }
    return render(request, 'dashboard/crm/referral_list.html', context)

@login_required(login_url='/users/login')
def mark_referral_paid(request, ref_id):
    ref = get_object_or_404(Referral, id=ref_id)
    if ref.status == 'converted':
        ref.status = 'paid'
        # Assume a fixed commission for now if not set
        if ref.commission_amount == 0:
            ref.commission_amount = 5000.00
        ref.save()
        messages.success(request, f"Commission of Rs. {ref.commission_amount} marked as paid to {ref.referrer_name}")
    return redirect('referral_list')


# ===============================
# FEATURE 18: ESCALATION MATRIX
# ===============================
from datetime import timedelta

@login_required(login_url='/users/login')
def escalation_dashboard(request):
    """
    Shows Leads and Tasks that have breached Turnaround Time (TAT) and highlights them.
    TAT Rule: 
    - Lead in 'new' for > 2 days -> L1 Escalated
    - Lead in 'contacted' for > 7 days -> L2 Escalated
    """
    now = timezone.now()
    
    # Analyze Leads
    leads = Lead.objects.all()
    escalated_leads = []
    
    for lead in leads:
        days_since_update = (now - lead.updated_at).days
        breached = False
        level = 0
        
        if lead.status == 'new' and days_since_update > 2:
            breached = True
            level = 1
        elif lead.status == 'contacted' and days_since_update > 7:
            breached = True
            level = 2
        elif lead.status == 'site_visit_scheduled' and days_since_update > 10:
            breached = True
            level = 3
            
        if breached:
            # Auto escalate in DB if not already
            if lead.escalation_level < level:
                lead.escalation_level = level
                lead.escalated_at = now
                lead.save(update_fields=['escalation_level', 'escalated_at'])
                
            escalated_leads.append(lead)
            
    # Sort by escalation level descending
    escalated_leads.sort(key=lambda x: x.escalation_level, reverse=True)
            
    context = {
        'escalated_leads': escalated_leads,
    }
    return render(request, 'dashboard/crm/escalation_dashboard.html', context)
