from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import LIMIT_EMAIL


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    email = models.EmailField(
        unique=True,
        max_length=LIMIT_EMAIL,
        verbose_name='Адрес электронной почты'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
