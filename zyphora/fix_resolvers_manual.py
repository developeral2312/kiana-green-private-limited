import os

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'
files = [f for f in os.listdir(base_path) if f.endswith('_sidebar.html')]

replacements = {
    "'project_list feasibility_list design_list installation_progress licensing_list energisation_projects completed_projects recent_activity gallery_projects'": "'project_list feasibility_list design_list installation_progress licensing_list energisation_projects completed_projects recent_activity gallery_projects ticket_list subcontractor_dashboard'",
    "'invoice_list client_payments all_expenses project_costing commission_list loan_dashboard'": "'invoice_list client_payments all_expenses project_costing commission_list loan_dashboard project_profit_report'",
    "'material_list' or request.resolver_match.url_name == 'admin_material_requests'": "'material_list' or request.resolver_match.url_name == 'rfq_list' or request.resolver_match.url_name == 'admin_material_requests'",
}

for filename in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for old_str, new_str in replacements.items():
        if old_str in content and new_str not in content:
            content = content.replace(old_str, new_str)
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Manual fix done.")
