import os

models_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\projects\models.py"

extra_models = """

# -------------------------------
# Enterprise Approval Engine
# -------------------------------
class ApprovalWorkflow(models.Model):
    STAGE_CHOICES = (
        ('design', 'Design Approval'),
        ('costing', 'Costing Approval'),
        ('quotation', 'Quotation Approval'),
        ('po', 'Purchase Order Approval'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='approvals')
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='approval_requests')
    approver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='pending_approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        unique_together = ('project', 'stage')

    def __str__(self):
        return f"{self.project.title} - {self.get_stage_display()} ({self.status})"


# -------------------------------
# Enterprise Document Management
# -------------------------------
class ProjectDocument(models.Model):
    CATEGORY_CHOICES = (
        ('survey', 'Site Survey Docs'),
        ('design', 'Engineering Designs'),
        ('discom', 'DISCOM / Net Metering'),
        ('subsidy', 'MNRE / Subsidy'),
        ('invoice', 'Invoices & Receipts'),
        ('handover', 'Handover Certificates'),
        ('other', 'Other Documents'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='enterprise_docs/')
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    
    history = HistoricalRecords()

    def __str__(self):
        return f"v{self.version} - {self.title} ({self.project.title})"
"""

with open(models_path, "a", encoding="utf-8") as f:
    f.write(extra_models)

print("Appended models successfully!")
