from django.shortcuts import get_object_or_404

from reviews.models import Review, Title


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        c_view = serializer_field.context['view']
        title_id = c_view.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title


class CurrentReviewDefault:
    requires_context = True

    def __call__(self, serializer_field):
        c_view = serializer_field.context['view']
        review_id = c_view.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review
