from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from reviews.models import Comment, Review, Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    score = serializers.IntegerField(
        validators=(
            MinValueValidator(1, 'Оценка не может быть меньше 1.'),
            MaxValueValidator(10, 'Оценка не может быть выше 10.'),
        )
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(title=title_id, author=author).exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на произведение'
            )
        return data
