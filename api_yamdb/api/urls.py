from api.views import (CategoryViewSet, GenreViewSet, JWTTokenView,
                       RegisterView, TitleViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

appname = 'api'
router = DefaultRouter()

router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register('users', CustomUserViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/auth/signup/',
        RegisterView.as_view(),
        name='registration'),
    path(
        'v1/auth/token/',
        JWTTokenView.as_view(),
        name='token_obtain_pair'
    ),
]
