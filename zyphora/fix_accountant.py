import os

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include'
acc_path = os.path.join(base_path, 'accountant_sidebar.html')

if os.path.exists(acc_path):
    with open(acc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'approval_dashboard' not in content:
        # Add after dashboard
        target = '<li class="sidebar-heading mt-3 text-muted small">FINANCE MANAGEMENT</li>'
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
        with open(acc_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('Accountant sidebar fixed.')
