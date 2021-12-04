from reviews.models import Comment, Review, Title
import datetime as dt

from django.db.models.aggregates import Avg
from rest_framework import serializers
from reviews.models import Category, Genre, Title
from users.models import CustomUser

ERROR_CHANGE_ROLE = {
    'role': 'Невозможно изменить роль пользователя.'
}
ERROR_CHANGE_EMAIL = {
    'email': 'Невозможно изменить подтвержденный адрес электронной почты.'
}


class CustomUserSerializer(serializers.ModelSerializer):
    """Выдает список всех пользователей."""
    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = CustomUser
        extra_kwargs = {
            'users': {'lookup_field': 'username'}
        }

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_admin:
            if data.get('role'):
                raise serializers.ValidationError(ERROR_CHANGE_ROLE)
            if data.get('email'):
                raise serializers.ValidationError(ERROR_CHANGE_EMAIL)
        return data


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


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True,)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField(required=False)

    class Meta:
        fields = ('name', 'year', 'rating',
                  'description', 'genre', 'category',)
        model = Title

    def get_rating(self, obj):
        return int(Review.objects.filter(id__title=obj.id).aggregate(Avg('score')).values())


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug', many=True,)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug', )

    class Meta:
        fields = ('name', 'year',
                  'description', 'genre', 'category',)
        model = Title

    def validate(self, data):
        year = data.get('year')
        if year > dt.date.today().year:
            raise serializers.ValidationError(
                'Нельзя указать будущую дату'
            )


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
