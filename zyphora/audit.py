import os
import re

base_path = r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora'
templates_path = os.path.join(base_path, 'templates')
urls_files = []

for root, dirs, files in os.walk(base_path):
    if 'urls.py' in files and 'ven' not in root:
        urls_files.append(os.path.join(root, 'urls.py'))

# 1. Collect all defined URL names
defined_url_names = set()
for uf in urls_files:
    with open(uf, 'r', encoding='utf-8') as f:
        content = f.read()
        # look for name='...'
        matches = re.findall(r"name\s*=\s*['\"]([^'\"]+)['\"]", content)
        defined_url_names.update(matches)

# Add some built-ins or implicitly known ones
defined_url_names.update(['admin:index', 'login', 'logout'])

missing_urls = set()
missing_csrf = []

# 2. Check templates for used URL names and missing CSRF
for root, dirs, files in os.walk(templates_path):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check CSRF
                forms = re.findall(r'<form[^>]*method=["\']post["\'][^>]*>', content, re.IGNORECASE)
                if forms and '{% csrf_token %}' not in content:
                    missing_csrf.append(filepath)

                # Check URLs
                used_urls = re.findall(r"{%\s*url\s+['\"]([^'\"]+)['\"]", content)
                for u in used_urls:
                    if u not in defined_url_names:
                        missing_urls.add((u, filepath))

print("Audit Results:")
print("Missing CSRF Tokens in forms with method POST:")
for p in missing_csrf:
    print(" -", p)
    
print("\nMissing URLs referenced in templates:")
for u, path in missing_urls:
    print(f" - {u} in {path}")
