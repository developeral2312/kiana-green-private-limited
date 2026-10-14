import os
import re

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'
files = [f for f in os.listdir(base_path) if f.endswith('_sidebar.html')]

# We'll map new views to their respective menu categories.
# If a sidebar has a string like "lead_list add_lead review" we will just append the new url names to the string.
# We will use regex to find all "resolver_match.url_name in '...'" and if it has lead_list, append referral_list, etc.

additions_map = {
    'lead_list': ' referral_list escalation_dashboard',
    'project_list': ' ticket_list subcontractor_dashboard project_costing',
    'material_list': ' rfq_list',
    'invoice_list': ' project_profit_report project_costing'
}

for filename in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # We look for patterns like: 'lead_list add_lead review'
    # Actually, it's easier to just do simple string replacements if the URL name is there.
    
    # 1. CRM
    if "'lead_list" in content and 'referral_list' not in content:
        # Some use 'lead_list add_lead review'
        content = re.sub(r"('[\w\s]*lead_list[\w\s]*)'", r"\1 referral_list escalation_dashboard'", content)
        modified = True

    # 2. Projects
    if "'project_list" in content and 'ticket_list' not in content:
        content = re.sub(r"('[\w\s]*project_list[\w\s]*)'", r"\1 ticket_list subcontractor_dashboard'", content)
        modified = True
        
    # 3. Procurement
    if "request.resolver_match.url_name == 'material_list'" in content and 'rfq_list' not in content:
        # Procurement in admin_sidebar uses "or request.resolver_match.url_name == '...'"
        content = content.replace("request.resolver_match.url_name == 'material_list'", "request.resolver_match.url_name == 'material_list' or request.resolver_match.url_name == 'rfq_list'")
        modified = True
        
    # 4. Finance
    if "'invoice_list" in content and 'project_profit_report' not in content:
        content = re.sub(r"('[\w\s]*invoice_list[\w\s]*)'", r"\1 project_profit_report'", content)
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Resolver checks fixed.")
