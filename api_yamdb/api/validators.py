import datetime as dt

from django.core.exceptions import ValidationError

from api_yamdb.constants import MAX_SCORE, MIN_SCORE


def validate_year(value):
    if value > dt.date.today().year:
        raise ValidationError(
            'Год произведения не может быть больше текущего.'
        )


def validate_score_range(value):
    is_valid = MIN_SCORE <= value <= MAX_SCORE
    if not is_valid:
        raise ValidationError(
            'Оценка должна быть в диапазоне от'
            f'{MIN_SCORE} до {MAX_SCORE}'
        )
    return value
