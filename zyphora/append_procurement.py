with open('procurement/models.py', 'a', encoding='utf-8') as f:
    f.write('''

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

''')
print('Appended RFQ models')
