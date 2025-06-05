
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Extending the User Model
class User(AbstractUser):
    contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

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

