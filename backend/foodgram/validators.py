# foodgram/validators.py

from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


def validate_username(value):
    for regex, inverse_match in settings.USERNAME_REGEXES:
        RegexValidator(
            regex=regex,
            message=_(f'{value} - недопустимое имя пользователя.'),
            inverse_match=inverse_match
        )(value)
