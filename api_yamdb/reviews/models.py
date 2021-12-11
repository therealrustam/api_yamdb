import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOISES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    ]

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    email = models.EmailField(
        blank=False,
        unique=True
    )

    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        null=True,
    )
    role = models.CharField(
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

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        ordering = ['date_joined']
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

    def year_validator(value):
        if value > timezone.now().year:
            raise ValidationError(
                ('%(value)s is not a correcrt year!'),
                params={'value': value},
            )

    name = models.CharField(
        max_length=256, db_index=True,
    )
    year = models.IntegerField(validators=[year_validator],)
    description = models.TextField(null=True,
                                   blank=True,)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles',
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
            MinValueValidator(1,
                              message='Оценка не должна быть меньше 1'),
            MaxValueValidator(10,
                              message='Оценка не должна быть больше 10')
        ),

    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review')
        ]

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

    class Meta:
        ordering = ['pub_date']
