import os
import re

include_dir = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include"

# Find all sidebars
for f in os.listdir(include_dir):
    if f.endswith('sidebar.html'):
        path = os.path.join(include_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace the sidebar-logo div
        new_logo_div = """<div class="sidebar-logo d-flex align-items-center" style="gap: 8px;">
            <img src="{% static 'images/logo1.png' %}" 
                 class="img-fluid" 
                 alt="Logo" 
                 style="height: 35px; width: auto; object-fit: contain;">
            
            <div class="sidebar-logo-full d-flex flex-column justify-content-center" style="line-height: 1;">
                <span style="font-size: 1.1rem; font-weight: 800; color: #2ecc71; letter-spacing: 0.5px; margin-bottom: 2px;">GREEN</span>
                <span style="font-size: 0.7rem; font-weight: 600; color: #4ade80; letter-spacing: 1px;">PVT. LTD.</span>
            </div>
        </div>"""
        
        # We need to replace the block starting from <div class="sidebar-logo... up to the matching closing div for sidebar-logo
        # Since regex is hard for nested divs, let's just do a string replacement for the known variants, or use regex that matches exactly.
        
        pattern = re.compile(r'<div class="sidebar-logo d-flex align-items-center".*?</div>\s*</div>', re.DOTALL)
        content = pattern.sub(new_logo_div, content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

# Update footer.html
footer_path = os.path.join(include_dir, 'footer.html')
with open(footer_path, 'r', encoding='utf-8') as f:
    footer_content = f.read()

# Current footer logo block is roughly:
# <img src="{% static 'images/logo1.png' %}" alt="Kiana Green Logo" style="width: 50px; height: auto;" class="me-3">
# <div>
#   <span style="color: #ffffff; font-size: 1.3rem; font-weight: 500; letter-spacing: 1px;">KIANA</span><br>
#   <span style="color: #2ecc71; font-size: 1.3rem; font-weight: 700; letter-spacing: 1px;">GREEN</span>
# </div>

new_footer_logo = """<div class="d-flex align-items-center mb-4">
          <img src="{% static 'images/logo1.png' %}" alt="Kiana Green Logo" style="height: 40px; width: auto;" class="me-3">
          <div>
            <span style="color: #2ecc71; font-size: 1.3rem; font-weight: 700; letter-spacing: 1px;">GREEN</span><br>
            <span style="color: #ffffff; font-size: 0.8rem; font-weight: 500; letter-spacing: 1px;">PRIVATE LIMITED</span>
          </div>
        </div>"""

# Replace the d-flex align-items-center mb-4 block
footer_pattern = re.compile(r'<div class="d-flex align-items-center mb-4">.*?</div>\s*</div>', re.DOTALL)
footer_content = footer_pattern.sub(new_footer_logo, footer_content, count=1)

with open(footer_path, 'w', encoding='utf-8') as f:
    f.write(footer_content)

print("Updated all sidebars and footer.")
