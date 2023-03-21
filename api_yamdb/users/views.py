from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import AdminAndSuperuserOnly
from api.serializers import (RegistrationSerializer, TokenSerializer,
                               UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для создания юзера,
    пользователя может добавить администратор.
    """
    http_method_names = ('get', 'patch', 'post', 'delete')
    queryset = User.objects.all()
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminAndSuperuserOnly,)
    filter_backends = (filters.SearchFilter,)
    serializer_class = UserSerializer
    search_fields = ('username',)

    @action(
        methods=('get', 'patch'),
        url_path='me',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserSerializer(user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
def signup_user(request):
    """
    Функция создания кода подтверждения,
    отправляет код на email.
    """
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        raise ValidationError(
            'Пользователи с таким username или email уже существуют',
            status.HTTP_400_BAD_REQUEST,
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация на YaMDb.',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_EMAIL,
        recipient_list=[user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_token(request):
    """
    Функция выдачи токена, доступ для всех,
    отправялет JWT-токена в обмен на username и confirmation code.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
    ):
        token = RefreshToken.for_user(user)
        return Response(
            {'access': str(token.access_token)}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
