from django.db import models


class Manager(models.Model):
    user_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'managers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (User ID: {self.user_id})"
