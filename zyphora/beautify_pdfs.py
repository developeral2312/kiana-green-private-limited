import os
import re

DASHBOARD_DIR = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\dashboard"

beautiful_style = """<style>
    @page {
        size: a4 portrait;
        margin: 2cm;
    }
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 13px;
        color: #333;
        line-height: 1.6;
        margin: 0;
        padding: 0;
    }
    .header-table {
        width: 100%;
        border-bottom: 3px solid #2ecc71;
        padding-bottom: 15px;
        margin-bottom: 30px;
        border-collapse: collapse;
    }
    .header-table td {
        border: none;
        padding: 0;
        vertical-align: top;
    }
    .company-info {
        font-size: 12px;
        color: #7f8c8d;
        margin-top: 5px;
        line-height: 1.4;
    }
    .company-name {
        font-size: 22px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 10px;
    }
    h3 {
        font-size: 24px;
        font-weight: bold;
        color: #2ecc71;
        text-transform: uppercase;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    h4 {
        color: #2c3e50;
        background-color: #f8f9fa;
        padding: 8px 10px;
        border-left: 4px solid #2ecc71;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    p {
        margin: 5px 0;
    }
    .section {
        margin-bottom: 25px;
    }
    table.data-table, table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    th, td {
        border: 1px solid #e0e0e0;
        padding: 10px 12px;
        text-align: left;
    }
    th {
        background-color: #2ecc71;
        color: #fff;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.5px;
    }
    tr:nth-child(even) {
        background-color: #fbfbfb;
    }
    .total-row td, td.right strong {
        font-weight: bold;
        color: #2c3e50;
    }
    .right {
        text-align: right;
    }
    .footer {
        position: fixed;
        bottom: 10px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 10px;
        color: #95a5a6;
        border-top: 1px solid #eee;
        padding-top: 10px;
    }
</style>"""

beautiful_header = """<table class="header-table">
    <tr>
        <td style="width: 60%; vertical-align: top;">
            <div style="width: 120px;">
                <img src="{% static 'images/logo.png' %}" style="width: 100%; height: auto; display: block;">
                <div style="width: 100%; text-align: right; font-weight: 800; color: #2ecc71; font-size: 1.3rem; letter-spacing: 1.5px; margin-top: 2px; text-transform: uppercase; padding-right: 2px;">GREEN</div>
            </div>
            <div class="company-info" style="margin-top: 10px;">
                Palakkad, Kerala<br>
                Phone: +91 XXXXX XXXXX<br>
                GSTIN: 32XXXXXXXXXXXXX
            </div>
        </td>
        <td style="width: 40%; text-align: right; vertical-align: bottom;">
            <!-- Document specific title can be placed below if needed -->
        </td>
    </tr>
</table>"""

beautiful_header_no_static = """<table class="header-table">
    <tr>
        <td style="width: 60%; vertical-align: top;">
            <div style="width: 120px;">
                <img src="/static/images/logo.png" style="width: 100%; height: auto; display: block;">
                <div style="width: 100%; text-align: right; font-weight: 800; color: #2ecc71; font-size: 1.3rem; letter-spacing: 1.5px; margin-top: 2px; text-transform: uppercase; padding-right: 2px;">GREEN</div>
            </div>
            <div class="company-info" style="margin-top: 10px;">
                Palakkad, Kerala<br>
                Phone: +91 XXXXX XXXXX<br>
                GSTIN: 32XXXXXXXXXXXXX
            </div>
        </td>
        <td style="width: 40%; text-align: right; vertical-align: bottom;">
            <!-- Document specific title can be placed below if needed -->
        </td>
    </tr>
</table>"""

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace <style> block
    style_pattern = re.compile(r'<style>.*?</style>', re.DOTALL)
    if style_pattern.search(content):
        content = style_pattern.sub(beautiful_style, content)
    elif '</head>' in content:
        content = content.replace('</head>', beautiful_style + '\n</head>')

    # Replace .header div block
    header_pattern = re.compile(r'<div class="header">.*?</div>\s*<div style="position:fixed.*?</div>', re.DOTALL)
    header_pattern2 = re.compile(r'<div class="header">.*?</div>', re.DOTALL)
    
    if "{% load static %}" in content or "purchase_pdf.html" in file_path:
        header_repl = beautiful_header
    else:
        # Some PDFs use {{ STATIC_ROOT }}, let's just use /static/images/logo.png or {{ STATIC_ROOT }}/images/logo.png
        if '{{ STATIC_ROOT }}' in content:
            header_repl = beautiful_header_no_static.replace('/static/images/logo.png', '{{ STATIC_ROOT }}/images/logo.png')
        else:
            header_repl = beautiful_header_no_static

    if header_pattern.search(content):
        content = header_pattern.sub(header_repl, content)
    elif header_pattern2.search(content):
        content = header_pattern2.sub(header_repl, content)

    # Convert existing tables to data-table if not already
    content = content.replace('<table border="1">', '<table class="data-table">')
    
    # Remove old inline table styles
    content = re.sub(r'<table[^>]*>', '<table>', content)

    # Check for {% load static %} if needed
    if "{% static" in header_repl and "{% load static %}" not in content:
        content = "{% load static %}\n" + content

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
for filename in os.listdir(DASHBOARD_DIR):
    if filename.endswith("pdf.html"):
        print(f"Updating {filename}")
        process_file(os.path.join(DASHBOARD_DIR, filename))
