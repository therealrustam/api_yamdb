from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User

from .title import CurrentReviewDefault, CurrentTitleDefault

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


def username_not_me(value):
    me = 'me'
    if value == me:
        raise serializers.ValidationError(ME_ERROR)


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            username_not_me,
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'username')
        extra_kwargs = {
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
        model = Category
        exclude = ('id', )
        #lookup_field = 'slug'
        # extra_kwargs = {
        #    'url': {'lookup_field': 'slug'}
        # }


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id', )
        #lookup_field = 'slug'
        # extra_kwargs = {
        #    'url': {'lookup_field': 'slug'}
        # }


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True,)
    category = CategorySerializer(required=False, read_only=True,)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating',)


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, )
    category = CategorySerializer()

    class Meta:
        fields = '__all__'
        model = Title

    def validate(self, data):
        year = data.get('year')
        if year > timezone.now().year:
            raise serializers.ValidationError(
                'Нельзя указать будущую дату'
            )
        return data


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


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.HiddenField(
        default=CurrentReviewDefault(), )
    author = serializers.SlugRelatedField(
        read_only=True, required=False, slug_field='username')

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'text': {'required': True}}
