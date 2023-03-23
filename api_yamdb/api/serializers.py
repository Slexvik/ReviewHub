import datetime as dt

from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class ObjectField(serializers.SlugRelatedField):

    def to_representation(self, obj):
        return {
            'name': obj.name,
            'slug': obj.slug,
        }


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = ObjectField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = ObjectField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, data):
        if data >= dt.date.today().year:
            raise serializers.ValidationError(
                'Год выпуска произведения должен быть меньше текущего.'
            )
        return data


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.ReadOnlyField()

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        exclude = ('review',)
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
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
