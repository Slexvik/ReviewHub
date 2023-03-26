import re

from django.conf import settings
from django.core.exceptions import ValidationError


class ValidateUsername:
    """Валидаторы для username."""

    def validate_username(self, username):
        pattern = re.compile(r'[\w.@+-]+')
        symbols_forbidden = re.sub(pattern, '', username)
        if symbols_forbidden:
            symbols = ", ".join(symbols_forbidden)
            raise ValidationError(
                f'Имя пользователя содержит запрещенные символы: {symbols}'
            )
        if username in settings.INVALID_FORBIDDEN:
            raise ValidationError(
                f'Имя пользователя "{username}" не разрешено!'
            )
        return username
