import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ValidateUsername:
    """Валидаторы для username."""

    def validate_username(self, username):
        if not re.match(r'[\w.@+-]+\Z', username):
            raise ValidationError(
                _(f'{username} не должно включать запрещенные символы!')
            )
        if username == 'me':
            raise ValidationError('Имя пользователя "me" не разрешено.')
        return username
