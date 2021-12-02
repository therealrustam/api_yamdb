from api.views import CategoriesViewSet, GenresViewSet, TitlesViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

appname = 'api'
router = DefaultRouter()

router.register(r'categories', CategoriesViewSet)
router.register(r'genres', GenresViewSet)
router.register(r'titles', TitlesViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
