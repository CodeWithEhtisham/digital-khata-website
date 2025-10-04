from django.db import models
from accounts.models import Business, Khata

# Create your models here.
# Business-specific models and utilities

class BusinessSettings(models.Model):
    """Settings and preferences for business operations"""
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='settings')
    default_currency = models.CharField(max_length=3, default='PKR')
    fiscal_year_start = models.DateField()
    enable_inventory = models.BooleanField(default=True)
    enable_gst = models.BooleanField(default=False)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.business.business_name}"

    class Meta:
        verbose_name_plural = "Business Settings"
