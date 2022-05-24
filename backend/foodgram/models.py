# foodgram/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import validate_username

USER = 'user'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, _('Пользователь')),
    (ADMIN, _('Администратор')),
)


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
        blank=True,
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=150,
        blank=True,
    )
    role = models.CharField(
        _('Роль'),
        choices=ROLE_CHOICES,
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        default=USER,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff
