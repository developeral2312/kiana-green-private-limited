import os
import glob

include_dir = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include"

# 1. Update logo in all sidebars
sidebar_files = glob.glob(os.path.join(include_dir, "*_sidebar.html"))

old_logo_block_1 = """        <div class="sidebar-logo d-flex align-items-center">
            <img src="{% static 'images/logo1.png' %}"
                class="sidebar-logo-full img-fluid"
                alt="Kiana Green Private Limited Logo">
            <img src="{% static 'images/favicon.ico' %}"
                class="sidebar-logo-mini"
                alt="Kiana Green Icon">
        </div>"""

old_logo_block_2 = """        <div class="sidebar-logo d-flex align-items-center">
            <img src="{% static 'images/logo1.png' %}"
                class="sidebar-logo-full img-fluid"
                alt="Lumora Solar Logo">
            <img src="{% static 'images/favicon.ico' %}"
                class="sidebar-logo-mini"
                alt="Lumora Solar Icon">
        </div>"""

new_logo_block = """        <!-- Custom HTML Text Logo -->
        <div class="sidebar-logo d-flex align-items-center" style="gap: 8px;">
            <!-- Keeping only the small leaf/sun icon -->
            <img src="{% static 'images/logo1.png' %}" 
                 class="img-fluid" 
                 alt="Icon" 
                 style="height: 38px; width: 38px; object-fit: contain;">
            
            <div class="sidebar-logo-full d-flex flex-column justify-content-center" style="line-height: 1;">
                <span style="font-size: 1.3rem; font-weight: 800; color: #1f4e3d; letter-spacing: 0.5px; margin-bottom: 2px;">KIANA</span>
                <span style="font-size: 0.75rem; font-weight: 600; color: #4ade80; letter-spacing: 2px;">GREEN</span>
            </div>
        </div>"""

for filepath in sidebar_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "sidebar-logo d-flex align-items-center" in content:
        # We need to replace whatever the logo block is with the new one
        # Because we don't know the exact alt tags, let's use regex or string replace
        # Let's just find the start and end of the logo block
        start_idx = content.find('<div class="sidebar-logo')
        end_idx = content.find('</div>', start_idx) + 6
        
        if start_idx != -1:
            old_block = content[start_idx:end_idx]
            content = content.replace(old_block, new_logo_block)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated logo in {os.path.basename(filepath)}")

# 2. Update topnavbar.html height
topnav_path = os.path.join(include_dir, "topnavbar.html")
with open(topnav_path, "r", encoding="utf-8") as f:
    topnav_content = f.read()

# adding py-3 padding to increase height
old_nav_class = '<nav class="navbar navbar-expand-lg bg-body shadow-sm sticky-top">'
new_nav_class = '<nav class="navbar navbar-expand-lg bg-body shadow-sm sticky-top py-3">'

if old_nav_class in topnav_content:
    topnav_content = topnav_content.replace(old_nav_class, new_nav_class)
    with open(topnav_path, "w", encoding="utf-8") as f:
        f.write(topnav_content)
    print("Updated topnavbar height.")
