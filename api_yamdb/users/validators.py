import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ValidateUsername:
    """Валидаторы для username."""

    def validate_username(self, username):
        pattern = re.compile(r'^[\w.@+-]+')

        if not re.fullmatch(pattern, username):
            symbols_forbidden = ''.join(re.split(pattern, username))
            raise ValidationError(
                _(f'Вы использовали запрещенные символы: {symbols_forbidden}!')
            )
        if username == 'me':
            raise ValidationError('Имя пользователя "me" не разрешено!')
        return username
