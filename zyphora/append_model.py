with open('finance/models.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# PROJECT COSTING & MARGIN (FEATURE 06)
# ===============================
class ProjectCosting(models.Model):
    project = models.OneToOneField('projects.Project', on_delete=models.CASCADE, related_name='costing')
    
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
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=13.8) # Blended GST
    commission_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contingency_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Totals (Calculated)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_margin = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    margin_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)

    def calculate(self):
        # Calculate Total Cost
        self.total_cost = (
            self.panels_cost + self.inverter_cost + self.structure_cost + 
            self.bos_cost + self.cable_cost + self.earthing_lightning_cost + 
            self.labour_cost + self.logistics_cost + self.installation_overhead + 
            self.commission_cost + self.contingency_cost
        )
        # Add GST
        gst_amount = self.total_cost * (self.gst_percentage / Decimal('100.0'))
        self.total_cost += gst_amount
        
        # Calculate Margin
        if self.selling_price > 0:
            self.gross_margin = self.selling_price - self.total_cost
            self.margin_percentage = (self.gross_margin / self.selling_price) * Decimal('100.0')
        else:
            self.gross_margin = Decimal('0.0')
            self.margin_percentage = Decimal('0.0')

    def save(self, *args, **kwargs):
        self.calculate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Costing for {self.project.title}"
''')
print('Appended ProjectCosting')
