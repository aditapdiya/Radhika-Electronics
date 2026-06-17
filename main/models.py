# models.py
from django.db import models
from django.contrib.auth.models import User

# 1
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15) 
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})" 
# 2
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
# 3 
class Brand(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name
# 4
class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(default='No description available') 
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    price = models.FloatField()
    stock = models.IntegerField()

    def __str__(self):
        return self.name

# 5
class Order(models.Model):
    PAYMENT_METHODS = [
        ('COD', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# 7 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10, unique=True)  

    def __str__(self):
        return self.user.username

# 8
class Wishlist(models.Model):
    user= models.ForeignKey(User, on_delete=models.PROTECT)
    product=models.ForeignKey(Product, on_delete=models.PROTECT)
    added_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"