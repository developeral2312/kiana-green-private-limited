with open('crm/views.py', 'a', encoding='utf-8') as f:
    f.write('''

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
''')
print("Appended CRM views")
