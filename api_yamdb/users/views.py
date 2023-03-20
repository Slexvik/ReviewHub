import random
from string import digits

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, viewsets, filters, generics, mixins
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404

from .permissions import AdminAndSuperuserOnly
from .serializers import CreateUserSerializer, UserSerializer

from .models import User
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
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
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    confirmation_code = ''.join(random.choices(digits, k=6)) # по возможности прикрутить другую библиотеку
    serializer.save(confirmation_code=confirmation_code)

    send_mail(
        subject='Registration on YaMDb',
        message=f'Your confirmation code is {confirmation_code}',
        from_email=settings.DEFAULT_EMAIL,
        recipient_list=(request.data['email'],))

    return Response(
        serializer.data
    )


@api_view(['POST'])
def create_token(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if not username or not confirmation_code:
        return Response(
            'Не заполнены обязательные поля',
            status=status.HTTP_400_BAD_REQUEST
        )

    if not User.objects.filter(username=username).exists():
        return Response(
            'Имя пользователя неверное',
            status=status.HTTP_404_NOT_FOUND
        )

    user = User.objects.get(username=username)

    if user.confirmation_code == confirmation_code:
        token = AccessToken.for_user(user)
        return Response(
            {
                'access': str(token)
            }
        )

    return Response(
        'Код подтверждения неверен',
        status=status.HTTP_400_BAD_REQUEST
    )
