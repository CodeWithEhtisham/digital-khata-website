from django.db import models
from accounts.models import User, Customer, Supplier, Khata, Account

# Create your models here.
# Import main models from accounts app to avoid duplication
# All core models (Business, Khata, Account, Roznamcha) are defined in accounts/models.py

# Additional models specific to roznamcha operations
class Product(models.Model):
    """Product model for inventory management"""
    name = models.CharField(max_length=255)
    uom = models.CharField(max_length=50, verbose_name="Unit of Measurement")
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    class Meta:
        db_table = 'products'
        verbose_name_plural = "Products"


class Sale(models.Model):
    """Sales transaction model"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales")
    date = models.DateField()
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cash_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale {self.id} - {self.date}"
        
    class Meta:
        db_table = 'sales'
        verbose_name_plural = "Sales"


class Stock(models.Model):
    """Stock/Inventory model"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="stocks")
    date = models.DateField()
    stock = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stock {self.id} - {self.product.name}"

    class Meta:
        db_table = 'stocks'
        verbose_name_plural = "Stocks"


class SupplierCashPaid(models.Model):
    """Supplier payment tracking"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="cash_payments")
    date = models.DateField()
    payment_method = models.CharField(max_length=50)
    cash_paid = models.DecimalField(max_digits=10, decimal_places=2)
    remaining = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default="Cash Paid")
    quantity = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.supplier.name}"
        
    class Meta:
        db_table = 'supplier_cash_paid'
        verbose_name_plural = "Supplier Cash Paid"


class CustomerCashReceived(models.Model):
    """Customer payment tracking"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cash_receipts")
    date = models.DateField()
    payment_method = models.CharField(max_length=50)
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default="Cash Received")
    quantity = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receipt {self.id} - {self.customer.name}"
        
    class Meta:
        db_table = 'customer_cash_received'
        verbose_name_plural = "Customer Cash Received"
