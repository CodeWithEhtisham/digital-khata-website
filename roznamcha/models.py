from django.db import models
from accounts.models import User, Customer, Supplier
# Create your models here.
# Business Model
class Business(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.TextField()
    contact = models.CharField(max_length=15)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'business'
        verbose_name_plural = "Businesses"

# Khata Model
class Khata(models.Model):
    name = models.CharField(max_length=255)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="khatas")

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'khata'
        verbose_name_plural = "Khata"

# Accounts Model
class Account(models.Model):
    BALANCE_TYPES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    balance_type = models.CharField(max_length=10, choices=BALANCE_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    khata = models.ForeignKey(Khata, on_delete=models.CASCADE, related_name="accounts")

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'accounts'
        verbose_name_plural = "Accounts"

# Products Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    uom = models.CharField(max_length=50, verbose_name="Unit of Measurement")
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'products'
        verbose_name_plural = "Products"

# Roznamcha (Ledger) Model
class Roznamcha(models.Model):
    CASH_TYPES = [
        ('CASH_IN', 'Cash In'),
        ('CASH_OUT', 'Cash Out'),
    ]

    khata = models.ForeignKey(Khata, on_delete=models.CASCADE, related_name="roznamchas")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="roznamchas")
    date = models.DateField()
    cash_type = models.CharField(max_length=10, choices=CASH_TYPES)
    reference = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cash_in = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining = models.DecimalField(max_digits=10, decimal_places=2)
    account_remaining = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.reference} - {self.cash_type}"
    
    class Meta:
        db_table = 'roznamcha'
        verbose_name_plural = "Roznamcha"

# Sales Model
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales")
    date = models.DateField()
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cash_paid = models.DecimalField(max_digits=10, decimal_places=2)
    cash_received = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale {self.id} - {self.date}"
    class Meta:
        db_table = 'sales'
        verbose_name_plural = "Sales"

# Stock Model
class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="stocks")
    date = models.DateField()
    stock = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Stock {self.id} - {self.product.name}"

    class Meta:
        db_table = 'stocks'
        verbose_name_plural = "Stocks"

# Supplier Cash Paid Model
class SupplierCashPaid(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="cash_payments")
    date = models.DateField()
    payment_method = models.CharField(max_length=50)
    cash_paid = models.DecimalField(max_digits=10, decimal_places=2)
    remaining = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default="Cash Paid")
    quantity = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Payment {self.id} - {self.supplier.name}"
    class Meta:
        db_table = 'supplier_cash_paid'
        verbose_name_plural = "Supplier Cash Paid"

# Customer Cash Received Model
class CustomerCashReceived(models.Model):
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

    def __str__(self):
        return f"Receipt {self.id} - {self.customer.name}"
    class Meta:
        db_table = 'customer_cash_received'
        verbose_name_plural = "Customer Cash Received"