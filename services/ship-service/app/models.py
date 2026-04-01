from django.db import models
import uuid


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)  # "Giao hàng nhanh", "Tiết kiệm"
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField()
    free_ship_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['fee']


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    order_id = models.IntegerField(unique=True)
    method = models.ForeignKey(ShippingMethod, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_code = models.CharField(max_length=50, unique=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f"BS{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipment {self.tracking_code} for Order #{self.order_id}"

    class Meta:
        ordering = ['-created_at']
