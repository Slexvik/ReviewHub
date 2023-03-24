from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year

User = get_user_model()


class Genre(models.Model):
    """Модель жанра."""
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=settings.MAX_LENGTH_NAME,
        db_index=True,
    )
    slug = models.SlugField(
        verbose_name='Slug произведения',
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True,
    )

    class Meta:
        db_table = 'genre'
        ordering = ['-id']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.slug


class Category(models.Model):
    """Модель категории."""
    name = models.CharField(
        verbose_name='Название категории',
        max_length=settings.MAX_LENGTH_NAME,
        db_index=True,
    )
    slug = models.SlugField(
        verbose_name='Slug категории',
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True,
    )

    class Meta:
        db_table = 'category'
        ordering = ['-id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=settings.MAX_LENGTH_NAME,
        db_index=True,
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания произведения',
        validators=(validate_year, ),
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        through='GenreTitle',
        through_fields=('title', 'genre'),
        related_name='titles',
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория произведения',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        db_index=True,
    )

    class Meta:
        db_table = 'title'
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель связи произведения с жанрами."""
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'genre_title'
        verbose_name = 'Связь произведения и жанра'
        verbose_name_plural = 'Связи произведений и жанров'


class Review(models.Model):
    """Модель отзывов о произведениях."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1.'),
            MaxValueValidator(10, 'Оценка не может быть выше 10.')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        db_table = 'review'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_title_author'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.author} - {self.text[:30]}'


class Comment(models.Model):
    """Модель комментариев к отзывам."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Обзор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        db_table = 'comment'
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author} - {self.text[:30]}'
