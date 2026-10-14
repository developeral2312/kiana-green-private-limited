import codecs
with codecs.open('users/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_statement = "from django.views.decorators.http import require_POST\r\n"
if import_statement not in content:
    content = import_statement + content

target1 = "@login_required(login_url=\"/users/login\")\r\ndef approve_request(request, pk):"
replacement1 = "@login_required(login_url=\"/users/login\")\r\n@require_POST\r\ndef approve_request(request, pk):"
content = content.replace(target1, replacement1)

target2 = "@login_required(login_url=\"/users/login\")\r\ndef reject_request(request, pk):"
replacement2 = "@login_required(login_url=\"/users/login\")\r\n@require_POST\r\ndef reject_request(request, pk):"
content = content.replace(target2, replacement2)

target1_lf = "@login_required(login_url=\"/users/login\")\ndef approve_request(request, pk):"
replacement1_lf = "@login_required(login_url=\"/users/login\")\n@require_POST\ndef approve_request(request, pk):"
content = content.replace(target1_lf, replacement1_lf)

target2_lf = "@login_required(login_url=\"/users/login\")\ndef reject_request(request, pk):"
replacement2_lf = "@login_required(login_url=\"/users/login\")\n@require_POST\ndef reject_request(request, pk):"
content = content.replace(target2_lf, replacement2_lf)

with codecs.open('users/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
