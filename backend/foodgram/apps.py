from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FoodgramConfig(AppConfig):
    name = 'foodgram'
    verbose_name = _('Продуктовый помощник')
