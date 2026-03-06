import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction

from backend.settings import BASE_DIR
from recipes.models import Ingredient

CSV_DEFAULT_DIR = BASE_DIR.parent / 'data/'


class Command(BaseCommand):
    """Менеджмент команда для заполнения базы данных из CSV файлов."""
    help = 'Импорт данных из CSV файлов директории в базу даннных.'

    @property
    def files(self):
        files = {
            'ingredients.csv': self._fill_ingredients,
        }
        return files

    def add_arguments(self, parser):
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='Кодировка файла (по умолчанию utf-8).',
        )
        parser.add_argument(
            '--delimiter',
            type=str,
            default=',',
            help='Разделитель CSV (по умолчанию ",").'
        )

    def handle(self, *args, **options):
        dir = CSV_DEFAULT_DIR
        self.encoding = options['encoding']
        self.delimiter = options['delimiter']

        if not dir.exists() or not dir.is_dir():
            raise CommandError(f'Не является директорией: {dir}')

        with transaction.atomic():
            for file, func in self.files.items():
                func(dir / file)

        self.stdout.write(self.style.SUCCESS('Импорт данных завершен.'))

    def _read(self, path: Path) -> list:
        if not path.exists():
            self.stdout.write(
                self.style.WARNING(f'Отсутствует файл: {path.name}')
            )
            return []

        with path.open(encoding=self.encoding, newline='') as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            return list(reader)

    def _import_file(
        self,
        path: Path,
        model: models.Model,
        row_to_obj,
        label: str
    ):
        rows = self._read(path)
        if not rows:
            return self.stdout.write(
                self.style.WARNING(f'Импорт {path.name} пропущен.')
            )

        objects = []
        for i, row in enumerate(rows, start=1):
            try:
                objects.append(row_to_obj(row))
            except IndexError:
                raise CommandError(
                    f'{path.name}: Отсутствует значение (строка №{i})'
                )

        model.objects.bulk_create(objects)
        self.stdout.write(f'{label}: +{len(objects)} объектов.')

    def _fill_ingredients(self, path: Path):
        self._import_file(
            path=path,
            model=Ingredient,
            label='ingredients',
            row_to_obj=lambda row: Ingredient(
                name=row[0].strip(),
                measurement_unit=row[1].strip(),
            ),
        )
