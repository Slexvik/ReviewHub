from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(data):
    """Проверка года публикации произведения."""
    year = timezone.now().year
    if year < data:
        raise ValidationError(
            'Проверьте год публикации произведения!'
        )
    return data
