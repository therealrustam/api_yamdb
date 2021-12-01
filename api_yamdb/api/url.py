from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

app_name = 'api'
router = DefaultRouter()
router1 = DefaultRouter()

router.register('reviews', ReviewViewSet)
router1.register('comments', CommentViewSet)

urlpatterns = [
    path('v1/titles/<int:title_id>/', include(router.urls)),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/', include(router1.urls)),
]
