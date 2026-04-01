from django.db import models


class Cart(models.Model):
    customer_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for customer {self.customer_id}"

    class Meta:
        db_table = 'carts'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot price
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'book_id']

    def __str__(self):
        return f"CartItem: book {self.book_id} x {self.quantity} in cart {self.cart_id}"
