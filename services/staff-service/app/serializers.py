from rest_framework import serializers

from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            'id',
            'user_id',
            'name',
            'email',
            'phone',
            'department',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
