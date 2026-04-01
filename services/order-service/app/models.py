from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipping', 'Shipping'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('momo', 'MoMo'),
        ('cod', 'COD'),
        ('bank', 'Bank Transfer'),
        ('vnpay', 'VNPay'),
    ]
    customer_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone = models.CharField(max_length=15)
    note = models.TextField(blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    shipping_method = models.CharField(max_length=50)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - Customer {self.customer_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=255)  # Snapshot
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.book_title} x {self.quantity}"

    @property
    def item_total(self):
        return self.quantity * self.price


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percent'),
        ('fixed', 'Fixed'),
    ]
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self, order_total):
        """Check if coupon is valid for the given order total."""
        from django.utils import timezone

        if not self.is_active:
            return False, "Coupon is not active"

        if self.expires_at and self.expires_at < timezone.now():
            return False, "Coupon has expired"

        if self.max_uses and self.used_count >= self.max_uses:
            return False, "Coupon usage limit reached"

        if order_total < self.min_order:
            return False, f"Minimum order amount is {self.min_order}"

        return True, "Coupon is valid"

    def calculate_discount(self, order_total):
        """Calculate discount amount for the given order total."""
        if self.discount_type == 'percent':
            return (order_total * self.discount_value) / 100
        return min(self.discount_value, order_total)
