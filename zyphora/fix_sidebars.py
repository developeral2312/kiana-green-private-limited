import os

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'

# Add Approval Engine to sales_sidebar.html (for managers)
sales_path = os.path.join(base_path, 'sales_sidebar.html')
if os.path.exists(sales_path):
    with open(sales_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'approval_dashboard' not in content:
        # Add after dashboard
        target = '<!-- WORK / TASKS -->'
        addition = '''<!-- ================= APPROVAL ENGINE ================= -->
        <li class="nav-item">
            <a href="{% url 'approval_dashboard' %}"
               class="nav-link d-flex align-items-center {% if request.resolver_match.url_name == 'approval_dashboard' %}active{% endif %}"
               data-bs-toggle="tooltip"
               data-bs-placement="right"
               title="Approvals">
                <i class="bi bi-check2-all nav-icon text-danger"></i>
                <span class="link-text ms-2">Approval Engine</span>
            </a>
        </li>\n\n        '''
        content = content.replace(target, addition + target)
        with open(sales_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Add RFQ to staff_sidebar.html (for procurement)
staff_path = os.path.join(base_path, 'staff_sidebar.html')
if os.path.exists(staff_path):
    with open(staff_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'rfq_list' not in content:
        target = '<li><a class="nav-link" href="{% url \'request_material\' %}">Request Additional Materials</a></li>'
        addition = '<li><a class="nav-link text-warning" href="{% url \'rfq_list\' %}">Vendor Bidding (RFQ)</a></li>'
        content = content.replace(target, target + '\n                    ' + addition)
        with open(staff_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('Sales and Staff sidebars fixed.')
