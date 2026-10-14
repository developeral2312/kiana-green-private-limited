import os
file_path = 'finance/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "@login_required(login_url='/users/login')\ndef edit_project_costing(request, project_id):"

if target in content:
    idx = content.find(target)
    new_content = content[:idx] + """@login_required(login_url='/users/login')
def edit_project_costing(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    costing, created = ProjectCosting.objects.get_or_create(project=project)
    
    if request.method == "POST":
        form = ProjectCostingForm(request.POST, instance=costing)
        if form.is_valid():
            costing = form.save(commit=False)
            costing.updated_by = request.user
            costing.save()
            messages.success(request, 'Project Costing & Margin calculated successfully.')
            return redirect("project_detail", pid=project.id)
    else:
        form = ProjectCostingForm(instance=costing)
        
    context = {
        "form": form,
        "project": project,
        "costing": costing
    }
    return render(request, "dashboard/finance/project_costing.html", context)
"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated!")
else:
    print("Target not found. Doing fallback target search.")
    target2 = "@login_required(login_url='/users/login')\r\ndef edit_project_costing(request, project_id):"
    if target2 in content:
        idx = content.find(target2)
        new_content = content[:idx] + """@login_required(login_url='/users/login')
def edit_project_costing(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    costing, created = ProjectCosting.objects.get_or_create(project=project)
    
    if request.method == "POST":
        form = ProjectCostingForm(request.POST, instance=costing)
        if form.is_valid():
            costing = form.save(commit=False)
            costing.updated_by = request.user
            costing.save()
            messages.success(request, 'Project Costing & Margin calculated successfully.')
            return redirect("project_detail", pid=project.id)
    else:
        form = ProjectCostingForm(instance=costing)
        
    context = {
        "form": form,
        "project": project,
        "costing": costing
    }
    return render(request, "dashboard/finance/project_costing.html", context)
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated with target2!")
    else:
        print("Could not find target anywhere!")
