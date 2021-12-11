from django.conf import settings
from django.core.mail import send_mail
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import CustomViewSet
from .permissions import (AdminOrReadOnly, IsAdmin, ReviewCommentPermissions,
                          TitlePermissions)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetAllUserSerializer,
                          GetTokenSerializer, RegistrationSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          TitleWriteSerializer)

USER_ERROR = {
    'Ошибка': 'Данный email уже зарегистирован.'
}
CODE_ERROR = {
    'Ошибка': 'Неверный код подтвреждения. Проверьте правильность кода.'
}
ERROR_CHANGE_ROLE = {
    'Ошибка': 'Невозможно изменить роль пользователя.'
}
ERROR_CHANGE_EMAIL = {
    'Электронный адрес': 'Невозможно изменить подтвержденный адрес.'
}

USERNAME_NOT_FOUND = {
    'Ошибка': 'Данный пользователь не найден.'
}

PERMISSIONS_ACTIONS = ('partial_update', 'destroy', 'create')

ME_ERROR = {
    'error': 'Данный никнейм выбрать нельзя.'
}


class GetAllUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = GetAllUserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)

    @action(
        detail=False, methods=['GET', 'PATCH'],
        permission_classes=[IsAuthenticated],
        serializer_class=GetAllUserSerializer
    )
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            if ((request.data.get('role') == settings.ADMIN_ROLE)
                    and (self.request.user.role == 'user')):
                data = dict(request.data)
                data['role'] = settings.USER_ROLE
            else:
                data = request.data
            serializer = self.get_serializer(
                user, data=data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class RegistrationView(views.APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def send_reg_mail(email, user):
        send_mail(
            subject='Код подтверждения для получения токена.',
            message=f'Пожалуйста, не передавайте данный код третьим лицам. '
                    f'Ваш код: {user.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        serializer.save(email=email)
        user = get_object_or_404(User, email=email)
        self.send_reg_mail(email, user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        username = serializer.validated_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                USERNAME_NOT_FOUND,
                status=status.HTTP_404_NOT_FOUND
            )
        if user.confirmation_code != confirmation_code:
            return Response(
                CODE_ERROR,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.obtain_token(user), status=status.HTTP_200_OK)

    @staticmethod
    def obtain_token(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (TitlePermissions,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (TitlePermissions,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    permission_classes = (TitlePermissions,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if (self.action == 'post') or (self.action == 'patch'):
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewCommentPermissions, ]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ReviewCommentPermissions, ]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all()
        return new_queryset
