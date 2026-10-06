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

    phone = models.CharField(max_length=20)

    email = models.EmailField(blank=True, null=True)

    address = models.TextField(blank=True)

    gst_number = models.CharField(max_length=50, blank=True)

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
