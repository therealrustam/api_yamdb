from rest_framework import serializers
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
            'role'
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
