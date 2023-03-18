from statistics import mean

from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from users.permissions import (AuthenticatedPrivilegedUsersOrReadOnly,
                               ListOrAdminModeratOnly)
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


class CategoryViewSet(CrLiDeViewSet):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (ListOrAdminModeratOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    search_fields = ('name',)


class GenreViewSet(CrLiDeViewSet):
    """Вьюсет для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (ListOrAdminModeratOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (ListOrAdminModeratOnly,)
    pagination_class = PageNumberPagination
    filterset_fields = (
        'category__slug',
        'genre__slug',
        'name',
        'year',
    )

    def get_serializer_class(self):
        """
        В случае возвращения произведения или списка произведений
        используется сериализатор TitleReadSerializer.
        Для остальных случаев - TitleWriteSerializer.
        """
        if self.action == 'list' or 'retrieve':
            return TitleReadSerializer
        return TitleWriteSerializer



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthenticatedPrivilegedUsersOrReadOnly,)

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
    # permission_classes = ('''IsAdminModeratorOwnerOrReadOnly,''')  как было
    permission_classes = (AuthenticatedPrivilegedUsersOrReadOnly,)

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
