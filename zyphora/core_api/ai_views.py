import os
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
from finance.models import Invoice, Payment, ExpenseReport
from procurement.models import Material, Stock, PurchaseOrder, Vendor, RequestForQuotation
from users.models import CustomUser, Employee

# LangChain & LangGraph imports (safe/conditional)
try:
    from langchain_core.tools import tool
    from langchain_groq import ChatGroq
    from langgraph.prebuilt import create_react_agent
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    tool = lambda f: f


# Define tools for LLM agent
if LANGGRAPH_AVAILABLE:
    @tool
    def get_delayed_projects() -> str:
        """Returns a list of currently delayed projects that have passed their deadline."""
        delayed = Project.objects.filter(end_date__lt=now().date()).exclude(status='completed')
        if not delayed.exists():
            return "There are no delayed projects right now."
        res = f"Found {delayed.count()} delayed projects:\n"
        for p in delayed[:10]:
            res += f"- {p.title} (Project ID: {p.project_id}, Deadline: {p.end_date})\n"
        return res

    @tool
    def get_pending_subsidies() -> str:
        """Returns a list of projects that are currently pending in the subsidy stage."""
        subsidy = Project.objects.filter(status='subsidy')
        if not subsidy.exists():
            return "No projects are currently pending subsidy."
        res = f"Found {subsidy.count()} projects pending subsidy:\n"
        for p in subsidy[:10]:
            res += f"- {p.title} (Project ID: {p.project_id})\n"
        return res

    @tool
    def get_pending_commercial_leads() -> str:
        """Returns a list of commercial leads that have not been contacted yet (status='new')."""
        leads = Lead.objects.filter(service='commercial', status='new')
        if not leads.exists():
            return "All commercial leads have been contacted."
        res = f"Found {leads.count()} unattended commercial leads:\n"
        for l in leads[:10]:
            res += f"- {l.name} (Phone: {l.phone}, Score: {l.score})\n"
        return res

    @tool
    def get_management_summary() -> str:
        """Returns the daily management summary including total active projects and total revenue."""
        act = Project.objects.exclude(status='completed').count()
        rev = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        return f"Active Projects: {act}\nTotal Invoiced Revenue: Rs. {rev:,.2f}"


def execute_smart_erp_query(user_query: str) -> str:
    """
    Intelligent direct ERP database analyzer that interprets questions
    in English, Hindi or Hinglish and answers with live database records.
    Uses pure HTML and Bootstrap Icons for 100% platform encoding compatibility.
    """
    q = user_query.lower().strip()
    today = now().date()

    # 1. GREETING / HELP
    if any(k in q for k in ['hi', 'hello', 'hey', 'namaste', 'kaise ho', 'help', 'kya kar sakte', 'who are you', 'kya help']) and len(q.split()) <= 4:
        return (
            "<div class='ai-answer'>"
            "<strong><i class='bi bi-robot text-primary me-1'></i>Namaste! Main Zyphora Solar ERP ka AI Assistant hoon.</strong><br><br>"
            "Main aapke live ERP system se instant data aur reports fetch kar sakta hoon:<br>"
            "<ul class='mt-2 ps-3 mb-2'>"
            "<li><strong><i class='bi bi-bar-chart text-primary me-1'></i>Executive Summary:</strong> Type <em>'summary'</em> ya <em>'today'</em></li>"
            "<li><strong><i class='bi bi-exclamation-triangle text-danger me-1'></i>Delayed Projects:</strong> Type <em>'delayed projects'</em></li>"
            "<li><strong><i class='bi bi-folder-check text-info me-1'></i>All Projects:</strong> Type <em>'projects'</em></li>"
            "<li><strong><i class='bi bi-bank text-warning me-1'></i>Subsidy Status:</strong> Type <em>'subsidy'</em></li>"
            "<li><strong><i class='bi bi-person-lines-fill text-success me-1'></i>Leads & CRM:</strong> Type <em>'leads'</em></li>"
            "<li><strong><i class='bi bi-boxes text-info me-1'></i>Godown Stock:</strong> Type <em>'stock'</em></li>"
            "<li><strong><i class='bi bi-currency-rupee text-success me-1'></i>Finance & Revenue:</strong> Type <em>'revenue'</em></li>"
            "<li><strong><i class='bi bi-truck text-secondary me-1'></i>Procurement:</strong> Type <em>'vendors'</em> ya <em>'orders'</em></li>"
            "</ul>"
            "<small class='text-muted'>Aap neeche diye gaye chips par click karke ya koi bhi sawaal type karke pooch sakte hain!</small>"
            "</div>"
        )

    # 2. DELAYED PROJECTS
    if any(k in q for k in ['delayed', 'delay', 'late', 'overdue', 'atke', 'late chal rahe', 'deadline', 'pending date']):
        delayed = Project.objects.filter(end_date__lt=today).exclude(status='completed').order_by('end_date')
        if not delayed.exists():
            return "<div class='ai-answer'><i class='bi bi-check-circle-fill text-success me-1'></i> <strong>Badhiya khabar!</strong> Abhi koi bhi project delayed nahi hai. Sabhi projects schedule par chal rahe hain.</div>"
        
        html = f"<div class='ai-answer'><i class='bi bi-exclamation-octagon-fill text-danger me-1'></i> <strong>{delayed.count()} Delayed Project(s) mile:</strong><br><ul class='mt-2 ps-3 mb-0'>"
        for p in delayed[:6]:
            days_late = (today - p.end_date).days if p.end_date else 0
            client = p.lead.name if (p.lead and p.lead.name) else (p.title or 'N/A')
            html += (
                f"<li class='mb-2'>"
                f"<strong>{p.title}</strong> (ID: {p.project_id or p.id})<br>"
                f"<span class='badge bg-danger-subtle text-danger border border-danger-subtle'>Deadline: {p.end_date} ({days_late} din late)</span><br>"
                f"<small class='text-muted'>Client: {client} | Stage: {p.get_status_display()}</small>"
                f"</li>"
            )
        html += "</ul></div>"
        return html

    # 3. PENDING SUBSIDIES
    if any(k in q for k in ['subsidy', 'subsidies', 'discom', 'anudan', 'yojana']):
        subsidy_projs = Project.objects.filter(status='subsidy').order_by('-created_at')
        if not subsidy_projs.exists():
            return "<div class='ai-answer'><i class='bi bi-info-circle text-primary me-1'></i> Abhi koi bhi project <strong>Subsidy Stage</strong> me pending nahi hai.</div>"
        
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

    # 4. PROJECTS GENERAL STATUS & PIPELINE
    if any(k in q for k in ['project', 'projects', 'solar project', 'projekts']):
        total_projs = Project.objects.count()
        act_projs = Project.objects.exclude(status='completed').count()
        completed_projs = Project.objects.filter(status='completed').count()
        recent = Project.objects.order_by('-created_at')[:5]
        
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-folder-fill text-primary me-1'></i>Projects Pipeline Snapshot:</strong><br>"
            f"Total Projects: <strong>{total_projs}</strong> | Active: <strong class='text-primary'>{act_projs}</strong> | Completed: <strong class='text-success'>{completed_projs}</strong><br><br>"
            f"<strong>Recent Active Projects:</strong><ul class='mt-1 ps-3 mb-0'>"
        )
        for p in recent:
            stage_badge = "<span class='badge bg-success'>Completed</span>" if p.status == 'completed' else f"<span class='badge bg-primary-subtle text-primary border border-primary-subtle'>{p.get_status_display()}</span>"
            html += f"<li class='mb-1'><strong>{p.title}</strong> {stage_badge}<br><small class='text-muted'>ID: {p.project_id or p.id} | Due: {p.end_date or 'N/A'}</small></li>"
        html += "</ul></div>"
        return html

    # 5. LEADS / CRM / CLIENTS
    if any(k in q for k in ['lead', 'leads', 'crm', 'commercial', 'residential', 'graahak', 'customer', 'inquiry']):
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
            html += "<br><strong>Top Pending Leads:</strong><ul class='mt-1 ps-3 mb-0'>"
            for l in new_leads[:5]:
                html += f"<li class='mb-1'><strong>{l.name}</strong> - <i class='bi bi-telephone text-primary'></i> {l.phone} (Score: {l.score or 0}, {l.get_service_display()})</li>"
            html += "</ul>"
        else:
            html += "<br><span class='text-success'><i class='bi bi-check-circle'></i> Sabhi leads contact ho chuki hain!</span>"
        html += "</div>"
        return html

    # 6. STOCK / INVENTORY / MATERIALS
    if any(k in q for k in ['stock', 'inventory', 'material', 'materials', 'panel', 'inverter', 'cable', 'godown', 'warehouse', 'samaan', 'kit']):
        stocks = Stock.objects.select_related('material').all()
        low_stocks = [s for s in stocks if s.quantity <= (s.material.minimum_stock or 5)]
        
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-boxes text-info me-1'></i>Warehouse & Inventory Status:</strong><br>"
            f"Total Materials in System: <strong>{Material.objects.count()}</strong><br>"
        )
        
        if low_stocks:
            html += f"<br><strong class='text-danger'><i class='bi bi-exclamation-triangle-fill me-1'></i>Low Stock Alert ({len(low_stocks)} items):</strong><ul class='mt-1 ps-3 mb-2'>"
            for s in low_stocks[:5]:
                html += f"<li><strong>{s.material.name}</strong>: Available <span class='badge bg-danger'>{s.quantity} {s.material.unit}</span> (Min: {s.material.minimum_stock})</li>"
            html += "</ul>"
        else:
            html += "<br><span class='text-success'><i class='bi bi-check-circle-fill me-1'></i>Sabhi materials minimum stock se upar hain.</span><br>"
            
        html += "<br><strong>Available Stock Highlights:</strong><ul class='mt-1 ps-3 mb-0'>"
        for s in stocks.order_by('-quantity')[:5]:
            html += f"<li>{s.material.name}: <strong>{s.quantity} {s.material.unit}</strong></li>"
        html += "</ul></div>"
        return html

    # 7. VENDORS / PROCUREMENT / PO / RFQ
    if any(k in q for k in ['vendor', 'vendors', 'procurement', 'purchase order', 'po', 'rfq', 'bidding', 'supplier', 'suppliers']):
        v_count = Vendor.objects.count()
        po_pending = PurchaseOrder.objects.filter(status='pending').count()
        po_received = PurchaseOrder.objects.filter(status='received').count()
        rfq_open = RequestForQuotation.objects.exclude(status='closed').count()
        
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-truck text-secondary me-1'></i>Procurement Intelligence:</strong><br>"
            f"Registered Vendors: <strong>{v_count}</strong><br>"
            f"Pending Purchase Orders (PO): <strong class='text-warning'>{po_pending}</strong><br>"
            f"Received / Completed POs: <strong class='text-success'>{po_received}</strong><br>"
            f"Active RFQ Tenders: <strong>{rfq_open}</strong>"
            f"</div>"
        )
        return html

    # 8. FINANCE / REVENUE / INVOICES / PAYMENTS
    if any(k in q for k in ['revenue', 'finance', 'invoice', 'invoices', 'payment', 'paisa', 'kamai', 'billing', 'profit', 'expense', 'expenses', 'collection']):
        total_invoiced = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        paid_invoices = Invoice.objects.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        pending_invoices = Invoice.objects.exclude(status='paid').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        html = (
            f"<div class='ai-answer'>"
            f"<strong><i class='bi bi-cash-stack text-success me-1'></i>Live Finance Snapshot:</strong><br>"
            f"Total Invoiced Revenue: <strong>₹{total_invoiced:,.2f}</strong><br>"
            f"Payments Collected: <strong class='text-success'>₹{paid_invoices:,.2f}</strong><br>"
            f"Pending / Due Invoices: <strong class='text-danger'>₹{pending_invoices:,.2f}</strong><br>"
            f"Total Invoices Generated: <strong>{Invoice.objects.count()}</strong>"
            f"</div>"
        )
        return html

    # 9. EMPLOYEES / STAFF / TEAM
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

    # 10. GENERAL SUMMARY / DEFAULT DASHBOARD SNAPSHOT
    act_projs = Project.objects.exclude(status='completed').count()
    delayed_projs = Project.objects.filter(end_date__lt=today).exclude(status='completed').count()
    subsidies = Project.objects.filter(status='subsidy').count()
    rev = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    new_leads = Lead.objects.filter(status='new').count()
    
    html = (
        f"<div class='ai-answer'>"
        f"<strong><i class='bi bi-speedometer2 text-primary me-1'></i>Live Zyphora ERP Executive Briefing:</strong><br><br>"
        f"• Active Solar Projects: <strong>{act_projs}</strong><br>"
        f"• Delayed Projects: <strong class='{'text-danger' if delayed_projs > 0 else 'text-success'}'>{delayed_projs}</strong><br>"
        f"• Pending Subsidies: <strong>{subsidies}</strong><br>"
        f"• Unattended New Leads: <strong>{new_leads}</strong><br>"
        f"• Total Invoiced Revenue: <strong>₹{rev:,.2f}</strong><br><br>"
        f"<small class='text-muted'>Tip: Aap quick chips click kar sakte hain ya pooch sakte hain: <em>'delayed projects'</em>, <em>'leads'</em>, <em>'stock'</em>, ya <em>'revenue'</em>.</small>"
        f"</div>"
    )
    return html


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
        
        # If Groq key is present and LangGraph is available, attempt LLM ReAct Agent
        if groq_key and LANGGRAPH_AVAILABLE:
            try:
                # Use current supported Groq model llama-3.3-70b-versatile
                llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=groq_key, timeout=7.0)
                tools = [
                    get_delayed_projects,
                    get_pending_subsidies,
                    get_pending_commercial_leads,
                    get_management_summary
                ]
                system_prompt = (
                    "You are the AI Assistant for the Zyphora Solar ERP. "
                    "Use the provided tools to answer the user's questions about live ERP data. "
                    "Format your final response in clean HTML using <ul>, <strong>, <br>. Do not use Markdown formatting in the final response."
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
