from rest_framework import viewsets

from .serializers import (
    CategorySerializer, GenreSerializer,
    TitleSerializer
)
from reviews.models import Category, Genre, Title


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
