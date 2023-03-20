
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.permissions import AdminAndSuperuserOnly
from .serializers import (UserSerializer, TokenSerializer,
                          RegistrationSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания юзера,
    пользователя может добавить администратор."""
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
    """Функция создания кода подтверждения,
    отправляет код на email."""
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        raise ValidationError(
            'username или email заняты!', status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация в проекте YaMDb.',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_EMAIL,
        recipient_list=[user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_token(request):
    """Функция выдачи токена, доступ для всех,
    отправялет JWT-токена в обмен на username и confirmation code."""

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


# @api_view(['POST'])
# def create_token(request):
#     username = request.data.get('username')
#     confirmation_code = request.data.get('confirmation_code')

#     if not username or not confirmation_code:
#         return Response(
#             'Не заполнены обязательные поля',
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     if not User.objects.filter(username=username).exists():
#         return Response(
#             'Имя пользователя неверное',
#             status=status.HTTP_404_NOT_FOUND
#         )

#     user = User.objects.get(username=username)

#     if user.confirmation_code == confirmation_code:
#         token = AccessToken.for_user(user)
#         return Response(
#             {
#                 'access': str(token)
#             }
#         )

#     return Response(
#         'Код подтверждения неверен',
#         status=status.HTTP_400_BAD_REQUEST
#     )
