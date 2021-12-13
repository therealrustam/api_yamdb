import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator


class User(AbstractUser):
    USER = settings.USER_ROLE
    MODERATOR = settings.MODERATOR_ROLE
    ADMIN = settings.ADMIN_ROLE
    ROLE_CHOISES = [
        (USER, settings.USER_ROLE),
        (MODERATOR, settings.MODERATOR_ROLE),
        (ADMIN, settings.ADMIN_ROLE)
    ]
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    email = models.EmailField(
        verbose_name='Электронная почта',
        blank=False,
        unique=True
    )

    bio = models.TextField(
        verbose_name='Биография пользователя',
        blank=True,
        null=True,
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=10,
        choices=ROLE_CHOISES,
        default=USER,
        blank=False,
    )
    confirmation_code = models.TextField(
        verbose_name='Код подтверждения',
        max_length=100,
        default=uuid.uuid4,
        null=True,
        editable=False,
    )

    class Meta:
        ordering = ['date_joined']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.email)

    @property
    def is_admin(self):
        return self.role == settings.ADMIN_ROLE or self.is_staff

    @property
    def is_moderator(self):
        return self.role == settings.MODERATOR_ROLE


class Category(models.Model):
    name = models.CharField(
        verbose_name='Наименование категории',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Slug категории',
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Наименование жанра',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Slug жанра',
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.slug


class Title(models.Model):

    name = models.TextField(
        verbose_name='Наименование произведения',
        max_length=256, db_index=True,
    )
    year = models.IntegerField(verbose_name='Год произведения',
                               validators=[year_validator],)
    description = models.TextField(verbose_name='Описание произведения',
                                   null=True, blank=True,)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        verbose_name='Категория',
        db_index=True,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(verbose_name='Текст отзыва',)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(1,
                              message='Оценка не должна быть меньше 1'),
            MaxValueValidator(10,
                              message='Оценка не должна быть больше 10')
        ),
        verbose_name='Оценка произведения',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review')
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.TextField(verbose_name='Текст комментария',)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор комментария',
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
