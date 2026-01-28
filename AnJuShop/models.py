from django.db import models



# Create your models here. 安豬店
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=200, blank=True, null=True)
    product_name = models.CharField(max_length=200, blank=True, null=True)

    quantity = models.PositiveIntegerField()
    order_date = models.DateField()

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.quantity})"
