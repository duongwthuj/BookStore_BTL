from rest_framework import serializers

from .models import Review, ReviewReply


class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ['id', 'staff_id', 'staff_name', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    replies = ReviewReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'book_id', 'customer_id', 'customer_name', 'rating',
            'comment', 'images', 'is_verified_purchase', 'created_at',
            'updated_at', 'replies'
        ]
        read_only_fields = ['id', 'is_verified_purchase', 'created_at', 'updated_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'book_id', 'customer_id', 'customer_name', 'rating',
            'comment', 'images', 'is_verified_purchase', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'is_verified_purchase', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_images(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Images must be a list.")
        return value


class ReviewReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ['id', 'staff_id', 'staff_name', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class RatingStatsSerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
