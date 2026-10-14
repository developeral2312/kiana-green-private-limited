from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Partner, PartnerLead, PartnerStock
from django.contrib import messages

@login_required
def partner_list(request):
    q = request.GET.get('q', '').strip()
    partner_type = request.GET.get('type', '').strip()

    partners = Partner.objects.prefetch_related('leads', 'stocks').all()

    if q:
        partners = partners.filter(
            Q(name__icontains=q) |
            Q(contact_person__icontains=q) |
            Q(phone__icontains=q) |
            Q(address__icontains=q) |
            Q(email__icontains=q)
        )

    if partner_type in ['franchise', 'dealer']:
        partners = partners.filter(partner_type=partner_type)

    partners = partners.order_by('-created_at')

    total_count = Partner.objects.count()
    franchise_count = Partner.objects.filter(partner_type='franchise').count()
    dealer_count = Partner.objects.filter(partner_type='dealer').count()
    total_leads = PartnerLead.objects.count()

    context = {
        'partners': partners,
        'q': q,
        'partner_type': partner_type,
        'total_count': total_count,
        'franchise_count': franchise_count,
        'dealer_count': dealer_count,
        'total_leads': total_leads,
    }
    return render(request, 'partners/partner_list.html', context)

@login_required
def all_partner_leads(request):
    status_filter = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    leads = PartnerLead.objects.select_related('partner').all()

    if status_filter:
        leads = leads.filter(status=status_filter)

    if q:
        leads = leads.filter(
            Q(customer_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(partner__name__icontains=q)
        )

    leads = leads.order_by('-created_at')
    partners = Partner.objects.all().order_by('name')

    context = {
        'leads': leads,
        'partners': partners,
        'status_filter': status_filter,
        'q': q,
    }
    return render(request, 'partners/all_partner_leads.html', context)

@login_required
def add_global_lead(request):
    if request.method == 'POST':
        partner_id = request.POST.get('partner_id')
        customer_name = request.POST.get('customer_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        status = request.POST.get('status', 'new').strip()
        notes = request.POST.get('notes', '').strip()

        if not partner_id or not customer_name or not phone:
            messages.error(request, 'Please provide Partner, Customer Name, and Phone.')
            return redirect('all_partner_leads')

        partner = get_object_or_404(Partner, id=partner_id)
        PartnerLead.objects.create(
            partner=partner,
            customer_name=customer_name,
            phone=phone,
            email=email if email else None,
            status=status if status in ['new', 'contacted', 'converted', 'lost'] else 'new',
            notes=notes
        )
        messages.success(request, f'Franchise lead for "{customer_name}" added successfully.')

    return redirect('all_partner_leads')

@login_required
def update_partner_lead(request, lead_id):
    lead = get_object_or_404(PartnerLead, id=lead_id)
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        status = request.POST.get('status', '').strip()
        notes = request.POST.get('notes', '').strip()
        partner_id = request.POST.get('partner_id')

        if customer_name:
            lead.customer_name = customer_name
        if phone:
            lead.phone = phone
        lead.email = email if email else None
        if status in ['new', 'contacted', 'converted', 'lost']:
            lead.status = status
        lead.notes = notes

        if partner_id:
            lead.partner_id = partner_id

        lead.save()
        messages.success(request, f'Lead "{lead.customer_name}" updated successfully.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('all_partner_leads')

@login_required
def delete_partner_lead(request, lead_id):
    lead = get_object_or_404(PartnerLead, id=lead_id)
    if request.method == 'POST':
        name = lead.customer_name
        lead.delete()
        messages.success(request, f'Lead "{name}" deleted successfully.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('all_partner_leads')

@login_required
def all_dealer_stocks(request):
    stocks = PartnerStock.objects.select_related('partner', 'material').all().order_by('-last_updated')
    return render(request, 'partners/all_dealer_stocks.html', {'stocks': stocks})

@login_required
def add_partner(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        partner_type = request.POST.get('partner_type')
        contact_person = request.POST.get('contact_person')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        commission_rate = request.POST.get('commission_rate', 0)

        Partner.objects.create(
            name=name,
            partner_type=partner_type,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            commission_rate=commission_rate
        )
        messages.success(request, 'Partner added successfully.')
        return redirect('partner_list')
    
    return render(request, 'partners/add_partner.html')

@login_required
def partner_detail(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    materials = __import__('procurement.models').models.Material.objects.all()
    crm_leads = __import__('crm.models').models.Lead.objects.exclude(status='converted')
    return render(request, 'partners/partner_detail.html', {'partner': partner, 'materials': materials, 'crm_leads': crm_leads})

@login_required
def add_partner_lead(request, pk):
    if request.method == 'POST':
        partner = get_object_or_404(Partner, pk=pk)
        
        crm_lead_id = request.POST.get('crm_lead_id')
        if crm_lead_id:
            # Assigning an existing CRM Lead
            crm_lead = __import__('crm.models').models.Lead.objects.get(id=crm_lead_id)
            PartnerLead.objects.create(
                partner=partner,
                customer_name=crm_lead.name,
                phone=crm_lead.phone,
                email=crm_lead.email,
                notes=f"Assigned from CRM: {crm_lead.service} - {crm_lead.notes or ''}"
            )
            messages.success(request, 'CRM Lead successfully assigned to Franchise.')
        else:
            # Manual Entry
            customer_name = request.POST.get('customer_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email', '')
            notes = request.POST.get('notes', '')
            
            PartnerLead.objects.create(
                partner=partner,
                customer_name=customer_name,
                phone=phone,
                email=email,
                notes=notes
            )
            messages.success(request, 'Lead added successfully.')
        
    return redirect('partner_detail', pk=pk)

@login_required
def update_partner_stock(request, pk):
    if request.method == 'POST':
        partner = get_object_or_404(Partner, pk=pk)
        material_id = request.POST.get('material_id')
        quantity = request.POST.get('quantity')
        
        if material_id and quantity:
            stock, created = PartnerStock.objects.get_or_create(
                partner=partner,
                material_id=material_id,
                defaults={'quantity': 0}
            )
            # Update quantity (adding or replacing depending on logic, let's just set it)
            stock.quantity = int(quantity)
            stock.save()
            messages.success(request, 'Stock updated successfully.')
            
    return redirect('partner_detail', pk=pk)

# ===============================
# PARTNER PORTAL VIEWS (EXTERNAL)
# ===============================

@login_required(login_url="/users/login")
def partner_portal_dashboard(request):
    if request.user.role != 'partner':
        return redirect('dashboard')
        
    try:
        partner = request.user.partner_profile
    except:
        messages.error(request, 'Your user account is not linked to a Partner profile.')
        return redirect('login')

    leads = partner.leads.all().order_by('-created_at')
    context = {
        'partner': partner,
        'leads': leads,
        'total_leads': leads.count(),
        'converted_leads': leads.filter(status='converted').count()
    }
    return render(request, 'partners/portal/dashboard.html', context)


@login_required(login_url="/users/login")
def partner_portal_add_lead(request):
    if request.user.role != 'partner':
        return redirect('dashboard')
        
    try:
        partner = request.user.partner_profile
    except:
        return redirect('login')
        
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        notes = request.POST.get('notes')
        
        # 1. Create Partner Lead (for partner tracking)
        PartnerLead.objects.create(
            partner=partner,
            customer_name=customer_name,
            phone=phone,
            email=email,
            notes=notes
        )
        
        # 2. Directly insert into Main CRM system for sales team!
        from crm.models import Lead
        Lead.objects.create(
            name=customer_name,
            phone=phone,
            email=email,
            notes=f"Lead submitted by Partner: {partner.name}\n" + notes,
            service='ongrid', # Default
            status='new'
        )
        
        messages.success(request, 'Lead successfully submitted to Zyphora CRM!')
        return redirect('partner_portal_dashboard')
        
    return render(request, 'partners/portal/add_lead.html')
