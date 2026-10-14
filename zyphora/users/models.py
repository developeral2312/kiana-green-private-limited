from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone



class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('admin', 'Director / Admin'),
        ('manager', 'Sales Manager'),
        ('sales','Sales Executive'),
        ('accountant', 'Accounts'),
        ('procurement', 'Procurement'),
        ('engineer', 'Installer / Engineer'),
        ('staff', 'Staff'),
        ('liaison','Liaison Officer'),
        ('subcontractor', 'Sub-Contractor / Vendor'),
        ('partner', 'Channel Partner / Dealer'),
        ('custom', 'Custom (Exception Based)')
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    must_change_password = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def get_full_name(self):
        full = super().get_full_name()
        if full and full.strip():
            return full.strip()
        if hasattr(self, 'employee') and self.employee and self.employee.name:
            return self.employee.name.strip()
        return self.username

    def __str__(self):
        if hasattr(self, 'employee') and self.employee and self.employee.name and self.employee.name.strip() != self.username:
            return f"{self.username} ({self.employee.name})"
        full = super().get_full_name()
        if full and full.strip() and full.strip() != self.username:
            return f"{self.username} ({full.strip()})"
        return self.username



class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee")
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='employees', blank=True, null=True)

    name = models.CharField(max_length=50,null=True,blank=True)
    phone = models.CharField(max_length=15,null=True,blank=True)
    address = models.TextField(blank=True,null=True)
    designation = models.CharField(max_length=50,null=True,blank=True)
    date_joined = models.DateField(null=True)
    is_active = models.BooleanField(default=True)

    # Role-specific fields
    specialization = models.CharField(max_length=100, blank=True,null=True)       # For engineers
    access_level = models.CharField(max_length=20, blank=True,null=True)          # For accountants
    supervisor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role__in': ['admin', 'manager', 'engineer']},
        related_name='supervised_staff'
    )  # For staff, sales & field teams

    def save(self, *args, **kwargs):
        if not self.employee_id:
            import re
            existing_ids = Employee.objects.filter(employee_id__isnull=False).values_list('employee_id', flat=True)
            max_num = 0
            for eid in existing_ids:
                nums = re.findall(r'\d+', str(eid))
                if nums:
                    try:
                        num_val = int(nums[-1])
                        if num_val > max_num:
                            max_num = num_val
                    except ValueError:
                        pass
            self.employee_id = f"EMP-{max_num + 1:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        emp_id = self.employee_id or f"EMP-{self.id:03d}"
        username = self.user.username if self.user else "Unknown"
        if self.name and self.name.strip() and self.name.strip().lower() != username.lower():
            return f"{emp_id} - {username} ({self.name})"
        return f"{emp_id} - {username}"


class EmployeeException(models.Model):
    """
    Exception-based access control granting specific module access to an employee.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='access_exceptions')
    module = models.CharField(max_length=50) # e.g., 'Costing', 'Inventory', 'CRM'
    access_type = models.CharField(max_length=20) # e.g., 'View', 'Edit', 'Approve'
    valid_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.module} ({self.access_type})"
    


class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150,null=True)
    message = models.TextField()
    category = models.CharField(max_length=50,null=True)
    link = models.URLField(blank=True, null=True) 
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def icon(self):
        if getattr(self, '_custom_icon', None):
            return self._custom_icon
        cat = (self.category or '').lower()
        if 'task' in cat:
            return 'bi-check2-square text-primary'
        elif 'lead' in cat or 'crm' in cat:
            return 'bi-person-plus text-info'
        elif 'employee' in cat:
            return 'bi-person-badge text-warning'
        elif 'finance' in cat or 'payment' in cat or 'invoice' in cat or 'cost' in cat:
            return 'bi-currency-rupee text-success'
        elif 'procurement' in cat or 'material' in cat or 'stock' in cat:
            return 'bi-box-seam text-secondary'
        elif 'project' in cat:
            return 'bi-kanban text-primary'
        elif 'approval' in cat:
            return 'bi-shield-check text-warning'
        elif 'alert' in cat or 'escalat' in cat:
            return 'bi-exclamation-triangle-fill text-danger'
        return 'bi-bell-fill text-primary'

    @icon.setter
    def icon(self, value):
        self._custom_icon = value

    @property
    def badge(self):
        if getattr(self, '_custom_badge', None):
            return self._custom_badge
        cat = (self.category or '').lower()
        if 'task' in cat:
            return 'bg-primary text-white'
        elif 'lead' in cat or 'crm' in cat:
            return 'bg-info text-dark'
        elif 'employee' in cat:
            return 'bg-warning text-dark'
        elif 'finance' in cat or 'payment' in cat or 'invoice' in cat:
            return 'bg-success text-white'
        elif 'procurement' in cat:
            return 'bg-secondary text-white'
        elif 'alert' in cat or 'escalat' in cat:
            return 'bg-danger text-white'
        return 'bg-light text-dark border'

    @badge.setter
    def badge(self, value):
        self._custom_badge = value

    def __str__(self):
        return f'Notification to {self.recipient.username} - Read: {self.is_read}'
# -------------------------------
# Employee Performance / KPI
# -------------------------------
class EmployeeKPI(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='kpis')
    month = models.DateField()
    target_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    achieved_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    leads_assigned = models.IntegerField(default=0)
    leads_converted = models.IntegerField(default=0)
    projects_completed_on_time = models.IntegerField(default=0)
    projects_delayed = models.IntegerField(default=0)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee.user.username} - KPI {self.month.strftime('%b %Y')}"


# ===============================
# CONFIGURABLE APPROVAL ENGINE
# ===============================
class ApprovalRule(models.Model):
    MODULE_CHOICES = (
        ('discount', 'Discount'),
        ('purchase', 'Purchase Order'),
        ('payment', 'Payment Release'),
        ('expense', 'Expense Claim'),
        ('costing', 'Costing Approval'),
        ('design', 'Design Approval'),
    )
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    required_role = models.CharField(max_length=50, choices=CustomUser.ROLE_CHOICES)

    def __str__(self):
        return f"{self.module} ({self.min_amount} - {self.max_amount}) -> {self.required_role}"

class ApprovalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    rule = models.ForeignKey(ApprovalRule, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="requested_approvals")
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="granted_approvals")
    reference_id = models.IntegerField(help_text="ID of the PO, Expense, or Quotation")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rule.module} Approval for {self.amount} ({self.status})"

# ===============================
# HR & STAFF MANAGEMENT
# ===============================

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    sign_in = models.TimeField(null=True, blank=True)
    sign_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.status})"

class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('earned', 'Earned Leave'),
        ('unpaid', 'Unpaid Leave'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    
    applied_on = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} ({self.status})"


