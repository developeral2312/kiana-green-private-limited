with open('projects/views.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# FEATURE 22: HELPDESK & TICKETS
# ===============================

@login_required(login_url='/users/login')
def ticket_list(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    
    # Simple status filtering
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
        
    return render(request, 'dashboard/projects/ticket_list.html', {'tickets': tickets})

@login_required(login_url='/users/login')
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        # Simple status and notes update
        new_status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        if new_status:
            ticket.status = new_status
            if new_status == 'resolved' or new_status == 'closed':
                ticket.resolved_at = timezone.now()
        
        if notes:
            ticket.resolution_notes += f"\\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
            
        ticket.save()
        messages.success(request, "Ticket updated successfully.")
        return redirect('view_ticket', ticket_id=ticket.id)
        
    return render(request, 'dashboard/projects/view_ticket.html', {'ticket': ticket})


# ===============================
# FEATURE 23: SUB-CONTRACTOR PORTAL
# ===============================

@login_required(login_url='/users/login')
def subcontractor_dashboard(request):
    # Ensure user has subcontractor role (or is admin/engineer for testing)
    if request.user.role not in ['subcontractor', 'admin', 'engineer']:
        messages.error(request, "Access denied. Sub-contractors only.")
        return redirect('dashboard')
        
    tasks = SubcontractorTask.objects.filter(subcontractor=request.user).order_by('deadline')
    
    # Separate by status
    pending_tasks = tasks.exclude(status__in=['completed', 'verified'])
    completed_tasks = tasks.filter(status__in=['completed', 'verified'])
    
    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks
    }
    return render(request, 'dashboard/projects/subcontractor_dashboard.html', context)

@login_required(login_url='/users/login')
def mark_task_completed(request, task_id):
    task = get_object_or_404(SubcontractorTask, id=task_id, subcontractor=request.user)
    
    if request.method == 'POST':
        notes = request.POST.get('notes')
        photo = request.FILES.get('photo')
        
        task.completion_notes = notes
        if photo:
            task.photo_proof = photo
            
        task.status = 'completed'
        task.save()
        messages.success(request, f"Task '{task.task_name}' submitted for verification.")
        
    return redirect('subcontractor_dashboard')
''')
print("Appended Support and Subcontractor views")
