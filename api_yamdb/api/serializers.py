import datetime as dt

from django.db.models.aggregates import Avg
from rest_framework import serializers
from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Genre
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ('name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title

        def validate(self, data):
            year = data.get('year')
            if year > dt.date.today().year:
                raise serializers.ValidationError(
                    'Нельзя указать будущую дату'
                )

        def get_rating(self, obj):
            return int(Review.objects.filter(id__title=obj.id).aggregate(Avg('score')).values())
