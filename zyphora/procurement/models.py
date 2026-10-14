from django.db import models,transaction
from finance.models import ExpenseReport, ExpenseItem
from datetime import date


# ===============================
# MATERIAL
# ===============================

class Material(models.Model):

    CATEGORY_CHOICES = (
        ('panel', 'Solar Panel'),
        ('inverter', 'Inverter'),
        ('battery', 'Battery'),
        ('cable', 'Cable'),
        ('structure', 'Structure'),
        ('accessory', 'Accessory'),
    )

    name = models.CharField(max_length=200)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        null=True
    )

    brand = models.CharField(max_length=150, blank=True, null=True)

    unit = models.CharField(max_length=50)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    description = models.TextField(blank=True)

    minimum_stock = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            Stock.objects.create(material=self, quantity=0)

    @property
    def is_low_stock(self):

        if hasattr(self, "stock"):
            return self.stock.quantity <= self.minimum_stock

        return False

    def __str__(self):
        return self.name


# ===============================
# VENDOR
# ===============================

class Vendor(models.Model):

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)

    # Business & Supply Details
    category = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="e.g. Solar Panels, Inverters, Structures, Cables, BOS"
    )
    payment_terms = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        default="30 Days Credit",
        help_text="e.g. 100% Advance, 15 Days Credit, 30 Days Credit"
    )

    # Bank Details for Payments
    bank_name = models.CharField(max_length=150, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ===============================
# PURCHASE ORDER
# ===============================

class PurchaseOrder(models.Model):

    STATUS = (
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="purchase_orders"
    )

    order_date = models.DateField()

    expected_delivery = models.DateField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def update_total(self):

        total = sum(
            item.subtotal() for item in self.items.all()
        )

        self.total_amount = total
        self.save(update_fields=["total_amount"])

    def __str__(self):
        return f"PO-{self.id} - {self.vendor.name}"


# ===============================
# PURCHASE ORDER ITEM
# ===============================

class PurchaseOrderItem(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="purchase_items"
    )

    quantity = models.IntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        self.purchase_order.update_total()


# ===============================
# STOCK
# ===============================

class Stock(models.Model):

    material = models.OneToOneField(
        Material,
        on_delete=models.CASCADE,
        related_name="stock"
    )

    quantity = models.IntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"


# ===============================
# GOODS RECEIVED
# ===============================

class GoodsReceived(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="goods_received"
    )

    received_date = models.DateField()

    received_by = models.ForeignKey(
        'users.Employee',
        on_delete=models.SET_NULL,
        null=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        with transaction.atomic():

            super().save(*args, **kwargs)

            if is_new:

                items = self.purchase_order.items.all()

                for item in items:

                    stock, _ = Stock.objects.get_or_create(
                        material=item.material
                    )

                    stock.quantity += item.quantity
                    stock.save()

                # update PO status
                self.purchase_order.status = "received"
                self.purchase_order.save(update_fields=["status"])

    def __str__(self):
        return f"GRN - PO-{self.purchase_order.id}"


# ===============================
# MATERIAL ALLOCATION
# ===============================

class MaterialAllocation(models.Model):

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name="material_allocations"
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="allocations"
    )

    quantity = models.IntegerField()

    allocated_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True
    )

    allocated_date = models.DateField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )




    def approve(self, user=None):
        """Approve allocation, reduce stock, and create expense"""

        if self.status == 'approved':
            return

        with transaction.atomic():

            # 🟢 Reduce stock
            stock = Stock.objects.get(material=self.material)
            if stock.quantity < self.quantity:
                raise ValueError(f"Not enough stock for {self.material.name}")

            stock.quantity -= self.quantity
            stock.save()

            # 🟢 Mark approved
            self.status = 'approved'
            self.save(update_fields=['status'])

            # 🟢 Calculate cost
            total_cost = self.quantity * self.material.unit_price

            # 🟢 Create Expense Report
            report, created = ExpenseReport.objects.get_or_create(
                project=self.project,
                expense_date=date.today(),
                category='materials',
                defaults={
                    "submitted_by": user,
                    "notes": "Auto material allocation expenses"
                }
            )

            # 🟢 Create Expense Item
            ExpenseItem.objects.create(
                report=report,
                description=f"{self.material.name} x {self.quantity}",
                amount=total_cost
            )

    def reject(self):
        """Call this method to reject request"""
        self.status = 'rejected'
        self.save(update_fields=['status'])

    def __str__(self):
        return f"{self.project} - {self.material} ({self.quantity})"

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
# FEATURE 13: PROCUREMENT INTELLIGENCE (RFQ)
# ===============================
class RequestForQuotation(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published / Open'),
        ('evaluating', 'Evaluating Bids'),
        ('closed', 'Closed (PO Awarded)'),
    )
    title = models.CharField(max_length=200)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"RFQ-{self.id}: {self.title}"

class RFQItem(models.Model):
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.material.name} x {self.quantity}"

class VendorQuotation(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted (L1)'),
    )
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name='quotations')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='quotations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_days = models.PositiveIntegerField(help_text="Expected delivery in days", default=7)
    payment_terms = models.TextField(blank=True)
    
    is_l1 = models.BooleanField(default=False, help_text="System calculated Lowest Bidder")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_total(self):
        total = sum([item.quantity * item.unit_price for item in self.items.all()])
        self.total_amount = total
        self.save()

    def __str__(self):
        return f"Quote by {self.vendor.name} for RFQ-{self.rfq.id}"

class QuotationItem(models.Model):
    quotation = models.ForeignKey(VendorQuotation, on_delete=models.CASCADE, related_name='items')
    rfq_item = models.ForeignKey(RFQItem, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def quantity(self):
        return self.rfq_item.quantity
        
    @property
    def subtotal(self):
        return self.quantity * self.unit_price

