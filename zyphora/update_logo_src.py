import os
import glob

include_dir = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include"
sidebar_files = glob.glob(os.path.join(include_dir, "*_sidebar.html"))

for filepath in sidebar_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "logo1.png" in content:
        content = content.replace("logo1.png", "logo_transparent.png")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")
