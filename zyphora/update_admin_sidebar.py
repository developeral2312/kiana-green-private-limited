import os

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'
admin_path = os.path.join(base_path, 'admin_sidebar.html')

if os.path.exists(admin_path):
    with open(admin_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add RFQ
    if 'rfq_list' not in content:
        content = content.replace(
            '<li><a href="{% url \'material_list\' %}" class="nav-link">Materials</a></li>',
            '<li><a href="{% url \'material_list\' %}" class="nav-link">Materials</a></li>\n                    <li><a href="{% url \'rfq_list\' %}" class="nav-link text-warning">Vendor Bidding (RFQ)</a></li>'
        )

    # Add P&L
    if 'project_profit_report' not in content:
        content = content.replace(
            '<li><a href="{% url \'project_costing\' %}" class="nav-link">Project Costing</a></li>',
            '<li><a href="{% url \'project_costing\' %}" class="nav-link">Project Costing</a></li>\n                    <li><a href="{% url \'project_profit_report\' %}" class="nav-link text-success">P&L Analytics</a></li>'
        )

    # Add Support Tickets and Subcontractor to Projects section
    if 'ticket_list' not in content:
        # find projects submenu and inject
        target = '<li><a href="{% url \'completed_projects\' %}" class="nav-link">Completed Projects</a></li>'
        addition = '<li><a href="{% url \'ticket_list\' %}" class="nav-link text-danger">Helpdesk & AMC</a></li>\n                    <li><a href="{% url \'subcontractor_dashboard\' %}" class="nav-link text-info">Subcontractor Portal</a></li>'
        content = content.replace(target, target + '\n                    ' + addition)

    # Add Referrals & Escalations to CRM section
    if 'referral_list' not in content:
        target = '<li><a href="{% url \'followups\' %}" class="nav-link">Follow-ups</a></li>'
        addition = '<li><a href="{% url \'referral_list\' %}" class="nav-link text-warning">Referral Engine</a></li>\n                    <li><a href="{% url \'escalation_dashboard\' %}" class="nav-link text-danger">Escalation Matrix</a></li>'
        content = content.replace(target, target + '\n                    ' + addition)

    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(content)

print('Admin sidebar fixed.')
