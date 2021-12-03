import datetime as dt
from django.db.models.aggregates import Avg

from rest_framework import serializers
from reviews.models import Comment, Review, Title


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ('name', 'year', 'description', 'genre', 'category',)
        model = Title

        def validate(self, data):
            year = data.get('year')
            if year > dt.date.today().year:
                raise serializers.ValidationError(
                    'Нельзя указать будущую дату'
                )

    def get_rating(self, obj):
        return int(Review.objects.filter(id__title=obj.id).aggregate(Avg('score')).values())


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, required=False, slug_field='username')

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, required=False, slug_field='username')

    class Meta:
        model = Comment
        fields = '__all__'
