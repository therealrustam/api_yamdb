import datetime as dt

from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title, User

ERROR_CHANGE_ROLE = {
    'role': 'Невозможно изменить роль пользователя.'
}
ERROR_CHANGE_EMAIL = {
    'email': 'Невозможно изменить подтвержденный адрес электронной почты.'
}
ME_ERROR = {
    'error': 'Данный никнейм выбрать нельзя.'
}


class GetAllUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

        extra_kwargs = {
            'users': {'lookup_field': 'username'},
            'username': {'required': True},
            'email': {'required': True}
        }


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username'
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        model = Category


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        model = Genre


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreField(slug_field='slug',
                       queryset=Genre.objects.all(), many=True)
    category = CategoryField(slug_field='slug',
                             queryset=Category.objects.all(), required=False)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = GenreField(slug_field='slug',
                       queryset=Genre.objects.all(), many=True)
    category = CategoryField(slug_field='slug',
                             queryset=Category.objects.all(), required=False)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

        def validate(self, data):
            year = data.get('year')
            if year > dt.date.today().year:
                raise serializers.ValidationError(
                    'Нельзя указать будущую дату'
                )

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(Avg('score'))['score__avg']
        return rating


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        c_view = serializer_field.context['view']
        title_id = c_view.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.HiddenField(default=CurrentTitleDefault())
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review
        validators = (UniqueTogetherValidator(
            queryset=Review.objects.all(),
            fields=('title', 'author',)),)


class CurrentReviewDefault:
    requires_context = True

    def __call__(self, serializer_field):
        c_view = serializer_field.context['view']
        review_id = c_view.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.HiddenField(
        default=CurrentReviewDefault(), )
    author = serializers.SlugRelatedField(
        read_only=True, required=False, slug_field='username')

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'text': {'required': True}}
