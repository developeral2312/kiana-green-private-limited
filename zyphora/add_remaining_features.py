import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# 1. PROCUREMENT: BOM & Kit Configuration + RFQ
# ---------------------------------------------------------
procurement_models_path = os.path.join(BASE_DIR, 'procurement', 'models.py')
procurement_code = """

# ===============================
# BOM & KIT CONFIGURATION
# ===============================
class KitConfiguration(models.Model):
    name = models.CharField(max_length=200)
    system_size_kw = models.FloatField()
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_cost(self):
        return sum(item.material.unit_price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"{self.name} (v{self.version})"

class KitMaterial(models.Model):
    kit = models.ForeignKey(KitConfiguration, on_delete=models.CASCADE, related_name="items")
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.material.name} for {self.kit.name}"

# ===============================
# PROCUREMENT INTELLIGENCE (RFQ)
# ===============================
class RequestForQuotation(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    )
    title = models.CharField(max_length=255)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_required = models.IntegerField()
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RFQ: {self.title}"

class VendorQuotation(models.Model):
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name="quotations")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quoted_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField()
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quoted_price_per_unit * self.rfq.quantity_required

    def __str__(self):
        return f"{self.vendor.name} for {self.rfq.title}"
"""
with open(procurement_models_path, 'a', encoding='utf-8') as f:
    f.write(procurement_code)


# ---------------------------------------------------------
# 2. FINANCE: Payment Milestone Tracker
# ---------------------------------------------------------
finance_models_path = os.path.join(BASE_DIR, 'finance', 'models.py')
finance_code = """

# ===============================
# PAYMENT MILESTONE TRACKER
# ===============================
class PaymentMilestone(models.Model):
    MILESTONE_CHOICES = (
        ('booking', 'Booking / Advance'),
        ('dispatch', 'Material Dispatch'),
        ('installation', 'Installation Completion'),
        ('commissioning', 'Commissioning & Net-Metering'),
        ('final', 'Final Payment'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    milestone_type = models.CharField(max_length=50, choices=MILESTONE_CHOICES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g. 50.00 for 50%")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_received = models.ForeignKey('finance.Payment', on_delete=models.SET_NULL, null=True, blank=True)
    
    def is_overdue(self):
        return self.status == 'pending' and timezone.now().date() > self.due_date

    def __str__(self):
        return f"{self.get_milestone_type_display()} - {self.project.title}"
"""
with open(finance_models_path, 'a', encoding='utf-8') as f:
    f.write(finance_code)


# ---------------------------------------------------------
# 3. USERS/CORE: Configurable Approval Engine
# ---------------------------------------------------------
users_models_path = os.path.join(BASE_DIR, 'users', 'models.py')
users_code = """

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
"""
with open(users_models_path, 'a', encoding='utf-8') as f:
    f.write(users_code)

print("Files updated successfully. Now run makemigrations and migrate.")
