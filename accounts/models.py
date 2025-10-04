
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from decimal import Decimal
import uuid

# Extending the User Model - matching Digital-Khata users table
class User(AbstractUser):
    USER_ROLES = [
        ('OWNER', 'Business Owner'),
        ('MANAGER', 'Manager'),
        ('STAFF', 'Staff'),
        ('ACCOUNTANT', 'Accountant'),
    ]
    
    name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    business = models.ForeignKey('Business', on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='OWNER')
    
    # Pakistan-specific fields
    cnic = models.CharField(max_length=15, blank=True, null=True, help_text="CNIC without dashes (13 digits)")
    
    # Security & preferences
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    language_preference = models.CharField(max_length=5, choices=[('en', 'English'), ('ur', 'Urdu')], default='en')
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    enable_notifications = models.BooleanField(default=True)
    enable_sms_alerts = models.BooleanField(default=True)
    enable_whatsapp_alerts = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Unique related_name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Unique related_name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name_plural = "Users"


# Business Model - matching Digital-Khata business table
class Business(models.Model):
    BUSINESS_TYPES = [
        ('RETAIL', 'Retail Shop'),
        ('WHOLESALE', 'Wholesale'),
        ('SERVICE', 'Service Provider'),
        ('MANUFACTURING', 'Manufacturing'),
        ('TRADING', 'Trading Company'),
        ('OTHER', 'Other'),
    ]
    
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField()
    business_address = models.TextField()
    business_contact = models.CharField(max_length=15)
    business_owner = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    
    # Pakistan-specific business fields
    ntn_number = models.CharField(max_length=20, blank=True, null=True, help_text="National Tax Number")
    strn_number = models.CharField(max_length=20, blank=True, null=True, help_text="Sales Tax Registration Number")
    
    # Payment integration settings
    enable_easypaisa = models.BooleanField(default=False)
    easypaisa_account = models.CharField(max_length=20, blank=True, null=True)
    enable_jazzcash = models.BooleanField(default=False)
    jazzcash_account = models.CharField(max_length=20, blank=True, null=True)
    enable_raast = models.BooleanField(default=False)
    raast_id = models.CharField(max_length=50, blank=True, null=True)
    bank_account_title = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Business settings
    currency = models.CharField(max_length=3, default='PKR')
    timezone = models.CharField(max_length=50, default='Asia/Karachi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

    class Meta:
        db_table = 'business'
        verbose_name_plural = "Businesses"


# Khata Model - matching Digital-Khata khata table
class Khata(models.Model):
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='khatas')
    khata_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.khata_name} ({self.business.business_name})"

    class Meta:
        db_table = 'khata'
        verbose_name_plural = "Khatas"
        unique_together = ['business', 'khata_name']  # Prevent duplicate khata names within same business


# Accounts Model - matching Digital-Khata accounts table
class Account(models.Model):
    ACCOUNT_TYPES = [
        ('CUSTOMER', 'Customer'),
        ('SUPPLIER', 'Supplier'),
        ('EMPLOYEE', 'Employee'),
        ('OTHER', 'Other'),
    ]
    
    BALANCE_TYPE_CHOICES = [
        ('DEBIT', 'Receivable (Customer owes us)'),
        ('CREDIT', 'Payable (We owe them)'),
    ]
    
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    cnic = models.CharField(max_length=15, blank=True, null=True)
    
    balance_type = models.CharField(max_length=10, choices=BALANCE_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum credit allowed")
    
    khata = models.ForeignKey(Khata, on_delete=models.CASCADE, related_name='accounts')
    
    # Customer portal access
    portal_access_enabled = models.BooleanField(default=False)
    portal_access_token = models.UUIDField(default=uuid.uuid4, unique=True)
    last_portal_access = models.DateTimeField(blank=True, null=True)
    
    # Notification preferences
    enable_sms_notifications = models.BooleanField(default=True)
    enable_whatsapp_notifications = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=False)
    
    # Payment preferences
    preferred_payment_method = models.CharField(max_length=20, blank=True, null=True)
    payment_terms_days = models.IntegerField(default=30, help_text="Payment due in days")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.khata.khata_name}) - {self.business.business_name}"

    class Meta:
        db_table = 'accounts'
        verbose_name_plural = "Accounts"
        unique_together = ['business', 'name', 'khata']  # Prevent duplicate account names within same business and khata


# Roznamcha Model - matching Digital-Khata roznamcha table
class Roznamcha(models.Model):
    CASH_TYPE_CHOICES = [
        ('CASH_IN', 'Cash In'),
        ('CASH_OUT', 'Cash Out'),
    ]
    
    khata = models.ForeignKey(Khata, on_delete=models.CASCADE, related_name='roznamcha_entries')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='roznamcha_entries')
    date = models.DateField()
    cash_type = models.CharField(max_length=10, choices=CASH_TYPE_CHOICES)
    references = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cash_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_out = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accounts_remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account.name} - {self.date} - {self.cash_type}"

    class Meta:
        db_table = 'roznamcha'
        verbose_name_plural = "Roznamcha Entries"
        ordering = ['-date', '-id']


# Legacy models for compatibility (keeping existing structure)
# Suppliers Model
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    balance_type = models.CharField(max_length=10, choices=[('DEBIT', 'Debit'), ('CREDIT', 'Credit')])
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'suppliers'
        verbose_name_plural = "Suppliers"

# Customers Model
class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    balance_type = models.CharField(max_length=10, choices=[('DEBIT', 'Debit'), ('CREDIT', 'Credit')])
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'customers'
        verbose_name_plural = "Customers"


# Notification System Models
class NotificationTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('PAYMENT_DUE', 'Payment Due Reminder'),
        ('PAYMENT_OVERDUE', 'Payment Overdue Alert'),
        ('PAYMENT_RECEIVED', 'Payment Received Confirmation'),
        ('ACCOUNT_STATEMENT', 'Account Statement'),
        ('WELCOME', 'Welcome Message'),
    ]
    
    CHANNEL_TYPES = [
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('EMAIL', 'Email'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='notification_templates')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNEL_TYPES)
    subject = models.CharField(max_length=200, blank=True, null=True)  # For email
    message_template = models.TextField(help_text="Use {name}, {amount}, {due_date} placeholders")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['business', 'template_type', 'channel']
        db_table = 'notification_templates'


class Notification(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='notifications')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)
    recipient_email = models.EmailField(blank=True, null=True)
    
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Tracking
    delivery_id = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


# Payment Integration Models
class PaymentMethod(models.Model):
    METHOD_TYPES = [
        ('EASYPAISA', 'Easypaisa'),
        ('JAZZCASH', 'JazzCash'),
        ('RAAST', 'RAAST'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    account_number = models.CharField(max_length=50)
    account_title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    # For QR code generation
    qr_code_data = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['business', 'method_type', 'account_number']
        db_table = 'payment_methods'


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='payments')
    roznamcha_entry = models.OneToOneField('Roznamcha', on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='PENDING')
    
    # Payment gateway response
    gateway_response = models.JSONField(blank=True, null=True)
    
    payment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']


# Business Analytics Models
class BusinessReport(models.Model):
    REPORT_TYPES = [
        ('DAILY_SUMMARY', 'Daily Summary'),
        ('WEEKLY_SUMMARY', 'Weekly Summary'),
        ('MONTHLY_SUMMARY', 'Monthly Summary'),
        ('PROFIT_LOSS', 'Profit & Loss'),
        ('CASH_FLOW', 'Cash Flow'),
        ('CUSTOMER_AGING', 'Customer Aging Report'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    
    # Report period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report data (stored as JSON)
    report_data = models.JSONField()
    
    # File attachments
    pdf_file = models.FileField(upload_to='reports/pdf/', blank=True, null=True)
    excel_file = models.FileField(upload_to='reports/excel/', blank=True, null=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'business_reports'
        ordering = ['-generated_at']


# Customer Portal Access Logs
class CustomerPortalAccess(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='portal_access_logs')
    access_token_used = models.UUIDField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customer_portal_access'
        ordering = ['-accessed_at']

