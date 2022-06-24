from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        _('Имя пользователя'),
        max_length=150,
        unique=True,
        validators=[validate_username],
    )
    email = models.EmailField(
        _('Адрес электронной почты'),
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        _('Имя'),
        max_length=150,
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=150,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.username
