from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser

from api.permissions import IsAdmin
from api.serializers import CustomUserSerializer

USER_ERROR = {
    'error': 'Пользователь с таким email уже существует!'
}
CODE_INFO = {
    'email': 'Код подтверждения отправлен на Ваш email!'
}
CODE_ERROR = {
    'error': 'Неверный код подтверждения'
}


class CustomUserViewSet(viewsets.ModelViewSet):
    """Выдает список всех пользователей."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return Response(
                USER_ERROR, status=status.HTTP_400_BAD_REQUEST
            )
        user = CustomUser.objects.create_user(
            username=email, email=email, password=None
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Ваш код подтверждения',
            confirmation_code,
            settings.DEFAULT_FROM_EMAIL,
            (email,),
        )
        return Response(CODE_INFO, status=status.HTTP_200_OK)


class JWTTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data['email']
        confirmation_code = request.data['confirmation_code']
        user = get_object_or_404(CustomUser, email=email)
        if not default_token_generator.check_token(
            user, confirmation_code
        ):
            return Response(
                CODE_ERROR, status=status.HTTP_400_BAD_REQUEST
            )
        response = get_tokens_for_user(user)
        return Response(response, status=status.HTTP_200_OK)
