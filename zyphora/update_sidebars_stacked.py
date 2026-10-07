import os
import re

include_dir = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include"

new_logo_div = """<div class="sidebar-logo d-flex flex-column align-items-center justify-content-center" style="width: 90px; margin: 0 auto; padding: 5px 0;">
    <img src="{% static 'images/logo1.png' %}" 
         class="img-fluid" 
         alt="Logo" 
         style="width: 100%; height: auto;">
    
    <div style="width: 100%; text-align: right; font-weight: 800; color: #2ecc71; font-size: 1.05rem; letter-spacing: 1.5px; margin-top: 2px; line-height: 1; padding-right: 2px;">GREEN</div>
</div>"""

# Find all sidebars
for f in os.listdir(include_dir):
    if f.endswith('sidebar.html'):
        path = os.path.join(include_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        pattern = re.compile(r'<div class="sidebar-logo d-flex align-items-center".*?</div>\s*</div>', re.DOTALL)
        content = pattern.sub(new_logo_div, content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

# Update footer.html
footer_path = os.path.join(include_dir, 'footer.html')
with open(footer_path, 'r', encoding='utf-8') as f:
    footer_content = f.read()

new_footer_logo = """<div class="mb-4" style="width: 110px;">
  <img src="{% static 'images/logo1.png' %}" alt="Kiana Logo" style="width: 100%; height: auto;">
  <div style="width: 100%; text-align: right; font-weight: 800; color: #2ecc71; font-size: 1.25rem; letter-spacing: 1.5px; margin-top: 2px; padding-right: 2px;">GREEN</div>
</div>"""

footer_pattern = re.compile(r'<div class="d-flex align-items-center mb-4">.*?</div>\s*</div>', re.DOTALL)
footer_content = footer_pattern.sub(new_footer_logo, footer_content, count=1)

with open(footer_path, 'w', encoding='utf-8') as f:
    f.write(footer_content)

print("Updated all sidebars and footer to stacked logo.")
