import os

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'

# 1. Update sales_sidebar.html
sales_path = os.path.join(base_path, 'sales_sidebar.html')
if os.path.exists(sales_path):
    with open(sales_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'referral_list' not in content:
        target = '<li><a href="{% url \'followups\' %}" class="nav-link">Follow-ups</a></li>'
        addition = '<li><a href="{% url \'referral_list\' %}" class="nav-link text-warning">Referrals</a></li>\n                    <li><a href="{% url \'escalation_dashboard\' %}" class="nav-link text-danger">Escalation Matrix</a></li>'
        content = content.replace(target, target + '\n                    ' + addition)
        with open(sales_path, 'w', encoding='utf-8') as f:
            f.write(content)

# 2. Update engineer_sidebar.html
eng_path = os.path.join(base_path, 'engineer_sidebar.html')
if os.path.exists(eng_path):
    with open(eng_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add RFQ to inventory menu
    if 'rfq_list' not in content:
        target1 = '<li><a href="{% url \'my_requests\' %}" class="nav-link">My Requests</a></li>'
        addition1 = '<li><a href="{% url \'rfq_list\' %}" class="nav-link text-warning">Vendor Bidding (RFQ)</a></li>'
        content = content.replace(target1, target1 + '\n                    ' + addition1)
        
    # Add AMC to service menu
    if 'ticket_list' not in content:
        target2 = '<li><a href="{% url \'service_history\'  %}" class="nav-link">Service History</a></li>'
        addition2 = '<li><a href="{% url \'ticket_list\' %}" class="nav-link text-danger">AMC / Helpdesk</a></li>'
        content = content.replace(target2, target2 + '\n                    ' + addition2)
        
    # Add Subcontractor Portal to project menu
    if 'subcontractor_dashboard' not in content:
        target3 = '<li><a href="{% url \'gallery_projects\' %}" class="nav-link">Project Gallery</a></li>'
        addition3 = '<li><a href="{% url \'subcontractor_dashboard\' %}" class="nav-link text-info">Subcontractor Portal</a></li>'
        content = content.replace(target3, target3 + '\n                    ' + addition3)

    with open(eng_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 3. Update staff_sidebar.html
staff_path = os.path.join(base_path, 'staff_sidebar.html')
if os.path.exists(staff_path):
    with open(staff_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'subcontractor_dashboard' not in content:
        target = '<li class="sidebar-heading mt-3 text-muted small text-uppercase">System</li>'
        addition = '''<!-- SUBCONTRACTOR -->
        <li class="nav-item">
            <a href="{% url 'subcontractor_dashboard' %}" class="nav-link d-flex align-items-center">
                <i class="bi bi-tools nav-icon text-warning"></i>
                <span class="link-text ms-2">Subcontractor Portal</span>
            </a>
        </li>\n\n        '''
        content = content.replace(target, addition + target)
        with open(staff_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('Updated sidebars successfully.')
