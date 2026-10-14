import os
import re
import json
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.db.models import Sum, Q, Count
from django.conf import settings

from projects.models import Project, Task
from crm.models import Lead
from finance.models import Invoice, Payment, ExpenseReport, ExpenseItem
from procurement.models import Material, Stock, PurchaseOrder, Vendor, RequestForQuotation, PurchaseOrderItem
from users.models import CustomUser, Employee

# LangChain & LangGraph imports (safe/conditional)
try:
    from langchain_core.tools import tool
    from langchain_groq import ChatGroq
    from langgraph.prebuilt import create_react_agent
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    def tool(f):
        return f


# ==============================================================================
# 1. SOLAR ENGINEERING & PM SURYA GHAR SUBSIDY CALCULATOR
# ==============================================================================
def calculate_solar_specs_and_subsidy(system_kw: float = 3.0, roof_sqft: float = 0.0) -> str:
    """
    Calculates technical specifications, power generation estimates, shadow-free roof area,
    and Central Government PM Surya Ghar Muft Bijli Yojana subsidy for solar rooftop plants.
    """
    try:
        kw = float(system_kw)
    except (ValueError, TypeError):
        kw = 3.0
        
    if kw <= 0:
        return "<div class='ai-answer'><i class='bi bi-exclamation-triangle-fill text-warning me-1'></i> System capacity 0 kW se jyada honi chahiye.</div>"
        
    # PM Surya Ghar Muft Bijli Yojana Subsidy Rules (2024-2026):
    # - 1 kW: Rs. 30,000
    # - 2 kW: Rs. 60,000 (Rs. 30,000/kW for first 2 kW)
    # - 3 kW to 10 kW (Residential): Flat Rs. 78,000 maximum central subsidy
    if kw < 1.0:
        subsidy = round(kw * 30000)
    elif kw < 2.0:
        subsidy = 30000 + round((kw - 1.0) * 30000)
    elif kw < 3.0:
        subsidy = 60000 + round((kw - 2.0) * 18000)
    else:
        subsidy = 78000  # Capped at Rs. 78,000 for residential under PM Surya Ghar
        
    # Estimated benchmark turnkey cost (Panels, Inverter, GI Structure, AC/DC Protection, Net Metering & Work)
    gross_cost_min = round(kw * 58000)
    gross_cost_max = round(kw * 68000)
    net_cost_min = max(0, gross_cost_min - subsidy)
    net_cost_max = max(0, gross_cost_max - subsidy)
    
    # Power generation specs (Average 4.3 units/day/kW in India)
    daily_units_min = round(kw * 4.0, 1)
    daily_units_max = round(kw * 4.6, 1)
    monthly_units_min = round(daily_units_min * 30)
    monthly_units_max = round(daily_units_max * 30)
    annual_units = round(kw * 1550)
    
    # Financial savings (Average domestic grid tariff Rs. 7.50 / unit)
    tariff = 7.50
    monthly_savings_min = round(monthly_units_min * tariff)
    monthly_savings_max = round(monthly_units_max * tariff)
    annual_savings = round(annual_units * tariff)
    
    # Payback period calculation
    avg_net_cost = (net_cost_min + net_cost_max) / 2
    payback_years = round(avg_net_cost / max(1, annual_savings), 1) if annual_savings > 0 else 3.2
    
    # Space feasibility (80 to 100 sq.ft shadow-free area per kW)
    req_roof_min = round(kw * 80)
    req_roof_max = round(kw * 100)
    
    # Approximate panel count (assuming ~540W Mono PERC panels)
    panel_count = max(1, round((kw * 1000) / 540))
    inv_kw = round(kw, 1)
    
    roof_msg = ""
    if roof_sqft > 0:
        if roof_sqft >= req_roof_min:
            roof_msg = f"<div class='alert alert-success py-1 px-2 my-2 small'><i class='bi bi-check-circle-fill me-1'></i> Available roof <strong>{roof_sqft:.0f} sq.ft</strong> is sufficient for {kw:.1f} kW (Required: {req_roof_min}-{req_roof_max} sq.ft).</div>"
        else:
            max_kw = round(roof_sqft / 90, 1)
            roof_msg = f"<div class='alert alert-warning py-1 px-2 my-2 small'><i class='bi bi-exclamation-triangle-fill me-1'></i> Chhat ka area (<strong>{roof_sqft:.0f} sq.ft</strong>) {kw:.1f} kW ke liye thoda kam hai. Isme lagbhag <strong>{max_kw} kW</strong> system fit ho sakta hai.</div>"

    html = (
        f"<div class='ai-answer'>"
        f"<div class='d-flex align-items-center justify-content-between mb-2 pb-1 border-bottom'>"
        f"<strong class='text-primary fs-6'><i class='bi bi-sun-fill text-warning me-1'></i> PM Surya Ghar Feasibility ({kw:.1f} kW Rooftop)</strong>"
        f"<span class='badge bg-success-subtle text-success border border-success-subtle'>Central Subsidy</span>"
        f"</div>"
        f"{roof_msg}"
        f"<div class='p-2 rounded-3 bg-light border mb-2'>"
        f"<div class='row g-2 text-center'>"
        f"<div class='col-6 border-end'><small class='text-muted d-block'>PM Surya Ghar Subsidy</small><strong class='text-success fs-5'>&#8377;{subsidy:,}</strong></div>"
        f"<div class='col-6'><small class='text-muted d-block'>Customer Net Cost</small><strong class='text-primary fs-5'>&#8377;{net_cost_min:,} - {net_cost_max:,}</strong></div>"
        f"</div>"
        f"</div>"
        f"<ul class='list-unstyled mb-2 small' style='line-height: 1.6;'>"
        f"<li><i class='bi bi-currency-rupee text-muted me-1'></i><strong>Gross Turnkey Cost:</strong> &#8377;{gross_cost_min:,} - &#8377;{gross_cost_max:,} (Panels, Inverter, Structure, Installation)</li>"
        f"<li><i class='bi bi-lightning-charge-fill text-warning me-1'></i><strong>Power Generation:</strong> ~{daily_units_min} to {daily_units_max} Units/day (~{monthly_units_min} - {monthly_units_max} Units/month)</li>"
        f"<li><i class='bi bi-piggy-bank-fill text-success me-1'></i><strong>Estimated Bill Savings:</strong> ~&#8377;{monthly_savings_min:,} to &#8377;{monthly_savings_max:,} / month (~&#8377;{annual_savings:,} / year)</li>"
        f"<li><i class='bi bi-hourglass-split text-info me-1'></i><strong>ROI / Payback Period:</strong> ~{payback_years} Years (Next 20+ years electricity is free!)</li>"
        f"<li><i class='bi bi-house-door-fill text-secondary me-1'></i><strong>Required Shadow-Free Roof:</strong> ~{req_roof_min} to {req_roof_max} sq. ft.</li>"
        f"<li><i class='bi bi-tools text-primary me-1'></i><strong>Recommended Hardware:</strong> ~{panel_count}x 540W Mono-PERC Panels + {inv_kw} kW Grid-Tie Inverter</li>"
        f"</ul>"
        f"<small class='text-muted'><i class='bi bi-info-circle me-1'></i>Subsidy directly customer ke Aadhaar-linked bank account me transfer hoti hai.</small>"
        f"</div>"
    )
    return html


# ==============================================================================
# 2. SPECIFIC PROJECT SEARCH
# ==============================================================================
def search_project(query: str) -> str:
    """Search for projects by Project ID, title, customer name, or location."""
    q_clean = query.strip()
    if not q_clean:
        return "Please specify a project ID or name to search."
        
    projects = Project.objects.filter(
        Q(project_id__icontains=q_clean) |
        Q(title__icontains=q_clean) |
        Q(lead__name__icontains=q_clean) |
        Q(location__icontains=q_clean)
    ).distinct()
    
    if not projects.exists() and q_clean.isdigit():
        projects = Project.objects.filter(id=int(q_clean))
        
    if not projects.exists():
        return f"<div class='ai-answer'><i class='bi bi-search text-muted me-1'></i> <em>'{q_clean}'</em> se milta julta koi project nahi mila. Type <strong>'projects'</strong> to see all.</div>"
        
    html = f"<div class='ai-answer'><div class='fw-semibold text-primary mb-2'><i class='bi bi-folder-check me-1'></i> {projects.count()} Matching Project(s) mile:</div>"
    today = now().date()
    
    for p in projects[:5]:
        client_name = p.lead.name if p.lead else 'Direct Customer'
        client_phone = p.lead.phone if p.lead else 'N/A'
        engineer_name = p.engineer.user.get_full_name() if (p.engineer and p.engineer.user) else (p.engineer.user.username if p.engineer else 'Unassigned')
        
        # Delay calculation
        if p.end_date:
            if p.end_date < today and p.status != 'completed':
                delay_days = (today - p.end_date).days
                time_badge = f"<span class='badge bg-danger-subtle text-danger border border-danger-subtle'>Delayed by {delay_days} days (Due: {p.end_date})</span>"
            else:
                time_badge = f"<span class='badge bg-secondary-subtle text-secondary'>Due: {p.end_date}</span>"
        else:
            time_badge = "<span class='badge bg-light text-muted border'>No due date</span>"
            
        # Financial billing for this project
        invoices = p.invoices.all()
        total_billed = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        paid_amount = Payment.objects.filter(invoice__in=invoices).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        balance_due = max(Decimal('0.00'), total_billed - paid_amount)
        
        html += (
            f"<div class='p-2 mb-2 rounded-2 bg-light border'>"
            f"<div class='d-flex justify-content-between align-items-start'>"
            f"<div><strong>{p.title}</strong> <small class='text-muted'>({p.project_id or f'ID: {p.id}'})</small></div>"
            f"<span class='badge bg-primary'>{p.get_status_display()}</span>"
            f"</div>"
            f"<div class='small mt-1 text-secondary'>"
            f"<div><i class='bi bi-person text-primary me-1'></i><strong>Customer:</strong> {client_name} ({client_phone}) | <i class='bi bi-geo-alt text-danger me-1'></i>{p.location or 'N/A'}</div>"
            f"<div><i class='bi bi-wrench text-secondary me-1'></i><strong>Engineer:</strong> {engineer_name} | <strong>Type:</strong> {p.get_project_type_display()}</div>"
            f"<div class='mt-1'>{time_badge}</div>"
            f"<div class='mt-1 text-dark'><i class='bi bi-cash text-success me-1'></i><strong>Billing:</strong> Invoiced: &#8377;{total_billed:,.2f} | Paid: <span class='text-success'>&#8377;{paid_amount:,.2f}</span> | Due: <span class='text-danger'>&#8377;{balance_due:,.2f}</span></div>"
            f"</div>"
            f"</div>"
        )
    html += "</div>"
    return html


# ==============================================================================
# 3. SPECIFIC LEAD / CUSTOMER SEARCH
# ==============================================================================
def search_lead_or_customer(query: str) -> str:
    """Search for CRM leads and customers by name, phone number, email, or location."""
    q_clean = query.strip()
    if not q_clean:
        return "Please specify a customer name or phone to search."
        
    leads = Lead.objects.filter(
        Q(name__icontains=q_clean) |
        Q(phone__icontains=q_clean) |
        Q(email__icontains=q_clean) |
        Q(location__icontains=q_clean)
    ).distinct().order_by('-created_at')
    
    if not leads.exists():
        return f"<div class='ai-answer'><i class='bi bi-search text-muted me-1'></i> <em>'{q_clean}'</em> naam ya number se koi lead nahi mili.</div>"
        
    html = f"<div class='ai-answer'><div class='fw-semibold text-success mb-2'><i class='bi bi-people-fill me-1'></i> {leads.count()} Matching Lead(s) mile:</div>"
    for l in leads[:5]:
        status_color = "success" if l.status == 'converted' else ("warning" if l.status == 'new' else "primary")
        score_badge = f"<span class='badge bg-success-subtle text-success border border-success-subtle'>Score: {l.score or 0}/100</span>"
        assigned = l.assigned_to.get_full_name() or l.assigned_to.username if l.assigned_to else "Unassigned"
        
        html += (
            f"<div class='p-2 mb-2 rounded-2 bg-light border small'>"
            f"<div class='d-flex justify-content-between align-items-start'>"
            f"<div><strong>{l.name}</strong> <span class='badge bg-{status_color} ms-1'>{l.get_status_display()}</span></div>"
            f"{score_badge}"
            f"</div>"
            f"<div class='mt-1 text-secondary'>"
            f"<div><i class='bi bi-telephone text-primary me-1'></i>{l.phone} {f'| <i class=\"bi bi-envelope text-muted me-1\"></i>' + l.email if l.email else ''}</div>"
            f"<div><i class='bi bi-geo-alt text-danger me-1'></i>{l.location or 'Location N/A'} | <strong>Service:</strong> {l.get_service_display()}</div>"
            f"<div><i class='bi bi-person-check text-info me-1'></i><strong>Assigned:</strong> {assigned} | <strong>Priority:</strong> {l.get_priority_display()}</div>"
            f"</div>"
            f"</div>"
        )
    html += "</div>"
    return html


# ==============================================================================
# 4. MATERIAL & GODOWN STOCK SEARCH
# ==============================================================================
def check_material_stock(material_query: str = "") -> str:
    """Checks stock quantity and reorder levels for solar panels, inverters, cables, and other inventory."""
    q_clean = material_query.strip()
    
    stocks = Stock.objects.select_related('material').all()
    if q_clean and q_clean.lower() not in ['stock', 'inventory', 'all']:
        stocks = stocks.filter(
            Q(material__name__icontains=q_clean) |
            Q(material__brand__icontains=q_clean) |
            Q(material__category__icontains=q_clean) |
            Q(material__description__icontains=q_clean)
        )
        
    if not stocks.exists():
        return f"<div class='ai-answer'><i class='bi bi-boxes text-muted me-1'></i> <em>'{q_clean}'</em> se related koi material nahi mila godown me.</div>"
        
    html = f"<div class='ai-answer'><div class='fw-semibold text-info mb-2'><i class='bi bi-boxes me-1'></i> Warehouse Inventory ({stocks.count()} items):</div>"
    for s in stocks.order_by('quantity')[:8]:
        mat = s.material
        is_low = s.quantity <= (mat.minimum_stock or 5)
        stock_badge = f"<span class='badge bg-danger'>Low Stock: {s.quantity} {mat.unit}</span>" if is_low else f"<span class='badge bg-success'>{s.quantity} {mat.unit}</span>"
        price_info = f"&#8377;{mat.unit_price:,.2f}/{mat.unit}" if mat.unit_price else "Price N/A"
        
        html += (
            f"<div class='p-2 mb-2 rounded-2 bg-light border small'>"
            f"<div class='d-flex justify-content-between align-items-center'>"
            f"<div><strong>{mat.name}</strong> {f'<span class=\"badge bg-secondary-subtle text-secondary ms-1\">{mat.brand}</span>' if mat.brand else ''}</div>"
            f"{stock_badge}"
            f"</div>"
            f"<div class='text-muted mt-1 d-flex justify-content-between'>"
            f"<span>Category: {mat.get_category_display() if hasattr(mat, 'get_category_display') else mat.category} | Min: {mat.minimum_stock} {mat.unit}</span>"
            f"<span><strong>{price_info}</strong></span>"
            f"</div>"
            f"</div>"
        )
    html += "</div>"
    return html


# ==============================================================================
# 5. FINANCIAL LEDGER & PROFITABILITY
# ==============================================================================
def get_financial_ledger_and_profit() -> str:
    """Calculates live company financials including total invoiced billing, payments collected, pending debt, approved expenses, and net profit."""
    total_invoiced = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    paid_invoices = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    pending_due = max(Decimal('0.00'), total_invoiced - paid_invoices)
    
    # Overdue count
    today = now().date()
    overdue_qs = Invoice.objects.filter(due_date__lt=today).exclude(status='paid')
    overdue_count = overdue_qs.count()
    overdue_amount = overdue_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Expenses (Approved expense items)
    approved_expenses = ExpenseItem.objects.filter(
        report__status='approved'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    all_expenses = ExpenseItem.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Net Profit estimate = Total Collections - Approved Project Expenses
    net_profit = paid_invoices - approved_expenses
    profit_margin = round((net_profit / paid_invoices) * 100, 1) if paid_invoices > 0 else 0.0
    profit_color = "success" if net_profit >= 0 else "danger"
    
    html = (
        f"<div class='ai-answer'>"
        f"<div class='fw-semibold text-success fs-6 mb-2 pb-1 border-bottom'><i class='bi bi-cash-coin me-1'></i> Zyphora Finance & Profit/Loss Ledger:</div>"
        f"<div class='p-2 rounded-3 bg-light border mb-2 text-center'>"
        f"<div class='row g-2'>"
        f"<div class='col-6 border-end'><small class='text-muted d-block'>Payments Collected</small><strong class='text-success fs-5'>&#8377;{paid_invoices:,.2f}</strong></div>"
        f"<div class='col-6'><small class='text-muted d-block'>Estimated Net Profit</small><strong class='text-{profit_color} fs-5'>&#8377;{net_profit:,.2f}</strong> ({profit_margin}%)</div>"
        f"</div>"
        f"</div>"
        f"<ul class='list-unstyled small mb-2' style='line-height: 1.6;'>"
        f"<li><i class='bi bi-receipt text-primary me-1'></i><strong>Total Invoiced Billing:</strong> &#8377;{total_invoiced:,.2f} ({Invoice.objects.count()} Invoices)</li>"
        f"<li><i class='bi bi-clock-history text-warning me-1'></i><strong>Customer Balance Due:</strong> &#8377;{pending_due:,.2f}</li>"
        f"<li><i class='bi bi-exclamation-circle text-danger me-1'></i><strong>Overdue Invoices:</strong> {overdue_count} Invoices (&#8377;{overdue_amount:,.2f})</li>"
        f"<li><i class='bi bi-credit-card text-secondary me-1'></i><strong>Approved Project Expenses:</strong> &#8377;{approved_expenses:,.2f} (Total logged: &#8377;{all_expenses:,.2f})</li>"
        f"</ul>"
        f"</div>"
    )
    return html


# ==============================================================================
# 6. VENDOR & PURCHASE ORDERS
# ==============================================================================
def search_vendor_or_po(query: str = "") -> str:
    """Searches vendors and purchase orders (PO) in procurement."""
    q_clean = query.strip()
    vendors = Vendor.objects.all()
    pos = PurchaseOrder.objects.select_related('vendor').all()
    
    if q_clean and q_clean.lower() not in ['vendor', 'vendors', 'po', 'procurement', 'purchase order']:
        vendors = vendors.filter(
            Q(name__icontains=q_clean) |
            Q(category__icontains=q_clean) |
            Q(contact_person__icontains=q_clean) |
            Q(phone__icontains=q_clean)
        )
        pos = pos.filter(
            Q(vendor__name__icontains=q_clean) |
            Q(id__icontains=q_clean)
        )
        
    html = f"<div class='ai-answer'><div class='fw-semibold text-secondary mb-2'><i class='bi bi-truck me-1'></i> Procurement & Vendors:</div>"
    
    if vendors.exists():
        html += f"<strong>Registered Vendors ({vendors.count()}):</strong><ul class='mt-1 ps-3 mb-2 small'>"
        for v in vendors[:4]:
            html += f"<li><strong>{v.name}</strong> ({v.category or 'General'}) - <i class='bi bi-telephone text-primary'></i> {v.phone} [Terms: {v.payment_terms or 'Credit'}]</li>"
        html += "</ul>"
        
    if pos.exists():
        html += f"<strong>Recent Purchase Orders ({pos.count()}):</strong><ul class='mt-1 ps-3 mb-0 small'>"
        for p in pos.order_by('-order_date')[:4]:
            badge = "<span class='badge bg-warning'>Pending</span>" if p.status == 'pending' else ("<span class='badge bg-success'>Received</span>" if p.status == 'received' else f"<span class='badge bg-secondary'>{p.status}</span>")
            html += f"<li>PO #{p.id} - <strong>{p.vendor.name}</strong>: &#8377;{p.total_amount:,.2f} {badge} (Delivery: {p.expected_delivery or 'N/A'})</li>"
        html += "</ul>"
        
    html += "</div>"
    return html


# ==============================================================================
# 7. DELAYED PROJECTS
# ==============================================================================
def get_delayed_projects() -> str:
    """Returns a list of currently delayed projects that have passed their deadline."""
    today = now().date()
    delayed = Project.objects.filter(end_date__lt=today).exclude(status='completed').order_by('end_date')
    if not delayed.exists():
        return "<div class='ai-answer'><i class='bi bi-check-circle-fill text-success me-1'></i> <strong>Badhiya khabar!</strong> Abhi koi bhi project delayed nahi hai. Sabhi projects schedule par chal rahe hain.</div>"
    
    html = f"<div class='ai-answer'><i class='bi bi-exclamation-octagon-fill text-danger me-1'></i> <strong>{delayed.count()} Delayed Project(s) mile:</strong><br><ul class='mt-2 ps-3 mb-0'>"
    for p in delayed[:6]:
        days_late = (today - p.end_date).days if p.end_date else 0
        client = p.lead.name if (p.lead and p.lead.name) else (p.title or 'N/A')
        client_phone = p.lead.phone if (p.lead and p.lead.phone) else ''
        html += (
            f"<li class='mb-2'>"
            f"<strong>{p.title}</strong> (ID: {p.project_id or p.id})<br>"
            f"<span class='badge bg-danger-subtle text-danger border border-danger-subtle'>Deadline: {p.end_date} ({days_late} din late)</span><br>"
            f"<small class='text-muted'>Client: {client} {f'({client_phone})' if client_phone else ''} | Stage: {p.get_status_display()}</small>"
            f"</li>"
        )
    html += "</ul></div>"
    return html


# ==============================================================================
# 8. PENDING SUBSIDIES
# ==============================================================================
def get_pending_subsidies() -> str:
    """Returns a list of projects that are currently pending in the subsidy stage."""
    subsidy_projs = Project.objects.filter(status='subsidy').order_by('-created_at')
    if not subsidy_projs.exists():
        return "<div class='ai-answer'><i class='bi bi-info-circle text-primary me-1'></i> Abhi koi bhi project <strong>Subsidy Stage</strong> me pending nahi hai. (Agar aapko solar subsidy rules/calculator dekhna hai, to <em>'3kw subsidy'</em> type karein!)</div>"
    
    html = f"<div class='ai-answer'><i class='bi bi-bank text-info me-1'></i> <strong>{subsidy_projs.count()} Project(s) Subsidy Stage me hain:</strong><br><ul class='mt-2 ps-3 mb-0'>"
    for p in subsidy_projs[:6]:
        client = p.lead.name if (p.lead and p.lead.name) else (p.title or 'N/A')
        loc = p.location or (p.lead.location if p.lead else 'N/A')
        html += (
            f"<li class='mb-2'>"
            f"<strong>{p.title}</strong> (Client: {client})<br>"
            f"<small class='text-muted'>Type: {p.get_project_type_display()} | Location: {loc}</small>"
            f"</li>"
        )
    html += "</ul></div>"
    return html


# ==============================================================================
# 9. MANAGEMENT SUMMARY
# ==============================================================================
def get_management_summary() -> str:
    """Returns the comprehensive management summary across CRM, Projects, Finance, and Godown."""
    today = now().date()
    act_projs = Project.objects.exclude(status='completed').count()
    delayed_projs = Project.objects.filter(end_date__lt=today).exclude(status='completed').count()
    subsidies = Project.objects.filter(status='subsidy').count()
    new_leads = Lead.objects.filter(status='new').count()
    rev = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    paid = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    low_stocks = Stock.objects.filter(quantity__lte=5).count()
    
    html = (
        f"<div class='ai-answer'>"
        f"<strong class='text-primary fs-6'><i class='bi bi-speedometer2 me-1'></i> Zyphora Solar ERP Executive Briefing:</strong><br><br>"
        f"• Active Solar Projects: <strong>{act_projs}</strong><br>"
        f"• Overdue / Delayed Projects: <strong class='{'text-danger' if delayed_projs > 0 else 'text-success'}'>{delayed_projs}</strong><br>"
        f"• Projects in Subsidy Stage: <strong>{subsidies}</strong><br>"
        f"• Unattended New Leads: <strong>{new_leads}</strong><br>"
        f"• Total Billed Revenue: <strong>&#8377;{rev:,.2f}</strong><br>"
        f"• Payments Collected: <strong class='text-success'>&#8377;{paid:,.2f}</strong><br>"
        f"• Low Stock Items Alert: <strong class='{'text-danger' if low_stocks > 0 else 'text-success'}'>{low_stocks}</strong><br><br>"
        f"<small class='text-muted'>Tip: Aap specific query pooch sakte hain, jaise <em>'3kw subsidy'</em>, <em>'PRJ-1001 status'</em>, <em>'Waaree panel stock'</em>, ya <em>'profit and loss'</em>.</small>"
        f"</div>"
    )
    return html


# ==============================================================================
# 10. TOOL DEFINITIONS FOR LANGGRAPH AGENT
# ==============================================================================
if LANGGRAPH_AVAILABLE:
    @tool
    def tool_calculate_solar_specs_and_subsidy(system_kw: float, roof_sqft: float = 0.0) -> str:
        """Calculates solar specs, power generation, roof space, and PM Surya Ghar subsidy for a given kW capacity."""
        return calculate_solar_specs_and_subsidy(system_kw, roof_sqft)

    @tool
    def tool_search_project(query: str) -> str:
        """Searches projects by Project ID, title, customer name, or location."""
        return search_project(query)

    @tool
    def tool_search_lead_or_customer(query: str) -> str:
        """Searches leads and customers by name, phone number, email, or location."""
        return search_lead_or_customer(query)

    @tool
    def tool_check_material_stock(material_query: str = "") -> str:
        """Checks inventory stock for solar panels, inverters, cables, structure, or returns low stock alerts."""
        return check_material_stock(material_query)

    @tool
    def tool_get_financial_ledger_and_profit() -> str:
        """Returns live financial ledger including billed revenue, collections, expenses, and net profit margin."""
        return get_financial_ledger_and_profit()

    @tool
    def tool_search_vendor_or_po(query: str = "") -> str:
        """Searches vendors and purchase orders in procurement."""
        return search_vendor_or_po(query)

    @tool
    def tool_get_delayed_projects() -> str:
        """Returns all overdue and delayed projects."""
        return get_delayed_projects()

    @tool
    def tool_get_pending_subsidies() -> str:
        """Returns all projects currently pending in subsidy stage."""
        return get_pending_subsidies()

    @tool
    def tool_get_management_summary() -> str:
        """Returns executive daily summary across projects, CRM, finance, and stock."""
        return get_management_summary()


# ==============================================================================
# 11. HYBRID NLP INTENT ENGINE (OFFLINE & DIRECT DB PARSER)
# ==============================================================================
def execute_smart_erp_query(user_query: str) -> str:
    """
    Direct intelligent ERP database analyzer that interprets questions
    in English, Hindi or Hinglish and answers with live database records.
    Uses pure HTML and Bootstrap Icons for 100% platform encoding compatibility.
    """
    q = user_query.lower().strip()
    today = now().date()

    # 1. GREETING / HELP
    if any(k in q for k in ['hi', 'hello', 'hey', 'namaste', 'kaise ho', 'help', 'kya kar sakte', 'who are you', 'kya help']) and len(q.split()) <= 4:
        return (
            "<div class='ai-answer'>"
            "<strong><i class='bi bi-robot text-primary me-1'></i>Namaste! Main Zyphora Solar ERP ka Senior AI Assistant hoon.</strong><br><br>"
            "Main aapke live ERP data aur Solar Engineering se related sabhi sawaalon ke instant jawaab de sakta hoon:<br>"
            "<ul class='mt-2 ps-3 mb-2 small' style='line-height: 1.6;'>"
            "<li><strong><i class='bi bi-sun text-warning me-1'></i>PM Surya Ghar & Solar Calculator:</strong> <em>'3kw subsidy'</em>, <em>'5kw solar cost'</em>, <em>'roof area for 4kw'</em></li>"
            "<li><strong><i class='bi bi-folder-check text-primary me-1'></i>Specific Project Details:</strong> <em>'PRJ-1001 status'</em>, <em>'manoj project'</em></li>"
            "<li><strong><i class='bi bi-exclamation-triangle text-danger me-1'></i>Delayed Projects:</strong> <em>'delayed projects'</em>, <em>'late projects'</em></li>"
            "<li><strong><i class='bi bi-cash-coin text-success me-1'></i>Profit & Loss & Finance:</strong> <em>'profit and loss'</em>, <em>'revenue'</em>, <em>'ledger'</em></li>"
            "<li><strong><i class='bi bi-boxes text-info me-1'></i>Material & Godown Stock:</strong> <em>'Waaree panel stock'</em>, <em>'Growatt inverter'</em>, <em>'stock alert'</em></li>"
            "<li><strong><i class='bi bi-person-lines-fill text-success me-1'></i>CRM & Leads Search:</strong> <em>'lead aditya'</em>, <em>'new leads'</em>, phone number</li>"
            "<li><strong><i class='bi bi-truck text-secondary me-1'></i>Procurement & Vendors:</strong> <em>'vendors'</em>, <em>'purchase orders'</em></li>"
            "</ul>"
            "<small class='text-muted'>Aap neeche diye gaye chips par click karke ya koi bhi sawaal type karke pooch sakte hain!</small>"
            "</div>"
        )

    # 2. SOLAR CALCULATION / PM SURYA GHAR SUBSIDY / ROOF FEASIBILITY INTENT
    kw_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kw|kilo\s*watt|kilowatt)', q)
    sqft_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square\s*feet|foot)', q)
    solar_calc_keywords = ['subsidy', 'surya ghar', 'muft bijli', 'solar calculator', 'bijli ka bill', 'kitna kharcha', 'generation', 'savings', 'payback', 'solar lagwana', 'chhat', 'roof']
    
    if kw_match or any(k in q for k in ['surya ghar', 'muft bijli', 'solar calculator']) or (any(k in q for k in ['subsidy', 'kharcha', 'generation', 'payback', 'savings']) and not any(k in q for k in ['project pending', 'stage'])):
        kw_val = float(kw_match.group(1)) if kw_match else 3.0
        roof_val = float(sqft_match.group(1)) if sqft_match else 0.0
        
        # If user only specified roof area like "500 sqft roof hai"
        if not kw_match and roof_val > 0:
            kw_val = round(roof_val / 90.0, 1)
            
        return calculate_solar_specs_and_subsidy(kw_val, roof_val)

    # 3. SPECIFIC PROJECT SEARCH BY ID OR NAME
    prj_id_match = re.search(r'\b(prj[-\s]?\d+|kg-up-[-\w]+)\b', q)
    if prj_id_match:
        return search_project(prj_id_match.group(1))

    cleaned_prj_q = re.sub(r'\b(project|projects|prject|details|ka|ki|ke|batao|show|status|delayed|all|list|report|summary)\b', '', q).strip()
    if cleaned_prj_q and len(cleaned_prj_q) >= 3 and any(k in q for k in ['project', 'prject', 'plant', 'site']):
        matching_prjs = Project.objects.filter(
            Q(project_id__icontains=cleaned_prj_q) |
            Q(title__icontains=cleaned_prj_q) |
            Q(lead__name__icontains=cleaned_prj_q)
        )
        if matching_prjs.exists():
            return search_project(cleaned_prj_q)

    # 4. DELAYED PROJECTS
    if any(k in q for k in ['delayed', 'delay', 'late', 'overdue', 'atke', 'late chal rahe', 'deadline', 'pending date']):
        return get_delayed_projects()

    # 5. SUBSIDY STAGE WORKFLOW (ERP Projects in Subsidy stage)
    if any(k in q for k in ['subsidy stage', 'projects in subsidy', 'discom', 'anudan stage']):
        return get_pending_subsidies()

    # 6. PROFIT & LOSS / FINANCIAL LEDGER / REVENUE
    if any(k in q for k in ['profit', 'loss', 'p&l', 'revenue', 'kamai', 'kharcha', 'expenses', 'ledger', 'balance sheet', 'collection', 'overdue invoice']):
        return get_financial_ledger_and_profit()

    # 7. MATERIAL & INVENTORY STOCK SEARCH
    mat_keywords = ['panel', 'inverter', 'cable', 'wire', 'structure', 'battery', 'waaree', 'growatt', 'polycab', 'luminous', 'tata', 'godown', 'warehouse', 'stock', 'inventory', 'samaan']
    if any(k in q for k in mat_keywords):
        term = ""
        for brand in ['waaree', 'growatt', 'polycab', 'luminous', 'tata', 'mono perc', 'inverter', 'cable', 'structure', 'battery', 'panel']:
            if brand in q:
                term = brand
                break
        return check_material_stock(term)

    # 8. SPECIFIC LEAD OR PHONE NUMBER SEARCH
    phone_match = re.search(r'\b[6-9]\d{9}\b', q)
    if phone_match:
        return search_lead_or_customer(phone_match.group(0))

    cleaned_lead_q = re.sub(r'\b(lead|leads|customer|customers|client|clients|graahak|details|ka|ki|ke|batao|show|status|phone|number|contact)\b', '', q).strip()
    if cleaned_lead_q and len(cleaned_lead_q) >= 3 and any(k in q for k in ['lead', 'customer', 'client', 'graahak']):
        matching_leads = Lead.objects.filter(
            Q(name__icontains=cleaned_lead_q) |
            Q(phone__icontains=cleaned_lead_q) |
            Q(location__icontains=cleaned_lead_q)
        )
        if matching_leads.exists():
            return search_lead_or_customer(cleaned_lead_q)

    # 9. GENERAL LEADS OVERVIEW
    if any(k in q for k in ['lead', 'leads', 'crm', 'commercial lead', 'residential lead', 'inquiry']):
        new_leads = Lead.objects.filter(status='new').order_by('-score', '-created_at')
        total_leads = Lead.objects.count()
        commercial_new = Lead.objects.filter(service='commercial', status='new').count()
        residential_new = Lead.objects.filter(service='residential', status='new').count()
        
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-people-fill text-success me-1'></i>CRM & Leads Overview:</strong><br>"
            f"Total Leads: <strong>{total_leads}</strong> | Unattended New: <strong class='text-warning'>{new_leads.count()}</strong><br>"
            f"Commercial New: <strong>{commercial_new}</strong> | Residential New: <strong>{residential_new}</strong><br>"
        )
        if new_leads.exists():
            html += "<br><strong>Top Pending Leads:</strong><ul class='mt-1 ps-3 mb-0 small'>"
            for l in new_leads[:5]:
                html += f"<li class='mb-1'><strong>{l.name}</strong> - <i class='bi bi-telephone text-primary'></i> {l.phone} (Score: {l.score or 0}, {l.get_service_display()})</li>"
            html += "</ul>"
        else:
            html += "<br><span class='text-success'><i class='bi bi-check-circle'></i> Sabhi leads contact ho chuki hain!</span>"
        html += "</div>"
        return html

    # 10. VENDORS / PROCUREMENT / PO / RFQ
    if any(k in q for k in ['vendor', 'vendors', 'procurement', 'purchase order', 'po', 'rfq', 'supplier', 'suppliers']):
        term = ""
        for word in q.split():
            if word not in ['vendor', 'vendors', 'po', 'status', 'list', 'purchase', 'order', 'orders', 'details', 'show', 'batao', 'ka', 'ki']:
                term = word
                break
        return search_vendor_or_po(term)

    # 11. GENERAL PROJECTS SNAPSHOT
    if any(k in q for k in ['project', 'projects', 'solar project', 'projekts']):
        total_projs = Project.objects.count()
        act_projs = Project.objects.exclude(status='completed').count()
        completed_projs = Project.objects.filter(status='completed').count()
        recent = Project.objects.order_by('-created_at')[:5]
        
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-folder-fill text-primary me-1'></i>Projects Pipeline Snapshot:</strong><br>"
            f"Total Projects: <strong>{total_projs}</strong> | Active: <strong class='text-primary'>{act_projs}</strong> | Completed: <strong class='text-success'>{completed_projs}</strong><br><br>"
            f"<strong>Recent Active Projects:</strong><ul class='mt-1 ps-3 mb-0 small'>"
        )
        for p in recent:
            stage_badge = "<span class='badge bg-success'>Completed</span>" if p.status == 'completed' else f"<span class='badge bg-primary-subtle text-primary border border-primary-subtle'>{p.get_status_display()}</span>"
            html += f"<li class='mb-1'><strong>{p.title}</strong> {stage_badge}<br><small class='text-muted'>ID: {p.project_id or p.id} | Due: {p.end_date or 'N/A'}</small></li>"
        html += "</ul></div>"
        return html

    # 12. DIRECT ENTITY LOOKUP (If user typed a bare name, phone, material, or project code)
    if len(q.split()) <= 4:
        # Check Project
        matched_proj = Project.objects.filter(Q(title__icontains=q) | Q(project_id__icontains=q) | Q(lead__name__icontains=q))
        if matched_proj.exists():
            return search_project(q)
            
        # Check Lead
        matched_lead = Lead.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))
        if matched_lead.exists():
            return search_lead_or_customer(q)
            
        # Check Material
        matched_mat = Material.objects.filter(Q(name__icontains=q) | Q(brand__icontains=q))
        if matched_mat.exists():
            return check_material_stock(q)

    # 13. EMPLOYEES / WORKFORCE
    if any(k in q for k in ['employee', 'employees', 'staff', 'team', 'engineer', 'worker']):
        emp_count = Employee.objects.count()
        users_count = CustomUser.objects.count()
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-person-badge text-primary me-1'></i>Team & Workforce:</strong><br>"
            f"Total Registered Employees: <strong>{emp_count}</strong><br>"
            f"Total Active System Users: <strong>{users_count}</strong>"
            f"</div>"
        )
        return html

    # 14. DEFAULT EXECUTIVE MANAGEMENT BRIEFING
    return get_management_summary()


# ==============================================================================
# 12. MAIN AI AGENT API ENDPOINT
# ==============================================================================
@csrf_exempt
@login_required(login_url='/users/login')
def ai_agent_query(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_query = data.get("query", "").strip()
        if not user_query:
            return JsonResponse({"error": "Empty query"}, status=400)
            
        groq_key = os.environ.get("GROQ_API_KEY", "").strip() or getattr(settings, 'GROQ_API_KEY', '').strip()
        
        # If Groq key is present and LangGraph is available, run advanced LLM ReAct Agent
        if groq_key and LANGGRAPH_AVAILABLE:
            try:
                llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=groq_key, timeout=7.0)
                tools = [
                    tool_calculate_solar_specs_and_subsidy,
                    tool_search_project,
                    tool_search_lead_or_customer,
                    tool_check_material_stock,
                    tool_get_financial_ledger_and_profit,
                    tool_search_vendor_or_po,
                    tool_get_delayed_projects,
                    tool_get_pending_subsidies,
                    tool_get_management_summary,
                ]
                system_prompt = (
                    "You are the senior intelligent AI Assistant for Zyphora Solar ERP. "
                    "You have direct real-time access to ERP database tools and a solar engineering & PM Surya Ghar calculator. "
                    "Always inspect user queries carefully. When asked about specific projects, leads, stock, vendors, subsidies, solar sizing, or financials, invoke the relevant tool immediately. "
                    "Format your final response in clean, beautiful HTML using standard HTML tags like <div>, <strong>, <span class='badge ...'>, <ul>, <li>, <i class='bi ...'>, <br>. "
                    "Do NOT use raw Markdown formatting (like ** or ```) in the final response - always return pure HTML."
                )
                agent_executor = create_react_agent(llm, tools, prompt=system_prompt)
                result = agent_executor.invoke({"messages": [("user", user_query)]})
                final_answer = result["messages"][-1].content
                return JsonResponse({"response": final_answer})
            except Exception as llm_err:
                # Fall back gracefully to internal Smart ERP engine!
                pass
                
        # Internal Smart ERP Engine (100% reliable, zero external downtime, accurate live DB metrics)
        response_html = execute_smart_erp_query(user_query)
        return JsonResponse({"response": response_html})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
