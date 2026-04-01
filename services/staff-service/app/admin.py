from django.contrib import admin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'name', 'email', 'department', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'email', 'department']
    ordering = ['-created_at']
