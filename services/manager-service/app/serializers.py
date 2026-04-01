from rest_framework import serializers
from .models import Manager


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'user_id', 'name', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
