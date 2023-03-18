from rest_framework import mixins, viewsets


class CrLiDeViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    Базовый вьюсет, позволяющий создавать и удалять объект,
    возвращать список объектов.
    """
    pass
