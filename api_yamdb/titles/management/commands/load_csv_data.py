import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Comment, Review
from titles.models import Category, Genre, GenreTitle, Title
from users.models import User

DATA_PATH = f'{settings.BASE_DIR}/static/data'

MODELS_AND_CSV_FILES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    help = 'Load data from CSV files into the database'

    def handle(self, *args, **kwargs):
        for model, csv_file_name in MODELS_AND_CSV_FILES.items():
            with open(
                    file=f'{DATA_PATH}/{csv_file_name}',
                    mode='r',
                    encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                if csv_file_name == 'titles.csv':
                    data = [Title(
                        id=row['id'],
                        name=row['name'],
                        year=row['year'],
                        category=Category.objects.get(id=row['category'])
                    ) for row in reader]
                elif csv_file_name == 'review.csv':
                    data = [Review(
                        id=row['id'],
                        title=Title.objects.get(id=row['title_id']),
                        author=User.objects.get(id=row['author']),
                        text=row['text'],
                        score=row['score']
                    ) for row in reader]
                elif csv_file_name == 'comments.csv':
                    data = [Comment(
                        id=row['id'],
                        review=Review.objects.get(id=row['review_id']),
                        author=User.objects.get(id=row['author']),
                        text=row['text']
                    ) for row in reader]
                else:
                    data = [model(**row) for row in reader]
                model.objects.bulk_create(data)
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
