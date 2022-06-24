import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from foodgram.models import Ingredient, Tag, User

ALREDY_LOADED_ERROR_MESSAGE = _(
    'База данных не пуста! '
    'Если вам нужно перезагрузить данные из CSV-файла, '
    'сначала удалите файл db.sqlite3. '
    'Затем запустите "python manage.py migrate" '
    'для создания новой пустой базы данных.'
)

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
                print(import_dict)
                if file == 'ingredients.csv':
                    ingredient, _ = model.objects.get_or_create(**import_dict)
                    # ingredient, _ = model.objects.get_or_create(
                    #     name=row[0],
                    #     measurement_unit=row[1]
                    # )
                if file == 'tags.csv':
                    tag, _ = model.objects.get_or_create(**import_dict)
                    # tag, _ = model.objects.get_or_create(
                    #     name=row[0],
                    #     color=row[1],
                    #     slug=row[2],
                    # )
                if file == 'users.csv':
                    raw_password = import_dict.pop('password')
                    user, created = model.objects.get_or_create(**import_dict)
                    if created:
                        user.set_password(raw_password)
                        user.save()


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
