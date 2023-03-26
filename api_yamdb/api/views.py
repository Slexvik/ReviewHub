from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (IsAdminAndSuperuserOnly,
                             IsAdminModeratorAuthorOrReadOnly,
                             IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, RegistrationSerializer,
                             ReviewSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenSerializer,
                             UserMeSerializer, UserSerializer)
from api.utils import CategoryGenreBaseClass, NoPutModelViewSet
from reviews.models import Category, Genre, Review, Title
from users.validators import ValidateUsername

User = get_user_model()


class UserViewSet(ValidateUsername, NoPutModelViewSet):
    """
    Вьюсет для создания юзера,
    пользователя может добавить администратор.
    """
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
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserMeSerializer(user, data=request.data,
                                      partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    user_username = User.objects.filter(username=username).first()
    user_email = User.objects.filter(email=email).first()
    if user_username == user_email:
        user, _ = User.objects.get_or_create(
            username=username, email=email)
    else:
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
            {'access': str(token)}, status=status.HTTP_200_OK
        )
    return Response(
        {'confirmation_code': 'Неверный код подтверждения'},
        status=status.HTTP_400_BAD_REQUEST
    )


class CategoryViewSet(CategoryGenreBaseClass):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseClass):
    """Вьюсет для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(NoPutModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        """
        В случае возвращения произведения или списка произведений
        используется сериализатор TitleReadSerializer.
        Для остальных случаев - TitleWriteSerializer.
        """
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(NoPutModelViewSet):
    """Вьюсет для отзывов о произведениях."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(NoPutModelViewSet):
    """Вьюсет для комментариев к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_review(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id, title=title_id)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
