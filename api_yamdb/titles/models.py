from django.db import models

from api.validators import validate_year
from api_yamdb import constants


class AbstractModelGenreCategory(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=constants.LIMIT_MODEL_NAME)
    slug = models.SlugField(verbose_name='slug', unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(AbstractModelGenreCategory):
    class Meta(AbstractModelGenreCategory.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(AbstractModelGenreCategory):
    class Meta(AbstractModelGenreCategory.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=constants.LIMIT_MODEL_NAME,
        verbose_name='Название',
        db_index=True
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        db_index=True,
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр'

    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
