import os
import re

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'
files = [f for f in os.listdir(base_path) if f.endswith('_sidebar.html')]

for filename in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Revert accidental URL replacements:
    content = content.replace("{% url 'lead_list referral_list escalation_dashboard' %}", "{% url 'lead_list' %}")
    content = content.replace("== 'lead_list referral_list escalation_dashboard'", "== 'lead_list'")
    
    content = content.replace("{% url 'project_list ticket_list subcontractor_dashboard project_costing' %}", "{% url 'project_list' %}")
    content = content.replace("== 'project_list ticket_list subcontractor_dashboard project_costing'", "== 'project_list'")
    content = content.replace("{% url 'project_list ticket_list subcontractor_dashboard' %}", "{% url 'project_list' %}")
    content = content.replace("== 'project_list ticket_list subcontractor_dashboard'", "== 'project_list'")

    content = content.replace("{% url 'invoice_list project_profit_report project_costing' %}", "{% url 'invoice_list' %}")
    content = content.replace("== 'invoice_list project_profit_report project_costing'", "== 'invoice_list'")
    content = content.replace("{% url 'invoice_list project_profit_report' %}", "{% url 'invoice_list' %}")
    content = content.replace("== 'invoice_list project_profit_report'", "== 'invoice_list'")

    # Also make sure the {% if url_name in ... %} has the correct spacing without duplicate
    # Wait, the previous regex was: `r"('[\w\s]*lead_list[\w\s]*)'"`
    # It might have affected ANY string with `lead_list` inside single quotes.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Reverted broken regex.")
