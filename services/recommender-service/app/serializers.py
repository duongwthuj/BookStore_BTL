from rest_framework import serializers
from .models import UserInteraction, BookSimilarity


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = ['id', 'customer_id', 'book_id', 'interaction_type', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if data.get('interaction_type') == 'rate' and data.get('rating') is None:
            raise serializers.ValidationError("Rating is required for 'rate' interaction type.")
        if data.get('rating') is not None and not (1 <= data['rating'] <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return data


class BookSimilaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSimilarity
        fields = ['id', 'book_id', 'similar_book_id', 'score']
        read_only_fields = ['id']


class RecommendationSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    score = serializers.FloatField()
    reason = serializers.CharField(required=False)
    book_details = serializers.DictField(required=False)


class ComputeSimilaritySerializer(serializers.Serializer):
    book_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of book IDs to compute similarities for. If empty, computes for all books."
    )
