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
        model = User
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


class TokenSerializer(serializers.Serializer):
    class Meta:
        fields = ('username', 'confirmation_code',)


class RegisterSerializer(serializers.Serializer):
    class Meta:
        fields = ('email', 'username',)


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
    rating = serializers.SerializerMethodField(required=False,)

    class Meta:
        fields = '__all__'
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
        fields = '__all__'
        model = Title

        def validate(self, data):
            year = data.get('year')
            if year > dt.date.today().year:
                raise serializers.ValidationError(
                    'Нельзя указать будущую дату'
                )


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
