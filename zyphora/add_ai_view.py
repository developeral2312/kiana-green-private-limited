import os

views_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\users\views.py"

ai_agent_code = """

@login_required(login_url='/users/login')
@require_POST
def ai_agent_query(request):
    if request.user.role not in ['admin']:
        return JsonResponse({"error": "Permission Denied. AI Agent requires Management access."}, status=403)
        
    try:
        data = json.loads(request.body)
        query = data.get("query", "").lower()
        
        response_html = ""
        
        # 1. Delayed Projects
        if "delayed" in query or "delay" in query:
            delayed = Project.objects.filter(end_date__lt=now().date()).exclude(status='completed')
            if delayed.exists():
                response_html += f"Found <strong>{delayed.count()}</strong> delayed projects:<br><ul style='text-align:left; margin-top:10px;'>"
                for p in delayed[:5]:
                    response_html += f"<li>{p.project_id or p.id} - {p.title} (Deadline: {p.end_date})</li>"
                response_html += "</ul>"
            else:
                response_html = "Great news! There are no delayed projects right now."

        # 2. Pending Subsidy
        elif "subsidy" in query:
            subsidy = Project.objects.filter(status='subsidy')
            if subsidy.exists():
                response_html += f"Found <strong>{subsidy.count()}</strong> projects pending subsidy:<br><ul style='text-align:left; margin-top:10px;'>"
                for p in subsidy[:5]:
                    response_html += f"<li>{p.project_id or p.id} - {p.title}</li>"
                response_html += "</ul>"
            else:
                response_html = "No projects are currently stuck in the subsidy stage."
                
        # 3. Commercial Leads pending
        elif "commercial" in query and "lead" in query:
            leads = Lead.objects.filter(service='commercial', status='new')
            if leads.exists():
                response_html += f"You have <strong>{leads.count()}</strong> unattended commercial leads:<br><ul style='text-align:left; margin-top:10px;'>"
                for l in leads[:5]:
                    response_html += f"<li>{l.name} - {l.phone} (Score: {l.score})</li>"
                response_html += "</ul>"
            else:
                response_html = "All commercial leads have been contacted!"

        # 4. Summary / Today
        elif "summary" in query or "today" in query:
            rev = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
            act = Project.objects.exclude(status='completed').count()
            response_html = f"<strong>Today's Management Summary:</strong><br>Total Revenue: ₹{rev:,.2f}<br>Active Projects: {act}<br>Keep up the good work!"
            
        else:
            response_html = "I am securely connected to the Django ERP Database. I can fetch insights on <strong>delayed projects, commercial leads, subsidies, and summaries</strong>.<br><br><small><em>(To answer ANY arbitrary question, please insert the Groq/OpenAI API Key in settings.py to activate full function-calling).</em></small>"
            
        return JsonResponse({"response": response_html})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
"""

with open(views_path, "a", encoding="utf-8") as f:
    f.write(ai_agent_code)

print("Appended ai_agent_query to views.py")
