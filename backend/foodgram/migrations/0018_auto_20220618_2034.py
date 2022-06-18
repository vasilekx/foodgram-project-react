# Generated by Django 2.2.16 on 2022-06-18 20:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0017_auto_20220618_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(help_text='Время приготовления (в минутах)', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(help_text='Количество ингредиента требуемого для рецепта', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество ингредиента'),
        ),
    ]
