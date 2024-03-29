from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


def validate_tag_color(value):
    regex, inverse_match = settings.COLORS_HEX_REGEX
    RegexValidator(
        regex=regex,
        message=_(f'{value} - недопустимый код цвета.'),
        inverse_match=inverse_match
    )(value)
