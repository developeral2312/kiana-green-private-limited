with open('projects/views.py', 'a', encoding='utf-8') as f:
    f.write('''

@login_required(login_url='/users/login')
def project_equipment_list(request, pid):
    project = get_object_or_404(Project, pk=pid)
    equipments = project.equipments.all().order_by('-installation_date')
    
    context = {
        'project': project,
        'equipments': equipments,
        'panel_count': equipments.filter(category='panel').count(),
        'inverter_count': equipments.filter(category='inverter').count(),
        'battery_count': equipments.filter(category='battery').count()
    }
    return render(request, 'dashboard/projects/equipment_list.html', context)

@login_required(login_url='/users/login')
def add_project_equipment(request, pid):
    project = get_object_or_404(Project, pk=pid)
    from .forms import EquipmentSerialForm
    
    if request.method == "POST":
        form = EquipmentSerialForm(request.POST)
        if form.is_valid():
            equip = form.save(commit=False)
            equip.project = project
            equip.added_by = request.user
            equip.save()
            messages.success(request, f"{equip.get_category_display()} Serial '{equip.serial_number}' successfully tracked.")
            return redirect('project_equipment', pid=project.id)
    else:
        form = EquipmentSerialForm()
        
    return render(request, 'dashboard/projects/add_equipment.html', {'project': project, 'form': form})
''')
print('Appended views')
