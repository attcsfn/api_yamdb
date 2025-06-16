import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    if value > dt.date.today().year:
        raise ValidationError(
            'Год произведения не может быть больше текущего.',
        )
