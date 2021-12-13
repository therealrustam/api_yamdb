from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

ME_ERROR = {
    'error': 'Данный никнейм выбрать нельзя.'
}


def username_not_me(value):
    me = 'me'
    if value == me:
        raise serializers.ValidationError(ME_ERROR)


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            ('%(value)s год не должен быть больше нынешнего!'),
            params={'value': value},
        )
