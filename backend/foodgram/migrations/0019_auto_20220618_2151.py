# Generated by Django 2.2.16 on 2022-06-18 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0018_auto_20220618_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='foodgram/images/', verbose_name='Картинка'),
        ),
    ]
