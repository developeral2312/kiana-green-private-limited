with open('crm/models.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# FEATURE 20: REFERRAL ENGINE
# ===============================
class Referral(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending (Lead)'),
        ('converted', 'Converted (Project Started)'),
        ('paid', 'Commission Paid'),
        ('rejected', 'Rejected / Invalid'),
    )
    
    # Who is referring
    referrer_name = models.CharField(max_length=150)
    referrer_phone = models.CharField(max_length=20)
    referrer_email = models.EmailField(blank=True, null=True)
    
    # Who is referred
    referred_lead = models.OneToOneField('Lead', on_delete=models.CASCADE, related_name='referred_by', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.referrer_name} referred {self.referred_lead.name if self.referred_lead else 'Unknown'}"
''')
print("Appended Referral model")
