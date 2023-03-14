from django.contrib.auth.models import AbstractUser
from django.db import models

USER_ROLE = 'user'
MODERATOR_ROLE = 'moderator'
ADMIN_ROLE = 'admin'

CHOICES_ROLE = (
    (USER_ROLE, 'Пользователь'),
    (MODERATOR_ROLE, 'Модератор'),
    (ADMIN_ROLE, 'Администратор'),
)


class User(AbstractUser):
    """Пользователь."""
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(
        verbose_name='Биография',
        max_length=512,
        blank=True,
    )
    role = models.CharField(
        max_length=20,
        choices=CHOICES_ROLE,
        default=USER_ROLE,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=6,
        verbose_name='Код подтверждения',
        blank=True,
    )


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
