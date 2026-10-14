with open('projects/models.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# FEATURE 24: WARRANTY & SERIAL TRACKING
# ===============================
class EquipmentSerial(models.Model):
    CATEGORY_CHOICES = (
        ('panel', 'Solar Panel'),
        ('inverter', 'Inverter'),
        ('battery', 'Battery'),
        ('other', 'Other Asset'),
    )
    STATUS_CHOICES = (
        ('active', 'Active (Under Warranty)'),
        ('expired', 'Warranty Expired'),
        ('faulty', 'Reported Faulty'),
        ('replaced', 'Replaced'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='equipments')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='panel')
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=150, unique=True)
    
    installation_date = models.DateField(default=timezone.now)
    warranty_months = models.PositiveIntegerField(default=120) # 10 years default for panels
    warranty_expiry = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    replaced_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replacement_for')
    
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from dateutil.relativedelta import relativedelta
        if not self.warranty_expiry and self.installation_date and self.warranty_months:
            self.warranty_expiry = self.installation_date + relativedelta(months=self.warranty_months)
            
        # Update status if expired
        if self.warranty_expiry and self.warranty_expiry < timezone.now().date() and self.status == 'active':
            self.status = 'expired'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_category_display()} - {self.serial_number}"
''')
print('Appended EquipmentSerial')
