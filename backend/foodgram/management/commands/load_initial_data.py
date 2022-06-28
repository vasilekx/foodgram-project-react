import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from foodgram.models import Ingredient, Tag, User

data_files_list = [
    ['tags.csv', Tag],
    ['ingredients.csv', Ingredient],
    ['users.csv', User],
]


def get_dirs(list_files: list) -> None:
    for i, lst in enumerate(list_files):
        data_files_list[i].append(
            os.path.join(settings.BASE_DIR, 'static/data', lst[0])
        )


def load_tags_data(list_data: list) -> None:
    for file, model, path in list_data:
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = next(reader)
            for row in reader:
                import_dict = {
                    key: value for key, value in zip(header, row)
                }
                if file == 'ingredients.csv':
                    ingredient, _ = model.objects.get_or_create(**import_dict)
                if file == 'tags.csv':
                    tag, _ = model.objects.get_or_create(**import_dict)
                if file == 'users.csv':
                    raw_password = import_dict.pop('password')
                    user, created = model.objects.get_or_create(**import_dict)
                    if created:
                        user.set_password(raw_password)
                        user.save()


class Command(BaseCommand):
    help = _('Загрузка данных')

    def handle(self, *args, **options):
        get_dirs(data_files_list)
        self.stdout.write(_('Загрузка данных...'))
        try:
            load_tags_data(data_files_list)
            self.stdout.write(
                self.style.SUCCESS(_('Модели импортированы'))
            )
        except Exception as error:
            self.stdout.write(
                self.style.WARNING(error)
            )
            self.stdout.write(
                self.style.ERROR(_('Не удалось выполнить импорт'))
            )
