from django.db import models


class Genre(models.Model):
    """Модель жанра."""
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Slug произведения',
        max_length=50,
        unique=True,
    )


class Category(models.Model):
    """Модель категории."""
    name = models.CharField(
        verbose_name='Название категории',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Slug категории',
        max_length=50,
        unique=True,
    )


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=256,
    )
    year = models.IntegerField(
        verbose_name='Год создания произведения',
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        through='GenreTitle',
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория произведения',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
    )


class GenreTitle(models.Model):
    """Модель связи произведения с жанрами."""
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
