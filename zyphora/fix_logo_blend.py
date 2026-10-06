import os
import glob

include_dir = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include"
sidebar_files = glob.glob(os.path.join(include_dir, "*_sidebar.html"))

old_style = "style=\"height: 38px; width: 38px; object-fit: contain;\""
new_style = "style=\"height: 38px; width: 38px; object-fit: contain; mix-blend-mode: multiply;\""

for filepath in sidebar_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Change it back to logo1.png just in case the edges of logo_transparent were rough
    if "logo_transparent.png" in content:
        content = content.replace("logo_transparent.png", "logo1.png")
    
    # Add mix-blend-mode
    if old_style in content:
        content = content.replace(old_style, new_style)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated style in {os.path.basename(filepath)}")
