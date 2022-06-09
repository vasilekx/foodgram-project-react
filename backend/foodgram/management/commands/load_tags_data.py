# foodgram/management/commands/load_tags_data.py

import csv
import os

from django.core.management import BaseCommand
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from foodgram.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = _(
    'База данных не пуста! '
    'Если вам нужно перезагрузить данные из CSV-файла, '
    'сначала удалите файл db.sqlite3. '
    'Затем запустите "python manage.py migrate" '
    'для создания новой пустой базы данных.'
)

data_files_list = [
    ['ingredients.csv', Ingredient],
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
            for row in reader:
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )


class Command(BaseCommand):
    help = _('Загрузка данных')

    def handle(self, *args, **options):
        # for lst in data_files_list:
        #     if lst[1].objects.exists():
        #         self.stdout.write(
        #             self.style.WARNING(ALREDY_LOADED_ERROR_MESSAGE)
        #         )
        #         return
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
