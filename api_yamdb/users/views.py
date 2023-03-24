from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from users.validators import ValidateUsername
from api.permissions import IsAdminAndSuperuserOnly
from api.serializers import (RegistrationSerializer, TokenSerializer,
                             UserSerializer, UserRoleSerializer)

User = get_user_model()


class UserViewSet(ValidateUsername, viewsets.ModelViewSet):
    """
    Вьюсет для создания юзера,
    пользователя может добавить администратор.
    """
    http_method_names = ('get', 'patch', 'post', 'delete')
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (IsAdminAndSuperuserOnly,)
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
        if request.method == 'GET':
            return Response(serializer.data)
        serializer = UserRoleSerializer(user, data=request.data,
                                        partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_user(request):
    """
    Функция создания кода подтверждения,
    отправляет код на email.
    """
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    if (User.objects.filter(username=username, email=email).exists()
        or not (User.objects.filter(username=username).exists()
                or User.objects.filter(email=email).exists())):
        user, _ = User.objects.get_or_create(
            username=username, email=email)
    else:
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация на YaMDb.',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_EMAIL,
        recipient_list=[user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
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
        token = AccessToken.for_user(user)
        return Response(
            {'access': str(token.access_token)}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
