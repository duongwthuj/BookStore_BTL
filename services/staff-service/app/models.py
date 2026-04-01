from django.db import models


class Staff(models.Model):
    user_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.department})"
