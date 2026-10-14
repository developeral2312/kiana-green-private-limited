with open('projects/models.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# FEATURE 22: HELPDESK & AMC TICKETS
# ===============================
class SupportTicket(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical (System Down)'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='support_tickets')
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20)
    
    issue_title = models.CharField(max_length=200)
    issue_description = models.TextField()
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.issue_title}"


# ===============================
# FEATURE 23: SUB-CONTRACTOR PORTAL
# ===============================
class SubcontractorTask(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed (Pending Verification)'),
        ('verified', 'Verified & Approved'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='subcontractor_tasks')
    subcontractor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subcontractor_tasks')
    
    task_name = models.CharField(max_length=200)
    description = models.TextField()
    
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    completion_notes = models.TextField(blank=True)
    photo_proof = models.ImageField(upload_site_photos_path, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_name} for {self.project.title}"

''')
print("Appended Support and Subcontractor models")
