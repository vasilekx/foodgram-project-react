# Generated by Django 2.2.16 on 2022-06-14 22:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0008_auto_20220614_2140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['user'], 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
