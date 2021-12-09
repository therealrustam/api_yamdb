from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, GenreViewSet, JWTTokenView,
                       RegisterView, TitleViewSet)

from .views import CommentViewSet, CustomUserViewSet, ReviewViewSet

appname = 'api'
router = DefaultRouter()
router1 = DefaultRouter()
router2 = DefaultRouter()

router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register('users', CustomUserViewSet)
router1.register('reviews', ReviewViewSet, basename='reviews')
router2.register('comments', CommentViewSet, basename='comments')


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
    path('v1/titles/<int:title_id>/', include(router1.urls)),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/', include(router2.urls)), ]
