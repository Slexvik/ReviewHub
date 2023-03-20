from statistics import mean

import django_filters
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from users.permissions import (IsAdminModeratorAuthorOrReadOnly,
                               IsAdminOrReadOnly)
from reviews.models import Category, Genre, Review, Title

from .mixins import CrLiDeViewSet
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
)

# Если будут какие-то вопросы или претензии, пишите в телегу @koyote92
# Вынести в api/filters.py, если не придумаете свой способ.
class TitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Title
        fields = '__all__'


class CategoryViewSet(CrLiDeViewSet):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CrLiDeViewSet):
    """Вьюсет для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # filter_backends = (filters.SearchFilter,)
    # permission_classes = (IsAdminOrReadOnly,)
    # pagination_class = PageNumberPagination
    # lookup_field = 'slug'
    # search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend, )
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'PUT'):
            return TitleWriteSerializer
        return TitleReadSerializer


# Ревью и комменты сыпались на тестах из-за неработающего Title, сейчас всё работает.
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()
    
    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

