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
    """Пользователям добавлены новые поля биография и роль."""
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
        blank=True, max_length=6,
        verbose_name='Код подтверждения')

    class Meta():
        db_table = 'user'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE

    @property
    def is_user(self):
        return self.role == USER_ROLE

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE
    
    def __str__(self):
        return self.username
