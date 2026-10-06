import os
import shutil

# 1. Update Logo
source_logo = r"C:\Users\dell\.gemini\antigravity-ide\brain\395c4b23-e48a-4002-bd6c-f4393b077b4b\.user_uploaded\media_1791186166748.png"
dest_logo1 = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images\logo1.png"
dest_logo2 = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\images\logo.png"

try:
    if os.path.exists(source_logo):
        shutil.copy(source_logo, dest_logo1)
        shutil.copy(source_logo, dest_logo2)
        print("Logo updated successfully.")
    else:
        print(f"Source logo not found at: {source_logo}")
except Exception as e:
    print(f"Error copying logo: {e}")

# 2. Update Text in templates
directories = [
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates",
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\public",
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\projects",
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\users",
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\finance",
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\procurement",
    r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\crm"
]

def replace_in_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
    
    # Specific replacements
    new_content = content.replace('<b>Zyphora</b><b class="text-solar">SOLAR</b>', '<b>Kiana Green</b><b class="text-solar"> PVT LTD</b>')
    new_content = new_content.replace('<strong>Zyphora</strong><span style="color:orange;">Solar</span>', '<strong>Kiana Green</strong><span style="color:orange;"> Pvt Ltd</span>')
    
    # General replacements
    new_content = new_content.replace("Zyphora Solar", "Kiana Green Private Limited")
    new_content = new_content.replace("ZYPHORA SOLAR", "KIANA GREEN PRIVATE LIMITED")
    new_content = new_content.replace("zyphora Solar", "Kiana Green Private Limited")
    new_content = new_content.replace("Zyphora", "Kiana Green")
    new_content = new_content.replace("zyphorasolar.com", "kianagreen.com")
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

count = 0
for d in directories:
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith(".html") or file.endswith(".py"):
                if replace_in_file(os.path.join(root, file)):
                    count += 1

print(f"Updated {count} files with new brand name.")
