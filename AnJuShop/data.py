from datetime import date, timedelta

#from AnJuShop.models import Customer, Product, Order
from .models import Customer, Product, Order


import random

# Create customers
customers = []
for i in range(1, 11):
    c = Customer.objects.create(
        name=f"Customer {i}",
        email=f"customer{i}@example.com",
        age=random.choice([25, 30, 35, 40, None]),  # include some missing age
        city=random.choice(["Hong Kong", "Kowloon", "New Territories", ""])
    )
    customers.append(c)

# Create products
products = []
for i in range(1, 6):
    p = Product.objects.create(
        name=f"Product {i}",
        category=random.choice(["Food", "Electronics", "Clothing"]),
        price=random.choice([10.5, 20.0, 35.99, 50.0])
    )
    products.append(p)

# Create orders (at least 20)
today = date.today()
for i in range(1, 25):
    Order.objects.create(
        customer=random.choice(customers),
        product=random.choice(products),
        quantity=random.randint(1, 5),
        order_date=today - timedelta(days=random.randint(0, 30))
    )