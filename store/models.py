"""
RK Store — Django Models (Stage 3)
Defines the 4 tables that will be created in Azure SQL Database.

Tables:
    Product   → iPhone catalog
    Customer  → Buyer information
    Order     → Placed orders
    OrderItem → Individual items within an order
"""

from django.db import models
from django.core.validators import MinValueValidator


# ════════════════════════════════════════════════════════════════════════════
# PRODUCT
# ════════════════════════════════════════════════════════════════════════════

class Product(models.Model):

    NEW  = 'New'
    USED = 'Used'
    CONDITION_CHOICES = [
        (NEW,  'New'),
        (USED, 'Certified Used'),
    ]

    name             = models.CharField(max_length=200)
    storage          = models.CharField(max_length=20)
    color            = models.CharField(max_length=100)
    condition        = models.CharField(max_length=10, choices=CONDITION_CHOICES, default=NEW)
    price            = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    original_price   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                           help_text="Original price before discount. Set for sale items.")
    stock            = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    warranty         = models.CharField(max_length=100)
    battery_health   = models.CharField(max_length=10, null=True, blank=True,
                           help_text="Battery health percentage. Used phones only.")
    description      = models.TextField()

    # Display flags — control which home page sections this product appears in
    is_featured      = models.BooleanField(default=False)
    is_latest        = models.BooleanField(default=False)
    is_special_offer = models.BooleanField(default=False)
    is_limited       = models.BooleanField(default=False)

    is_active        = models.BooleanField(default=True,
                           help_text="Uncheck to hide product without deleting.")
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'products'
        ordering            = ['name']
        verbose_name        = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name} — {self.storage} {self.color} ({self.condition})"

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_amount(self):
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return None

    @property
    def stock_status(self):
        if self.stock == 0:          return 'Out of Stock'
        if self.is_limited or self.stock <= 3: return f'Only {self.stock} left'
        if self.stock <= 8:          return 'Limited Stock'
        return 'In Stock'


# ════════════════════════════════════════════════════════════════════════════
# CUSTOMER
# ════════════════════════════════════════════════════════════════════════════

class Customer(models.Model):

    name       = models.CharField(max_length=200)
    email      = models.EmailField()
    phone      = models.CharField(max_length=30)
    address    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'customers'
        ordering            = ['-created_at']
        verbose_name        = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.name} ({self.email})"


# ════════════════════════════════════════════════════════════════════════════
# ORDER
# ════════════════════════════════════════════════════════════════════════════

class Order(models.Model):

    PENDING    = 'pending'
    CONFIRMED  = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED    = 'shipped'
    DELIVERED  = 'delivered'
    CANCELLED  = 'cancelled'

    STATUS_CHOICES = [
        (PENDING,    'Pending'),
        (CONFIRMED,  'Confirmed'),
        (PROCESSING, 'Processing'),
        (SHIPPED,    'Shipped'),
        (DELIVERED,  'Delivered'),
        (CANCELLED,  'Cancelled'),
    ]

    order_number  = models.CharField(max_length=20, unique=True,
                        help_text="Auto-generated. Format: RK-XXXXXXX")
    customer      = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CONFIRMED)
    total_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    notes         = models.TextField(blank=True, default='')
    email_sent    = models.BooleanField(default=False)
    sms_sent      = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'orders'
        ordering            = ['-created_at']
        verbose_name        = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"{self.order_number} — {self.customer.name} — CAD ${self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import time
            self.order_number = 'RK-' + str(int(time.time()))[-7:].upper()
        super().save(*args, **kwargs)


# ════════════════════════════════════════════════════════════════════════════
# ORDER ITEM
# ════════════════════════════════════════════════════════════════════════════

class OrderItem(models.Model):

    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity   = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                     help_text="Price at the time of order (snapshot).")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'order_items'
        verbose_name        = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.order.order_number} — {self.product.name} x{self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
