import sqlite3

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

data = (
    (f'{settings.CSV_DIRS}/users.csv', 'user'),
    (f'{settings.CSV_DIRS}/category.csv', 'category'),
    (f'{settings.CSV_DIRS}/genre.csv', 'genre'),
    (f'{settings.CSV_DIRS}/titles.csv', 'title'),
    (f'{settings.CSV_DIRS}/genre_title.csv', 'genre_title'),
    (f'{settings.CSV_DIRS}/review.csv', 'review'),
    (f'{settings.CSV_DIRS}/comments.csv', 'comment'),
)


class Command(BaseCommand):
    help = 'Импорт данных из файлов CSV'

    def handle(self, *args, **options):
        con = sqlite3.connect('db.sqlite3')

        for file, table in data:
            try:
                df = pd.read_csv(
                    file,
                    sep=',',
                    header=0,
                )
                df.rename(
                    columns={
                        'category': 'category_id',
                        'author': 'author_id',
                    },
                    inplace=True,
                )
                df.columns
                df.to_sql(
                    table,
                    con,
                    if_exists='append',
                    index=False
                )
                print(f'Данные из {file} успешно импортированы')
            except Exception as error:
                print(f'Ошибка загрузки - {error}')
        print('Работа команды import_csv завершена')
