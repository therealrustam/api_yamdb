import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    USER_ROLES = [
        ('Admin', 'Администратор'),
        ('Moderator', 'Модератор'),
        ('User', 'Пользователь'),
    ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    username = models.CharField(max_length=150, unique=True,)

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        blank=True,
        max_length=254,
    )
    bio = models.CharField(
        'Информация о себе',
        max_length=500,
        null=True,
        blank=True
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=20,
        choices=USER_ROLES,
        default='user'
    )
    confirmation_code = models.TextField(
        'Код подтверждения',
        max_length=100,
        default=uuid.uuid4,
        null=True,
        editable=False
    )

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.email)


class Category(models.Model):
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
    )
    year = models.IntegerField()
    rating = models.IntegerField(null=True,
                                 blank=True,)
    description = models.TextField(null=True,
                                   blank=True,)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='title',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='title',
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )

    def __str__(self):
        return self.text
