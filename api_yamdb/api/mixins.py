from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from users.permissions import IsAdminOrReadOnly


class CrLiDeViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    Базовый вьюсет, позволяющий создавать и удалять объект,
    возвращать список объектов.
    """
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    search_fields = ('name',)
