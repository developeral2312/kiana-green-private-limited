import os

# 1. Clean admin.html
admin_html_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\dashboard\admin\admin.html"
with open(admin_html_path, "r", encoding="utf-8") as f:
    admin_html = f.read()

# Split by the comment block and take the first part
marker = "<!-- AI AGENT WIDGET -->"
if marker in admin_html:
    admin_html = admin_html.split(marker)[0]
    with open(admin_html_path, "w", encoding="utf-8") as f:
        f.write(admin_html.rstrip() + "\n\n{% endblock %}\n")
    print("Removed AI Agent from admin.html")

# 2. Clean urls.py
urls_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\users\urls.py"
with open(urls_path, "r", encoding="utf-8") as f:
    urls_lines = f.readlines()

new_urls_lines = [line for line in urls_lines if "ai_agent_query" not in line]
with open(urls_path, "w", encoding="utf-8") as f:
    f.writelines(new_urls_lines)
print("Removed AI Agent from urls.py")

# 3. Clean views.py
views_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\users\views.py"
with open(views_path, "r", encoding="utf-8") as f:
    views_content = f.read()

view_marker = "@login_required(login_url='/users/login')\n@require_POST\ndef ai_agent_query(request):"
if view_marker in views_content:
    views_content = views_content.split(view_marker)[0]
    with open(views_path, "w", encoding="utf-8") as f:
        f.write(views_content.rstrip() + "\n")
    print("Removed AI Agent from views.py")
