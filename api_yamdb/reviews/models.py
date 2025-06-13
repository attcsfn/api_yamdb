from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from titles.models import Title
from users.models import User


class BaseModel(models.Model):
    """
    Абстрактная модель.
    Наследуется в моделях Review и Comment.
    """
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Review(BaseModel):
    """Модель для отзыва пользователя на произведение."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Оценка произведения от 1 до 10',
        verbose_name='Оценка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(BaseModel):
    """Модель для комментария к отзыву."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta():
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
