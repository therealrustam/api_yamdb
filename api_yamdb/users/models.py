import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_ROLES = [
        ('Admin', 'Администратор'),
        ('Moderator', 'Модератор'),
        ('User', 'Пользователь'),
    ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        blank=True
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

