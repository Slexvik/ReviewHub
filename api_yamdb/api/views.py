from statistics import mean
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from reviews.models import Review, Title

from .serializers import CommentSerializer, ReviewSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    pass


class GenreViewSet(viewsets.ModelViewSet):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    pass

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = ('''IsAdminModeratorOwnerOrReadOnly,''')

    def create_or_update(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)
        ratings = Review.objects.filter(title=title.id)
        title.rating = round(mean([r.score for r in ratings]))
        title.save()

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        self.create_or_update(serializer)

    def perform_update(self, serializer):
        self.create_or_update(serializer)

    def get_permissions(self):
        if self.action == "retrieve":
            return ('''ReadOnly(),''')
        return super().get_permissions()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = ('''IsAdminModeratorOwnerOrReadOnly,''')

    def get_review(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(title.reviews, id=review_id)

    def get_queryset(self):
        title = self.get_review()
        return title.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_permissions(self):
        if self.action == "retrieve":
            return ('''ReadOnly(),''')
        return super().get_permissions()
