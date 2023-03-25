from rest_framework import filters, mixins, viewsets

from api.permissions import IsAdminOrReadOnly


class CategoryGenreBaseClass(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    """
    Базовый вьюсет, позволяющий создавать и удалять объект,
    возвращать список объектов.
    """
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    search_fields = ('name',)


class NoPutModelViewSet(viewsets.ModelViewSet):
    """
    Базовый вьюсет, запрещающий метод PUT.
    """
    http_method_names = ('get', 'patch', 'post', 'delete')
