from django.db import models
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=[('admin', 'Admin'), ('cashier', 'Cashier'), ('manager', 'Manager')],
        default='cashier'
    )

# Items model
class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.IntegerField()
    qr_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
from django.db import models
from django.conf import settings
# Sales model
class Sale(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_type = models.CharField(
        max_length=50,
        choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'),('pos', 'P.o.s')]
    )
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

# Sales Items model
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

