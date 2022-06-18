# Generated by Django 2.2.16 on 2022-06-18 18:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0016_auto_20220618_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(help_text='Количество ингредиента требуемого для рецепта', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10000)], verbose_name='Количество ингредиента'),
        ),
    ]
