from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import JWTTokenView, RegisterView

from .views import CustomUserViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet)
# router.register(r'users/(?P<username>[^/.]+)', CustomUserViewSet)


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
