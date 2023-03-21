from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.validators import ValidateUsername

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_role(self, role):
        context_user = self.context['request'].user
        user = User.objects.get(username=context_user)
        if user.is_user:
            role = user.role
        return role


class RegistrationSerializer(serializers.Serializer, ValidateUsername):
    """Сериализатор регистрации Usera."""

    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)


class TokenSerializer(serializers.Serializer, ValidateUsername):
    """Сериализатор токена."""

    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        exclude = ('id', )
        # lookup_field = 'slug' так тоже тесты проодят, у нас есть такое поле в моделях, тут точно нужно?


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        exclude = ('id', )
        # lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для возвращения одного произведения
    или списка произведений.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления, редактирования
    и удаления произведений.
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',

    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, data):
        """Проверка года публикации произведения."""
        year = timezone.now().year
        if data < 0 or year < data:
            raise serializers.ValidationError(
                'Проверьте год публикации произведения!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов к произведениям."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        author = self.context['request'].user
        if Review.objects.filter(title=title_id, author=author).exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на произведение'
            )
        return data
