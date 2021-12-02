import datetime as dt

from rest_framework import serializers
from reviews.models import Categories, Genres, Titles


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Categories
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Genres
        lookup_field = 'slug'


class TitlesSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)

    class Meta:
        fields = ('name', 'year', 'description', 'genre', 'category',)
        model = Titles

        def validate(self, data):
            year = data.get('year')
            if year > dt.date.today().year:
                raise serializers.ValidationError(
                    'Нельзя указать будущую дату'
                )
