from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, GenreTitle, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""
    category = SlugRelatedField(slug_field='slug', read_only=True)
    genre = GenreSerializer(required=False, many=True)

    class Meta:
        model = Title
        fields = '__all__'

    def create(self, validated_data):
        if 'genre' not in self.initial_data:
            raise ValidationError('Поле "genre" является обязательным!')
        
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre, status = Genre.objects.get(**genre)
            GenreTitle.objects.create(
                genre=current_genre, title=title
                    )
        return title
