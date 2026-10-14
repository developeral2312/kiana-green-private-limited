from .models import Task, InstallationTask
from datetime import date

def task_processor(request):
    pending = 0
    overdue = 0
    todays = 0
    task_count = 0

    if request.user.is_authenticated:
        today = date.today()

        tasks = Task.objects.filter(assigned_to=request.user)
        itasks = InstallationTask.objects.filter(assigned_to=request.user)

        pending = (
            tasks.filter(status__in=['in_progress', 'new']).count() +
            itasks.filter(status__in=['in_progress', 'new']).count()
        )
        overdue = (
            tasks.filter(due_date__lt=today).exclude(status='completed').count() +
            itasks.filter(due_date__lt=today).exclude(status='completed').count()
        )
        todays = (
            tasks.filter(due_date=today).exclude(status='completed').count() +
            itasks.filter(due_date=today).exclude(status='completed').count()
        )
        task_count = pending

    context = {
        'pending': pending,
        'overdue': overdue,
        'todays': todays,
        'task_count': task_count,
    }

    return context