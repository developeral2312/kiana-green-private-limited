import os

def replace_in_files(directory):
    for root, dirs, files in os.walk(directory):
        if 'ven' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.html', '.css', '.js', '.txt', '.md')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    # Replace user-facing text
                    new_content = new_content.replace('Zyphora Solar', 'Kiana Green')
                    new_content = new_content.replace('Zyphora', 'Kiana Green')
                    new_content = new_content.replace('zyphora-', 'kiana-')
                    new_content = new_content.replace('zyphora_', 'kiana_')
                    
                    # Fix django internal stuff that might have been accidentally changed by the above naive replacement
                    # Wait, if I replace 'zyphora-', it changes class="zyphora-cta" to class="kiana-cta". That's good.
                    
                    # Only write if changed
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated {path}")
                except Exception as e:
                    pass

if __name__ == '__main__':
    replace_in_files(r'c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora')
