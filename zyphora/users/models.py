from django.db import models
from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
        ('accountant', 'Accountant'),
        ('sales','Sales'),
        ('staff', 'Staff'),
        ('liaison','Liaison Officer')
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    must_change_password = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)



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
        limit_choices_to={'role__in': ['admin','engineer']},
        related_name='supervised_staff'
    )  # For staff

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last_emp = Employee.objects.filter(employee_id__startswith="EMP-").order_by('-id').first()
            if last_emp and last_emp.employee_id:
                try:
                    last_num = int(last_emp.employee_id.split('-')[-1])
                    new_num = last_num + 1
                except ValueError:
                    new_num = 1
            else:
                new_num = 1
            self.employee_id = f"EMP-{new_num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.user.username}"


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
