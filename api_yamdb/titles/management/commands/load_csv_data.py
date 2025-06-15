import csv
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

DATA_PATH = f'{settings.BASE_DIR}/static/data'


MODEL_FILES = {
    'User': 'users.csv',
    'Title': 'titles.csv',
    'GenreTitle': 'genre_title.csv',
    'Comment': 'comments.csv',
}


class Command(BaseCommand):
    help = 'Загрузка данных в БД из CSV файлов'

    def add_arguments(self, parser):
        """Определение аргументов для команды."""
        parser.add_argument(
            '--directory',
            type=str,
            default=DATA_PATH,
            help='Каталог с CSV файлами (по-умолчанию: {DATA_PATH})',
        )
        parser.add_argument(
            '--delimiter',
            type=str,
            default=',',
            help='CSV разделитель (по-умолчанию: ",")',
        )
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='Кодировка файла (по-умолчанию: utf-8)',
        )

    def handle(self, *args, **options):
        """Основная процедура."""
        self.directory = options['directory']
        self.delimiter = options['delimiter']
        self.encoding = options['encoding']
        self.success_count = 0
        self.error_count = 0

        if not self._validate_directory():
            return

        with transaction.atomic():
            self._process_all_models()

        self._print_final_summary()

    def _validate_directory(self):
        """Проверка наличия каталога с файлами загрузки."""
        if not os.path.exists(self.directory):
            self.stderr.write(self.style.ERROR(
                f"Каталог '{self.directory}' не найден",
            ))
            return False
        return True

    def _process_all_models(self):
        """Обработка всех моделей приложений."""
        for model in apps.get_models():
            model_name = model.__name__
            file_path = self._get_model_file_path(model_name)

            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(
                    f"Файл {file_path} для модели {model_name} не найден..."
                ))
                continue

            self._process_model_file(model, file_path)

    def _get_model_file_path(self, model_name):
        """Получить CSV файл для модели."""
        file_name = MODEL_FILES.get(model_name, f"{model_name}.csv")
        return os.path.join(self.directory, file_name)

    def _process_model_file(self, model, file_path):
        """Обработка файла CSV."""
        try:
            with open(file_path, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=self.delimiter)
                created_count = 0

                for row in reader:
                    if self._process_model_row(model, row):
                        created_count += 1

                if created_count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f"Создано {created_count} {model.__name__}"
                        f" объектов из {os.path.basename(file_path)}"
                    ))
                    self.success_count += 1

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Ошибка обработки {file_path} для {model.__name__}: {str(e)}",
            ))
            self.error_count += 1

    def _process_model_row(self, model, row):
        """Обработка одной строки из CSV файла."""
        try:
            model_data = self._prepare_model_data(model, row)
            obj, created = model.objects.get_or_create(**model_data)
            return created
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Ошибка создания {model.__name__} для строки {row}: {str(e)}"
            ))
            self.error_count += 1
            return False

    def _prepare_model_data(self, model, row):
        """Подготовка данных из CSV, получение внешних ключей."""
        model_data = row.copy()

        for field in model._meta.get_fields():
            field_name = field.name

            if field_name in model_data and field.many_to_one:
                model_data[field_name] = self._get_related_object(
                    field.related_model,
                    model_data[field_name],
                )
        return model_data

    def _get_related_object(self, related_model, related_id):
        """Получить связанный объект для поля foreign key."""
        try:
            return related_model.objects.get(pk=related_id)
        except related_model.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f"Связанный объект не найден: {related_model.__name__}"
                f" с id {related_id}"
            ))
            raise
        except ValueError:
            self.stderr.write(self.style.ERROR(
                f"Некорректный ID для {related_model.__name__}: {related_id}"
            ))
            raise

    def _print_final_summary(self):
        """Вывод итоговой информации о загрузке данных."""
        self.stdout.write(self.style.SUCCESS(
            f"\nЗагрузка данных завершена."
            f" Успешно: {self.success_count}, Ошибок: {self.error_count}"
        ))
