from django.db.models import Q
from projects.models import Project
from users.models import Employee


def get_user_accessible_projects(user):
    """
    Returns the queryset of projects accessible by the given user based strictly
    on their role and active assignments. Ensures bulletproof RBAC across all forms,
    dropdowns, and views.
    """
    if not user or not user.is_authenticated:
        return Project.objects.none()

    # 1. Superuser, Admin & Executive Director: full system visibility
    if user.is_superuser or user.role in ['admin', 'director']:
        return Project.objects.all().order_by('-created_at')

    # 2. Sales Executive / Salesman
    if user.role == 'sales':
        return Project.objects.filter(lead__assigned_to=user).distinct().order_by('-created_at')

    # 3. Sales Manager
    if user.role == 'manager':
        # Strictly show projects converted from leads assigned to this manager or their direct leads
        return Project.objects.filter(
            Q(lead__assigned_to=user) | Q(lead__notes__icontains=user.username)
        ).distinct().order_by('-created_at')

    # 4. Site Engineer / Installer
    if user.role == 'engineer':
        employee = Employee.objects.filter(user=user).first()
        if employee:
            return Project.objects.filter(
                Q(engineer=employee) | 
                Q(installation_tasks__assigned_to=user) |
                Q(site_visits__engineer=user) |
                Q(lead__site_visits__engineer=user)
            ).distinct().order_by('-created_at')
        return Project.objects.filter(
            Q(installation_tasks__assigned_to=user) |
            Q(site_visits__engineer=user) |
            Q(lead__site_visits__engineer=user)
        ).distinct().order_by('-created_at')

    # 5. Sub-Contractor / Vendor
    if user.role == 'subcontractor':
        return Project.objects.filter(subcontractor_tasks__subcontractor=user).distinct().order_by('-created_at')

    # 6. Internal Site Technician / Staff
    if user.role == 'staff':
        return Project.objects.filter(installation_tasks__assigned_to=user).distinct().order_by('-created_at')

    # 7. Liaison Officer
    if user.role == 'liaison':
        return Project.objects.filter(
            Q(licensing_tasks__assigned_to=user) | Q(licensing__assigned_to=user)
        ).distinct().order_by('-created_at')

    # 8. Channel Partner / Dealer
    if user.role == 'partner':
        return Project.objects.filter(lead__channel_partner__user=user).distinct().order_by('-created_at')

    # 9. Accountant / Finance Officer
    if user.role == 'accountant':
        return Project.objects.all().order_by('-created_at')

    # 10. Procurement / Warehouse Officer
    if user.role == 'procurement':
        return Project.objects.all().order_by('-created_at')

    # Fallback: strictly projects with any direct assignment to this user
    return Project.objects.filter(
        Q(installation_tasks__assigned_to=user) |
        Q(subcontractor_tasks__subcontractor=user) |
        Q(lead__assigned_to=user)
    ).distinct().order_by('-created_at')
