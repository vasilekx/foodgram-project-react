from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from foodgram.models import Ingredient


def validate_ingredients(ingredients: dict) -> bool:
    if not ingredients:
        raise serializers.ValidationError(
            {
                'ingredients': 'Обязательное поле.'
            }
        )
    ingredient_list = []
    for ingredient_item in ingredients:
        ingredient_id = ingredient_item['ingredient']['id']
        amount = ingredient_item['amount']
        if not ingredient_id:
            raise serializers.ValidationError(
                {
                    'ingredients': {
                        'id': _('Обязательное поле.')
                    }
                }
            )
        if not amount:
            raise serializers.ValidationError(
                {
                    'ingredients': {
                        'amount': _('Обязательное поле.')
                    }
                }
            )
        ingredient = Ingredient.objects.filter(id=ingredient_id)
        ingredient_exists = ingredient.exists()
        if not ingredient_exists:
            raise serializers.ValidationError(
                {
                    'ingredients': {
                        'id': _('Ингридиента не существует.')
                    }
                }
            )
        ingredient = ingredient.get()
        if ingredient in ingredient_list:
            raise serializers.ValidationError(
                'Недопустимо дублирование ингридиентов.'
            )
        ingredient_list.append(ingredient)
        if int(amount) < 0:
            raise serializers.ValidationError(
                {
                    'ingredients': {
                        'amount': (
                            'Количества ингредиента меньше 0.'
                        )
                    }
                }
            )
    return True
