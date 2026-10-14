from django.db import models
from users.models import CustomUser

class PartnerType(models.TextChoices):
    FRANCHISE = 'franchise', 'Franchise'
    DEALER = 'dealer', 'Dealer'

class Partner(models.Model):
    """
    Master model for Franchises, Branches, and Dealers.
    """
    name = models.CharField(max_length=255)
    partner_type = models.CharField(max_length=50, choices=PartnerType.choices)
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)
    
    # Partner Login User
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='partner_profile',
        help_text="Login user account for this partner."
    )
    
    # Manager/Owner of the franchise or dealer account
    assigned_manager = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_partners',
        help_text="Internal employee assigned to manage this partner."
    )
    
    # Financial metrics or settings
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00, 
        help_text="Percentage commission applied to sales"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()})"


class PartnerLead(models.Model):
    """
    Franchise leads tracking system.
    """
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='leads')
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('lost', 'Lost')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lead: {self.customer_name} by {self.partner.name}"


class PartnerStock(models.Model):
    """
    Dealer-wise or Franchise-wise stock tracking.
    """
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='stocks')
    material = models.ForeignKey('procurement.Material', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('partner', 'material')

    def __str__(self):
        return f"{self.partner.name} - {self.material.name}: {self.quantity}"
