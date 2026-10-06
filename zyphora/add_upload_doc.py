import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Update views.py
views_path = os.path.join(base_dir, 'projects', 'views.py')
with open(views_path, 'a', encoding='utf-8') as f:
    f.write("""

def upload_project_document(request, pid):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=pid)
        title = request.POST.get('title')
        category = request.POST.get('category')
        file = request.FILES.get('file')
        if title and category and file:
            ProjectDocument.objects.create(
                project=project,
                title=title,
                category=category,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, 'Document uploaded successfully.')
        else:
            messages.error(request, 'Please provide title, category, and a file.')
    return redirect('view_project', pid=pid)
""")

# 2. Update urls.py
urls_path = os.path.join(base_dir, 'projects', 'urls.py')
with open(urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "path('upload-document/<int:pid>/', views.upload_project_document, name='upload_project_document')," not in content:
    content = content.replace("urlpatterns = [", "urlpatterns = [\n    path('upload-document/<int:pid>/', views.upload_project_document, name='upload_project_document'),")
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Backend updated.")
