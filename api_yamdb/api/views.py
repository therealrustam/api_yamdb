from copy import deepcopy


from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (AdminOrReadOnly, AuthorOrReadOnly, IsAdmin,
                          IsAdminOrReadOnly, IsOwnerAdminModeratorOrReadOnly,
                          ModeratorOrReadOnly)
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
ME_ERROR = {
    'Ошибка': 'Данный никнейм выбрать нельзя.'
}
USERNAME_NOT_FOUND = {
    'Ошибка': 'Данный пользователь не найден.'
}


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class GetAllUserViewSet(viewsets.ModelViewSet):
    """Пользователь с правами админа может создать
    нового пользователя, отправив запрос на api/v1/users/.

    Авторизованный пользователь, получивший токен,
    может с помощью PATCH-запроса заполнить поля
    своего профиля, отправив запрос на api/v1/users/me/.
    """
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
            if (request.data.get('role') == 'admin') and (self.request.user.role == 'user'):
                data = deepcopy(request.data)
                data['role'] = 'user'
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
        username = serializer.validated_data['username']
        if username == 'me':
            return Response(ME_ERROR, status=status.HTTP_400_BAD_REQUEST)
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


class CustomViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    pass


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.user.is_authenticated:
            if (self.action == 'partial_update') or (self.action == 'destroy') or (self.action == 'create'):
                return (AdminOrReadOnly(),)
        return super().get_permissions()


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.user.is_authenticated:
            if (self.action == 'partial_update') or (self.action == 'destroy') or (self.action == 'create'):
                return (AdminOrReadOnly(),)
        return super().get_permissions()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'post' or 'patch' or 'delete':
            return TitleWriteSerializer
        return TitleReadSerializer

    def get_permissions(self):
        if self.request.user.is_authenticated:
            if (self.action == 'partial_update') or (self.action == 'destroy') or (self.action == 'create'):
                return (AdminOrReadOnly(),)
        return super().get_permissions()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_queryset = Review.objects.filter(title__id=title.id)
        return new_queryset

    def get_permissions(self):
        if self.request.user.is_authenticated:
            if (self.action == 'partial_update'):
                return (AuthorOrReadOnly(),)
            if (self.action == 'destroy'):
                return (ModeratorOrReadOnly(),)
        return super().get_permissions()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        new_queryset = Comment.objects.filter(review__id=review.id)
        return new_queryset

    def get_permissions(self):
        if self.request.user.is_authenticated:
            if (self.action == 'partial_update'):
                return (AuthorOrReadOnly(),)
            if (self.action == 'destroy'):
                return (ModeratorOrReadOnly(),)
        return super().get_permissions()
