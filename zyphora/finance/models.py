from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from projects.models import Project
from users.models import Employee,CustomUser

class Invoice(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    invoice_number = models.CharField(max_length=100, unique=True)

    issue_date = models.DateField()

    due_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class Payment(models.Model):

    PAYMENT_METHOD = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cheque', 'Cheque'),
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD
    )

    received_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment for {self.invoice.invoice_number}"



class ExpenseReport(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    CATEGORY_CHOICES = (
        ('sales','Sales'),
        ('structure','Project - Structure'),
        ('electrical','Project - Electrical'),
        ('services','Services'),
        ('materials','Materials'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="expense_reports"
    )

    expense_date = models.DateField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    submitted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    @property
    def total_amount(self):
        return self.items.aggregate(total=Sum('amount'))['total'] or 0

    def __str__(self):
        return f"{self.project} - {self.expense_date}"
    



class ExpenseItem(models.Model):

    report = models.ForeignKey(
        ExpenseReport,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.description} - {self.amount}"
    
class ExpenseReceipt(models.Model):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name="receipts")
    file = models.FileField(upload_to="expense_receipts/")


class DesignCosting(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='design_costing' 
    )

    cost = models.DecimalField(max_digits=12, decimal_places=2)
    design_file = models.FileField(upload_to='design_costs/', null=True, blank=True)
    
    entered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Design Cost - {self.project.title}"
    






# ===============================
# PROJECT COSTING & MARGIN
# ===============================
class ProjectCosting(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='project_costing'
    )

    # Material Costs
    panels_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    inverter_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    structure_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bos_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cable_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    earthing_lightning_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Operational Costs
    labour_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    logistics_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    installation_overhead = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Taxes & Contingency
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('13.80'))
    commission_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contingency_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Calculated & Final Pricing
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_margin = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    margin_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Approval tracking
    proposal_sent = models.BooleanField(default=False)
    client_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    updated_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_costing(self):
        def _to_dec(val):
            if val is None:
                return Decimal('0')
            if isinstance(val, Decimal):
                return val
            return Decimal(str(val))

        base = (
            _to_dec(self.panels_cost) +
            _to_dec(self.inverter_cost) +
            _to_dec(self.structure_cost) +
            _to_dec(self.bos_cost) +
            _to_dec(self.cable_cost) +
            _to_dec(self.earthing_lightning_cost) +
            _to_dec(self.labour_cost) +
            _to_dec(self.logistics_cost) +
            _to_dec(self.installation_overhead) +
            _to_dec(self.commission_cost) +
            _to_dec(self.contingency_cost)
        )
        gst_pct = _to_dec(self.gst_percentage)
        gst = (base * gst_pct) / Decimal('100.0')
        self.total_cost = base + gst

        selling_price = _to_dec(self.selling_price)
        if selling_price > Decimal('0'):
            self.gross_margin = selling_price - self.total_cost
            self.margin_percentage = round((self.gross_margin / selling_price) * Decimal('100.0'), 2)
        else:
            self.gross_margin = Decimal('0.00')
            self.margin_percentage = Decimal('0.00')

    def save(self, *args, **kwargs):
        self.calculate_costing()
        super().save(*args, **kwargs)

    @property
    def estimated_cost(self):
        return self.total_cost

    @property
    def actual_cost(self):
        expenses_total = self.project.expense_reports.aggregate(
            total=Sum('items__amount')
        )['total'] or Decimal('0')
        return expenses_total

    @property
    def revenue(self):
        return self.selling_price

    @property
    def profit(self):
        return self.gross_margin

    def mark_client_approved(self):
        self.client_approved = True
        self.approved_at = timezone.now()
        self.save()

        # Automated commission generation
        if self.project and self.project.lead:
            lead = self.project.lead

            # 1. Internal Sales Commission (2% Flat rate)
            if lead.assigned_to:
                CommissionPayout.objects.get_or_create(
                    user=lead.assigned_to,
                    project=self.project,
                    defaults={
                        'amount': self.estimated_cost * Decimal('0.02'),
                        'description': f'Internal Sales Commission (2%) - {self.project.title}',
                        'status': 'pending'
                    }
                )

            # 2. Franchise / Partner Commission
            try:
                from partners.models import PartnerLead
                partner_lead = PartnerLead.objects.filter(phone=lead.phone).first()
                if partner_lead and partner_lead.partner:
                    partner = partner_lead.partner
                    rate = partner.commission_rate / Decimal('100.0')
                    CommissionPayout.objects.get_or_create(
                        partner=partner,
                        project=self.project,
                        defaults={
                            'amount': self.estimated_cost * rate,
                            'description': f'Partner Commission ({partner.commission_rate}%) - {self.project.title}',
                            'status': 'pending'
                        }
                    )
            except Exception as e:
                print(f"Error generating partner commission: {e}")

    @property
    def system_costing(self):
        return self.panels_cost

    @system_costing.setter
    def system_costing(self, value):
        self.panels_cost = value or Decimal('0')

    @property
    def kseb_cost(self):
        return self.installation_overhead

    @kseb_cost.setter
    def kseb_cost(self, value):
        self.installation_overhead = value or Decimal('0')

    @property
    def entered_by(self):
        return self.updated_by

    @entered_by.setter
    def entered_by(self, value):
        self.updated_by = value

    @property
    def design_costing(self):
        return getattr(self.project, 'design_costing', None)

    @property
    def gross_margin_percentage(self):
        return self.margin_percentage

    @property
    def last_updated(self):
        return self.updated_at

    def __str__(self):
        return f"Costing - {self.project.title}"

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


class CommissionPayout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='commissions', help_text="For internal sales team")
    partner = models.ForeignKey('partners.Partner', on_delete=models.SET_NULL, null=True, blank=True, related_name='commissions', help_text="For external franchises/dealers")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='commissions_generated')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        target = self.user.get_full_name() if self.user else (self.partner.name if self.partner else "Unknown")
        return f"{target} - Rs. {self.amount} ({self.status})"


# ===============================
# LOAN & FINANCING
# ===============================
class Financier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    interest_rate_range = models.CharField(max_length=50, blank=True, help_text="e.g. 8.5% - 12%")

    def __str__(self):
        return self.name

class LoanApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('rejected', 'Rejected'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='loans')
    financier = models.ForeignKey(Financier, on_delete=models.SET_NULL, null=True, related_name='loans')
    
    applicant_name = models.CharField(max_length=255)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual Interest Rate (%)")
    tenure_months = models.IntegerField(help_text="Duration in months")
    
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    applied_on = models.DateField(auto_now_add=True)
    approved_on = models.DateField(null=True, blank=True)
    disbursed_on = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.applicant_name} - {self.financier.name if self.financier else 'No Bank'}"
        
    def calculate_emi(self):
        """Standard EMI Calculation formula: P x R x (1+R)^N / [(1+R)^N-1]"""
        try:
            p = float(self.loan_amount or 0)
            r = (float(self.interest_rate or 0) / 100) / 12  # monthly interest rate
            n = int(self.tenure_months or 0)
            
            if r > 0 and n > 0:
                emi = p * r * ((1 + r)**n) / (((1 + r)**n) - 1)
                self.emi_amount = Decimal(str(round(emi, 2)))
            elif n > 0:
                self.emi_amount = Decimal(str(round(p / n, 2)))
            else:
                self.emi_amount = Decimal('0')
        except Exception:
            self.emi_amount = Decimal('0')
        self.save(update_fields=['emi_amount'])

    def generate_schedule(self):
        """Generates EMISchedule rows based on calculated EMI."""
        if not self.emi_amount:
            self.calculate_emi()
            
        self.schedules.all().delete()  # Clear existing
        
        try:
            p = float(self.loan_amount or 0)
            r = (float(self.interest_rate or 0) / 100) / 12
            emi = float(self.emi_amount or 0)
            n = int(self.tenure_months or 0)
            
            balance = p
            start_date = self.disbursed_on or timezone.now().date()
            
            for i in range(1, n + 1):
                interest = balance * r
                principal = emi - interest
                balance -= principal
                
                due_date = start_date + timezone.timedelta(days=30 * i)  # Approx month
                
                EMISchedule.objects.create(
                    loan=self,
                    installment_no=i,
                    due_date=due_date,
                    principal_amount=Decimal(str(round(max(0, principal), 2))),
                    interest_amount=Decimal(str(round(max(0, interest), 2))),
                    total_amount=self.emi_amount or Decimal('0'),
                    status='pending'
                )
        except Exception:
            pass


class EMISchedule(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='schedules')
    installment_no = models.IntegerField()
    due_date = models.DateField()
    
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_on = models.DateField(null=True, blank=True)

    def is_overdue(self):
        return self.status == 'pending' and timezone.now().date() > self.due_date

    def __str__(self):
        return f"EMI {self.installment_no} for {self.loan.applicant_name}"

